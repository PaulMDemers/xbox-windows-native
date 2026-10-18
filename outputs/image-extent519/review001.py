# SPDX-License-Identifier: MIT
"""Read-only original-artifact review; proposal stays only in host memory."""
import datetime,hashlib,importlib.util,json,re,shutil,struct,subprocess,sys,traceback
from pathlib import Path
import extent
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('C:/xwn516/build001');R=Path('C:/xwn519/review001');OUT=K/'review001.json'
assert not OUT.exists() and not R.exists()
assert shutil.disk_usage('C:/').free-8*1024**2>=20*1024**3
R.mkdir(parents=True)
sys.path.insert(0,str(K.parent/'data-layout515'));import elf32
sp=importlib.util.spec_from_file_location('xbe_structure519',K.parent/'loader-comparison509/inspect.py');xm=importlib.util.module_from_spec(sp);sp.loader.exec_module(xm)
sha=lambda b:hashlib.sha256(b).hexdigest();pins={}

def load(p):
    p=Path(p);b=p.read_bytes();pins[str(p.resolve())]=dict(bytes=len(b),sha256=sha(b));return b

def js(p):return json.loads(load(p))
def mapped(n):return Path(n.replace('/mnt/c/','C:/',1))
def save(p,r):p.write_bytes((json.dumps(r,indent=2)+'\n').encode())

