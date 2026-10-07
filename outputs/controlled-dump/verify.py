"""Replay failed capture and cold crash evidence without converting failure to PASS."""
import hashlib,json,struct,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];out=k/'crash001';run=ws/'work/runs/nt5-controlled-dump-crash001'
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
assert t['status']=='capture_incomplete' and t['error']=="AssertionError('E14')"
assert len(t['events'])==1 and len(t['runtime_pins'])==2 and t['guest_resumed'] and not t['armed_breakpoints_remaining']
assert t['events'][0]['arguments']==['0xe058d103','0x44554d50','0x103','0x10000','0x1']
assert t['runtime_pins'][t['events'][0]['caller_pin']]['module']=='trigger.sys'
assert a['intent_exact'] and a['integrity_passed'] and not a['dump_write_evidence_passed'] and not a['dump_header_matches']
for v in a['pagefiles']:assert sha(out/'artifacts'/(v['phase']+'-pagefile-prefix.bin'))==v['prefix_sha256']
assert (out/'artifacts/before-alias.bin').read_bytes()==(out/'artifacts/after-alias.bin').read_bytes()
assert sha(out/'allocation.json')==a['allocation_sha256']
for v in a['hives']:assert sha(out/'artifacts'/('after-'+v['name']))==v['sha256']
assert sha(run/'cpu-trace.log')==a['disk_trace_sha256']
r=dict(failed_evidence_consistent=True,capture_passed=False,dump_write_qualified=False,recovery_qualified=False,physical_access=False,intended_crash_confirmed=True,failure=t['error'],integrity_passed=True,trace_sha256=sha(out/'trace.json'),audit_sha256=sha(out/'audit.json'))
(k/'verification.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
