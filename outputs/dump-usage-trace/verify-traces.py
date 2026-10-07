"""Replay frozen module bytes, dispatch pairing and pre-free completion evidence."""
import hashlib,json,struct,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sys.path.insert(0,str(ws/'work/python-packages'));import pefile
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
results=[]
for case in ['dispatch001','dispatch002']:
    out=k/case;t=read(out/'trace.json');pre=read(out/'preflight.json');a=read(out/'audit.json')
    for name,digest in pre['sources'].items():assert sha(out/'source'/name)==digest
    assert sha(out/'source/trace.py')==t['source_sha256']
    for name,digest in t['input_sha256'].items():assert sha(out/'source'/name)==digest
    modulefile=next(n for n in t['input_sha256'] if n.startswith('modules'))
    mods=read(out/'source'/modulefile);pes={}
    for name,m in mods.items():
        assert sha(Path(m['path']))==m['sha256'];pes[name]=pefile.PE(m['path'])
    for pin in t['runtime_pins']:
        m=mods[pin['module']];p=pes[pin['module']];rva=int(pin['rva'],16);base=int(pin['base'],16)
        assert pin['source_sha256']==m['sha256'] and int(pin['address'],16)==base+rva
        # Loaded modules reserve whole 4 KiB pages; old PE SizeOfImage can be unrounded.
        assert any(v['base']==base and v['name'].lower()==pin['module'] and v['size']==((m['image_size']+4095)&~4095) for v in t['module_list'])
        raw=p.get_data(rva,len(bytes.fromhex(pin['raw'])));assert raw.hex()==pin['raw']
        data=bytearray(raw)
        rel=[e.rva-rva for b in p.DIRECTORY_ENTRY_BASERELOC for e in b.entries if e.type==3 and rva<=e.rva<rva+len(data)]
        assert rel==pin['relocations']
        for off in rel:struct.pack_into('<I',data,off,(struct.unpack_from('<I',data,off)[0]+base-p.OPTIONAL_HEADER.ImageBase)&0xffffffff)
        assert data.hex()==pin['resident']
    assert t['guest_resumed'] and not t['armed_breakpoints_remaining']
    assert a['debugger'] and not a['ordinary_qualified'] and not a['strict_qualification_passed']
    assert a['workload_and_persistence_passed'] and a['integrity_passed']
    assert [(e['source'],e['event_id']) for e in a['warnings_errors']]==[('Ftdisk',49)]
    if case=='dispatch001':
        assert t['status']=='capture_incomplete' and 'Unpinned module' in t['error'] and 'diskperf.sys' in t['error']
        assert t['unreturned_dispatches']==4
        results.append(dict(case=case,diagnostic_passed=False,preserved_failure=t['error'],resident_pins=len(t['runtime_pins'])));continue
    assert t['status']=='usage_return_captured' and t['unreturned_dispatches']==0
    events=t['events'];assert [e['index'] for e in events]==list(range(len(events)))
    assert events[0]['kind']=='usage_call' and events[-1]['kind']=='usage_return' and events[-1]['status']=='0xc00000bb'
    assert events[0]['thread']==events[-1]['thread'] and events[0]['registers']['EBP']==events[-1]['registers']['EBP']
    dispatch=[e for e in events if e['kind']=='dispatch']
    assert [e['device']['name'] for e in dispatch]==['\\FileSystem\\XwnFatx','\\Driver\\Ftdisk','\\Driver\\Disk','\\Driver\\Diskperf','\\Driver\\PartMgr','\\Driver\\Disk','\\Driver\\atapi','\\Driver\\atapi','\\Driver\\PCIIde','\\Driver\\PCIIde','\\Driver\\PCI','\\Driver\\PCI','\\Driver\\PCI_HAL']
    assert len(t['calls'])==13 and len(t['tracked_irps'])==4
    for call in t['calls']:
        entry=next(e for e in dispatch if e['call_index']==call['index'])
        ret=next(e for e in events if e['kind']=='dispatch_return' and e['call_index']==call['index'])
        assert entry['index']<ret['index'] and call['returned']
        assert entry['thread']==ret['thread']==call['thread']
        assert int(ret['registers']['ESP'],16)==int(call['entry_stack'],16)+4
        assert ret['registers']['EIP']==call['return_address'] and ret['status']==call['status']
        sl=bytes.fromhex(entry['stack_location']);assert sl[:2]==b'\x1b\x16' and sl[4]==1 and struct.unpack_from('<I',sl,8)[0]==3
        assert entry['request']['irp']==call['irp'] and entry['request']['io_status']=='0xc00000bb'
    for irp in t['tracked_irps']:
        matching=[e for e in events if e.get('request',{}).get('irp')==irp['irp']]
        assert irp['freed'] and matching[-1]['kind']=='free'
        assert sum(e['kind']=='free' for e in matching)==1
        assert all(e['request']['io_status']=='0xc00000bb' for e in matching)
    first=next(e for e in events if e['kind']=='complete');pin=t['runtime_pins'][first['caller_pin']]
    assert pin['module']=='hal.dll' and pin['rva']=='0x83d8' and first['request']['irp']==dispatch[-1]['request']['irp']
    assert [c['status'] for c in t['calls'][:2]]==['0x103','0x103']
    results.append(dict(case=case,diagnostic_passed=True,events=len(events),dispatch_pairs=len(t['calls']),tracked_irps=len(t['tracked_irps']),resident_pins=len(t['runtime_pins']),first_completion_module=pin['module'],first_completion_rva=pin['rva'],final_status=events[-1]['status'],strict_qualification_passed=False))
result=dict(scope=__doc__,results=results);path=k/'trace-verification.json'
if path.exists():assert read(path)==result
else:path.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(results,indent=2))