result=dict(passed=False,started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),physical_access=False,build=False,new_XBE_saved=False,runtime_executed=False)
try:
    for p in [K/'review001.py',K/'extent.py',K/'DESIGN.md',K/'.gitattributes',K.parent/'data-layout515/elf32.py',K.parent/'loader-comparison509/inspect.py']:load(p)
    build=js(K.parent/'entry-colocated516/build001.json');review=js(K.parent/'entry-colocated516/review001.json')
    assert build['status']=='compiled' and review['passed']
    for n,row in build['files'].items():assert sha(load(mapped(n)))==row['sha256']
    for n,row in review['private_files'].items():assert sha(load(mapped(n)))==row['sha256']
    actual=load(P/'default.xbe');extent.original(actual)
    o=elf32.parse(load(P/'xbeboot.o'));e=elf32.parse(load(P/'wrapper.elf'))
    t=o['named']['.text'];d=o['named']['.data'];sections,ledger=elf32.relocated(o,{t:extent.BASE,d:0x94c20})
    assert len(ledger)==395
    for n,i in [('.text',t),('.data',d)]:assert sections[i]==e['data'](e['sections'][e['named'][n]])
    assert e['sections'][e['named']['.text']][3:4]==(extent.BASE,)
    assert len(sections[t])==0x94c18-extent.BASE and len(sections[d])==320
    assert e['sections'][e['named']['.data']][3]==0x94c20
    sy={s['name']:s['value'] for s in e['symbols'] if s['name']}
    assert sy['_end']==sy['_edata']==sy['__bss_start']==extent.END
    assert '.bss' not in e['named'] or e['sections'][e['named']['.bss']][5]==0
    raw=load(P/'wrapper.bin');assert raw==sections[t]+bytes(8)+sections[d] and len(raw)==extent.SIZE
    joined=bytearray(raw);joined[:4096]=actual[:4096];joined[0x3000:0x84000]=actual[0x3000:0x84000]
    assert joined==actual[:extent.SIZE]
    assert not any(actual[extent.SIZE:0x85000]) and len(actual[0x85000:])==320
    tail=actual[extent.SIZE:];assert len(tail)==992
    tail_refs=[r for r in ledger if r['kind']==1 and extent.END<=r['value']<extent.BASE+len(actual)]
    assert tail_refs==[]
    data_refs=[r for r in ledger if r['symbol_section']==d]
    assert len(data_refs)==74 and all(r['kind']==1 and 0x94c20<=r['value']<extent.END for r in data_refs)
    assert sum(r['section']==t for r in data_refs)==72
    assert all(r['section'] in (t,d) for r in ledger)
    # Independent actual disassembly, joined byte-for-byte to the retained XBE.
    text=subprocess.check_output(['wsl','-d','Ubuntu','--','objdump','-dw','-Mintel','--start-address=0x94877','--stop-address=0x94c18','/mnt/c/xwn516/build001/wrapper.elf'],text=True,timeout=20)
    (R/'diagnostic.txt').write_bytes(text.encode())
    instructions={}
    for line in text.splitlines():
        m=re.match(r'\s*([0-9a-f]+):\s+((?:[0-9a-f]{2} )+)\s*([a-z][a-z0-9]*)\s*(.*)',line)
        if m:instructions[int(m[1],16)]=(bytes.fromhex(m[2]),m[3],m[4])
    at=0x94877;direct=[];indirect=[];memory=[]
    allowed_slots={0x94d0c,0x1100c,0x11010,0x11014,0x11018,0x1101c,0x11020,0x11024}
    for address,(b,mn,op) in sorted(instructions.items()):
        assert address==at and b==actual[address-extent.BASE:address-extent.BASE+len(b)];at+=len(b)
        for found in re.findall(r'ds:0x([0-9a-f]+)',op):
            a=int(found,16);assert (0x94c20<=a and a+4<=extent.END) or a in allowed_slots
            memory.append(dict(instruction=address,address=a,bytes=4))
        if mn.startswith('j') or mn.startswith('loop') or mn=='call':
            if op.startswith('DWORD PTR ds:'):
                slot=int(op.split(':')[1],16);assert slot in allowed_slots
                indirect.append(dict(instruction=address,slot=slot))
            else:
                target=int(op.split()[0],16);assert target in instructions
                direct.append(dict(instruction=address,target=target))
    assert at==0x94c18 and len(direct)==49 and len(indirect)==8
    assert set(v['slot'] for v in indirect)==allowed_slots
    assert struct.unpack_from('<I',actual,0x94d0c-extent.BASE)[0]==sy['entry503_failed_file']==0x94bac
    assert actual[0x1100:0x1105]==b'\xe9'+struct.pack('<i',sy['entry503_gate']-0x11105)
    buffers=[('record_write_and_hash',sy['entry498_record'],96),('trailer_write',sy['entry498_trailer'],16),('iosb',sy['entry498_iosb'],8),('object_attributes',sy['entry498_object'],12),('name',sy['entry498_name'],8),('path_with_terminator',sy['entry498_path'],sy['entry498_path_end']-sy['entry498_path']+1),('saved_entry_registers',sy['entry498_record']+20,32),('saved_post_file_registers',sy['entry503_restored'],36),('delay_interval',sy['entry503_interval'],8)]
    assert all(0x94c20<=a and a+n<=extent.END for _,a,n in buffers)
    obj=struct.unpack_from('<III',actual,sy['entry498_object']-extent.BASE);assert obj==(0,sy['entry498_name'],0x40)
    size,maximum,path=struct.unpack_from('<HHI',actual,sy['entry498_name']-extent.BASE)
    assert path==sy['entry498_path'] and maximum==size+1 and path+maximum<=extent.END
    assert actual[path-extent.BASE:path-extent.BASE+maximum]==b'\\Device\\Harddisk0\\Partition1\\Applications\\XWNBoot516a\\entry.bin\0'
    # Cold joins are historical readback, not another physical observation.
    joins={};images={}
    for case,folder,remote,built in [('494','d3d-transform494','/E/Applications/XWNBoot494a/default.xbe','C:/xwn494/build002/default.xbe'),('518','entry-physical518','/E/Applications/XWNBoot516a/default.xbe',str(P/'default.xbe'))]:
        s=js(K.parent/folder/'physical001-stage.json');c=js(K.parent/folder/'physical001-collection.json');row=c['files'][remote]
        b=load(built);assert b==load(row['path']) and sha(b)==row['sha256']==s['staged'][remote]['sha256']
        joins[case]=dict(build=built,cold=row['path'],sha256=sha(b));images[case]=xm.inspect(b)
    for n in ['entry-physical518/physical-final001.json','entry-physical518/final-review.json','entry-observer517/data-placement-review001.json','entry-observer517/actual-review001.json','entry-observer517/final-review.json']:js(K.parent/n)
    q=extent.propose(actual);assert extent.validate(q,actual);prop=xm.inspect(q)
    assert prop['rounded_image_end']==images['494']['rounded_image_end']==0x95000 and images['518']['rounded_image_end']==0x96000
    assert prop['entry']==images['518']['entry']==0x11100
    for field in ['imports','certificate_sha256','tls_bytes_sha256','tls_words','tls_address']:
        assert prop[field]==images['518'][field]
    assert not prop['tls_generic_in_image_range_check'] and not images['494']['tls_generic_in_image_range_check']
    assert q[4096:]==actual[4096:extent.SIZE] and q[0x3000:0x84000]==actual[0x3000:0x84000]
    changed=[i for i,(a,b) in enumerate(zip(q,actual)) if a!=b]
    permitted={i for off in extent.FIELDS for i in range(off,off+4)}|set(range(0x36c,0x380))
    assert set(changed)<=permitted
    # Repair digest after mutation: live-byte checks must reject independently.
    negatives=[]
    positions=sorted(set(range(4096))|set(range(0x94877-extent.BASE,extent.SIZE))|set(range(4096,extent.SIZE,4096))|{0x1100,0x1104,0x3000,0x83fff})
    for off in positions:
        bad=bytearray(q);bad[off]^=1
        if not 0x36c<=off<0x380:bad[extent.DIGEST]=extent.digest(bad)
        try:extent.validate(bytes(bad),actual)
        except ValueError:negatives.append(off)
        else:raise AssertionError(('mutation accepted',off))
    invalid_sizes=[0,4096,extent.SIZE-1,extent.SIZE+1,len(actual),0x85000]
    for n in invalid_sizes:
        bad=q[:n]+bytes(max(0,n-len(q)))
        try:extent.validate(bad,actual)
        except ValueError:pass
        else:raise AssertionError(('invalid size accepted',n))
    save(R/'closure.json',dict(relocations=ledger,direct_edges=direct,indirect_edges=indirect,absolute_memory_operands=memory,bounded_buffers=buffers,tail_references=tail_refs,scope='known static entry-only instructions/data; external kernel/caller stack/TLS runtime remain separate'))
    result.update(passed=True,actual_parent_sha256=sha(actual),actual_parent_bytes=len(actual),proposed_bytes=len(q),proposed_sha256=sha(q),proposed_metadata=prop,removed_bytes=len(tail),removed_sha256=sha(tail),removed_zero_padding=672,removed_old_data=320,relocations_reconstructed=len(ledger),data_references=len(data_refs),direct_edges=len(direct),indirect_edges=len(indirect),absolute_memory_operands=len(memory),bounded_buffers=buffers,physical_cold_joins=joins,actual_images=images,header_changed_offsets=changed,negative_byte_mutations=len(negatives),invalid_lengths_rejected=invalid_sizes,live_prefix_exact=True,payload_exact=True,known_entry_tail_references=[],inherited_TLS_runtime_unknown=True,physical_root_cause_established=False,queued_launch=False)
except Exception:result['failure']=traceback.format_exc()
finally:
    result.update(finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),inputs=pins,private_files={str(p):dict(bytes=p.stat().st_size,sha256=sha(p.read_bytes())) for p in R.iterdir() if p.is_file()})
    save(OUT,result)
    print(json.dumps({n:result[n] for n in ['passed','failure','removed_bytes','proposed_bytes','negative_byte_mutations'] if n in result}))
if not result['passed']:raise SystemExit(1)
