"""Replay crash003 raw pins, paired shutdown and cold evidence without waivers."""
import hashlib,json,struct,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];out=k/'crash003';run=ws/'work/runs/nt5-nvnet-controlled-dump-crash003'
sys.path.insert(0,str(ws/'work/python-packages'));import pefile
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pre=read(out/'preflight.json');t=read(out/'trace.json');a=read(out/'audit.json');c=read(out/'closure.json');mods=read(out/'source/modules.json')
for n,h in pre['sources'].items():assert sha(out/'source'/n)==h
assert sha(out/'source/trace.py')==t['source_sha256']
for n,h in t['dependencies'].items():assert sha(ws/n)==h
assert sha(run/'hdd.qcow2')==c['private_disk_sha256']==a['crash_disk_sha256']
for n,h in c['metadata_sha256'].items():assert sha(run/n)==h
for v in t['runtime_pins']:
    m=mods[v['module']];p=Path(m['path']);assert sha(p)==v['source_sha256']==m['sha256'];pe=pefile.PE(str(p));rva=int(v['rva'],16);base=int(v['base'],16)
    assert int(v['address'],16)==base+rva;raw=pe.get_data(rva,len(bytes.fromhex(v['raw'])));assert raw.hex()==v['raw'];b=bytearray(raw)
    rel=[e.rva-rva for block in pe.DIRECTORY_ENTRY_BASERELOC for e in block.entries if e.type==3 and rva<=e.rva<rva+len(b)];assert rel==v['relocations']
    for off in rel:struct.pack_into('<I',b,off,(struct.unpack_from('<I',b,off)[0]+base-pe.OPTIONAL_HEADER.ImageBase)&0xffffffff)
    assert b.hex()==v['resident']
assert t['guest_resumed'] and not t['armed_breakpoints_remaining']
events=t['events'];assert events[0]['kind']=='bugcheck_entry' and events[0]['arguments']==['0xe058d103','0x44554d50','0x103','0x10000','0x1']
by={v['kind']:v for v in events};callback_complete=all(n in by for n in ['nvnet_shutdown_entry','nvnet_idle_entry','nvnet_shutdown_return','callbacks_return'])
if callback_complete:
    en,ex=by['nvnet_shutdown_entry'],by['nvnet_shutdown_return'];assert en['thread']==ex['thread'] and int(ex['registers']['ESP'],16)==int(en['registers']['ESP'],16)+8
    assert en['index']<by['nvnet_idle_entry']['index']<ex['index']<by['callbacks_return']['index']
if 'dump_return' in by:
    en,ex=by['dump_entry'],by['dump_return'];assert en['thread']==ex['thread'] and int(ex['registers']['ESP'],16)==int(en['registers']['ESP'],16)+28
    assert ex['returned_boolean']==(int(ex['eax'],16)&255)
assert sha(out/'allocation.json')==a['allocation_sha256']
for v in a['hives']:assert sha(out/'artifacts'/('after-'+v['name']))==v['sha256']
for v in a['pagefiles']:
    p=out/'artifacts'/(v['phase']+'-pagefile-prefix.bin');data=p.read_bytes();assert sha(p)==v['prefix_sha256'] and data[:8].hex()==v['header8'] and [hex(x) for x in struct.unpack_from('<5I',data,0x28)]==v['bugcheck_fields']
assert a['alias_unchanged']==((out/'artifacts/before-alias.bin').read_bytes()==(out/'artifacts/after-alias.bin').read_bytes())
before,after=[read(out/(phase+'-pagefile-map.json')) for phase in ['before','after']]
assert before['requested_65536']==after['requested_65536']==[dict(byte_length=65536,volume_byte_offset=140436013056),dict(byte_length=0,volume_byte_offset=0)]
assert before['clusters']==after['clusters'] and len(before['clusters'])==1536
assert a['pagefile_disk_offset']==before['partition_offset']+140436013056>1<<37
success=callback_complete and a['dump_write_evidence_passed'] and a['integrity_passed']
r=dict(evidence_consistent=True,intended_crash_confirmed=True,network_shutdown_returned=callback_complete,dump_write_qualified=success,recovery_qualified=False,ordinary_qualified=False,physical_access=False,trace_status=t['status'],events=len(events),pins=len(t['runtime_pins']),trace_sha256=sha(out/'trace.json'),audit_sha256=sha(out/'audit.json'),crash_disk_sha256=c['private_disk_sha256'],limits='Runtime pins and cold dump header/high-LBA evidence. Separate recovery boot and complete dump-format validation still required.')
(k/'verification.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
