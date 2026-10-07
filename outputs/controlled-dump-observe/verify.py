"""Replay failed capture and cold crash evidence without converting failure to PASS."""
import hashlib,json,struct,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];out=k/'crash002';run=ws/'work/runs/nt5-controlled-dump-observe-crash002'
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

assert t['status']=='dump_capture_timeout' and t['guest_resumed'] and not t['armed_breakpoints_remaining']
assert [v['kind'] for v in t['events']]==['bugcheck_entry','stop_line_call','message_call','message_return','callbacks_call'] and len(t['runtime_pins'])==8
assert t['events'][0]['arguments']==['0xe058d103','0x44554d50','0x103','0x10000','0x1']
assert a['intent_exact'] and a['integrity_passed'] and not a['dump_write_evidence_passed'] and not a['dump_header_matches']
s=read(out/'timeout-snapshot.json');q=read(out/'timeout-analysis.json');ramfile=out/'artifacts/timeout-ram.bin';assert sha(ramfile)==s['ram_sha256']==q['ram_sha256'];ram=ramfile.read_bytes()
assert s['captured'] and s['resumed'] and s['preceding_trace_sha256']==sha(out/'trace.json') and q['snapshot_sha256']==sha(out/'timeout-snapshot.json')
assert q['bugcheck_data']==['0xd1','0xf8d17800','0x1f','0x0','0xf8d17800'] and q['halted']
cr3=int(q['cr3'],16);va=int(q['cr2'],16);pde=struct.unpack_from('<I',ram,(cr3&~4095)+(va>>22)*4)[0];pte=struct.unpack_from('<I',ram,(pde&~4095)+((va>>12)&1023)*4)[0]
assert q['fault_mapping']['pde']==hex(pde) and q['fault_mapping']['pte']==hex(pte) and not pte&1 and not q['fault_mapping']['present']
def memory(a,n):
    b=b''
    while n:
        d=struct.unpack_from('<I',ram,(cr3&~4095)+(a>>22)*4)[0];assert d&1
        if d&128:physical=(d&0xffc00000)+(a&0x3fffff)
        else:
            e=struct.unpack_from('<I',ram,(d&~4095)+((a>>12)&1023)*4)[0];assert e&1;physical=(e&~4095)+(a&4095)
        take=min(n,4096-(a&4095));b+=ram[physical:physical+take];a+=take;n-=take
    return b
syms=read(k.parent/'native-windows-nt5-kernel/kernel-publics.json')['symbols'];assert [hex(v) for v in struct.unpack('<5I',memory(0x823df000+syms['_KiBugCheckData']['rva'],20))]==q['bugcheck_data']
cb=q['active_callback'];assert cb['state']==2 and cb['checksum_valid'] and memory(int(cb['address'],16),32).hex()==cb['raw']
assert memory(int(cb['buffer'],16),cb['length']).hex()==q['callback_buffer']
assert struct.unpack_from('<2I',bytes.fromhex(q['callback_buffer']))==(int(q['adapter'],16),int(q['miniport_handler'],16))
for v in q['pins']:
    name=v['module'].lower();p=out/'artifacts'/('after-'+name);assert sha(p)==v['sha256'];pe=pefile.PE(str(p));rva=int(v['rva'],16);base=int(v['base'],16);raw=pe.get_data(rva,len(bytes.fromhex(v['raw'])));assert raw.hex()==v['raw'];b=bytearray(raw)
    rel=[e.rva-rva for block in pe.DIRECTORY_ENTRY_BASERELOC for e in block.entries if e.type==3 and rva<=e.rva<rva+len(b)];assert rel==v['relocations']
    for off in rel:struct.pack_into('<I',b,off,(struct.unpack_from('<I',b,off)[0]+base-pe.OPTIONAL_HEADER.ImageBase)&0xffffffff)
    assert b==memory(int(v['address'],16),len(b)) and b.hex()==v['resident']
cb_review=read(k/'callback-review.json');assert cb_review['driver_sha256']==sha(out/'artifacts/after-nvnetnt5.sys')
assert cb_review['symbols']['_NvNetIdleTransmitter']['rva']==q['fault_module']['rva']=='0x7800' and q['fault_section']=='PAGE'
assert cb_review['symbols']['_MiniportShutdown@4']['rva']==q['handler_module']['rva']=='0x21f0'
for n in ['ndis.sys','nvnetnt5.sys']:assert (out/'artifacts'/('before-'+n)).read_bytes()==(out/'artifacts'/('after-'+n)).read_bytes()
assert sha(out/'allocation.json')==a['allocation_sha256']
for v in a['hives']:assert sha(out/'artifacts'/('after-'+v['name']))==v['sha256']
for v in a['pagefiles']:assert sha(out/'artifacts'/(v['phase']+'-pagefile-prefix.bin'))==v['prefix_sha256']
assert (out/'artifacts/before-alias.bin').read_bytes()==(out/'artifacts/after-alias.bin').read_bytes()
r=dict(evidence_consistent=True,bounded_trace_timeout_retained=True,intended_crash_confirmed=True,nested_bugcheck=q['bugcheck_data'],active_callback='NDIS miniport shutdown',fault_function='nvnetnt5!NvNetIdleTransmitter',fault_rva='0x7800',fault_page_present=False,fault_section='PAGE',integrity_passed=True,dump_write_qualified=False,recovery_qualified=False,physical_access=False,trace_sha256=sha(out/'trace.json'),audit_sha256=sha(out/'audit.json'),snapshot_sha256=sha(out/'timeout-snapshot.json'),analysis_sha256=sha(out/'timeout-analysis.json'))
(k/'verification.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
