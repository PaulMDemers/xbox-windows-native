"""Replay successful runtime extents, retained dump context and independent cold map."""
import hashlib,json,struct,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];out=k/'trace001'
sys.path.insert(0,str(ws/'work/python-packages'));import pefile
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
t=read(out/'trace.json');pre=read(out/'preflight.json');a=read(out/'audit.json')
for n,d in pre['sources'].items():assert sha(out/'source'/n)==d
assert sha(out/'source/trace.py')==t['source_sha256']
for n,d in t['input_sha256'].items():assert sha(out/'source'/n)==d
mods=read(out/'source/modules.json');pes={}
for n,m in mods.items():assert sha(Path(m['path']))==m['sha256'];pes[n]=pefile.PE(m['path'])
for pin in t['runtime_pins']:
    m=mods[pin['module']];p=pes[pin['module']];rva=int(pin['rva'],16);base=int(pin['base'],16)
    assert pin['source_sha256']==m['sha256'] and int(pin['address'],16)==base+rva
    assert any(v['base']==base and v['name'].lower()==pin['module'] and v['size']==((m['image_size']+4095)&~4095) for v in t['module_list'])
    raw=p.get_data(rva,len(bytes.fromhex(pin['raw'])));assert raw.hex()==pin['raw'];data=bytearray(raw)
    rel=[e.rva-rva for b in p.DIRECTORY_ENTRY_BASERELOC for e in b.entries if e.type==3 and rva<=e.rva<rva+len(data)];assert rel==pin['relocations']
    for off in rel:struct.pack_into('<I',data,off,(struct.unpack_from('<I',data,off)[0]+base-p.OPTIONAL_HEADER.ImageBase)&0xffffffff)
    assert data.hex()==pin['resident']
assert t['status']=='initialization_success_captured' and t['guest_resumed'] and not t['armed_breakpoints_remaining']
assert not t['pending_calls'] and not t['unreturned_fatx_calls']
ev=t['events'];assert [v['index'] for v in ev]==list(range(len(ev)))
assert [v['kind'] for v in ev]==['configure_entry','configure_handle_return','stack_entry','stack_usage_call','stack_usage_return','stack_final_return','dump_stack_return','complete_call','entry','handle_return','query_call','query_return','fsctl_call','fatx_entry','fatx_return','fsctl_return','return','caller_status']
by={v['kind']:v for v in ev};assert len(t['calls'])==len(t['fatx_calls'])==1
for v in ev:assert t['runtime_pins'][v['resident_pin']]['address']==v['registers']['EIP']
for n in ['configure_handle_return','stack_usage_return','stack_final_return','dump_stack_return','handle_return','query_return','fatx_return','fsctl_return','return','caller_status']:assert by[n]['status']=='0x0'
usage=bytes.fromhex(by['stack_usage_call']['usage_stack']['bytes']);assert usage[:2]==b'\x1b\x16' and usage[4]==1 and struct.unpack_from('<I',usage,8)[0]==3
call=t['calls'][0];ret=by['return'];caller=by['caller_status'];assert call['completed'] and call['status']=='0x0'
assert ret['thread']==caller['thread']==call['thread'] and ret['registers']['ESP']==call['stack']
assert caller['registers']['EIP']==call['return_address'] and int(caller['registers']['ESP'],16)==int(call['stack'],16)+8
fs=by['fsctl_call'];fe=by['fatx_entry'];fr=by['fatx_return'];args=[int(v,16) for v in fs['arguments']]
assert args[5]==0x9003b and args[7]==8 and args[9]==4
assert fs['input']['address']==hex(args[6]) and fs['input']['length']==8 and bytes.fromhex(fs['input']['bytes'])==struct.pack('<Q',65536)
sl=bytes.fromhex(fe['stack_location']);assert sl[:2]==b'\x0d\0' and struct.unpack_from('<4I',sl,4)==(4,8,0x9003b,args[6])
assert fe['input']==fs['input'] and fe['requestor_mode']==0 and fe['user_buffer']==hex(args[8])
fc=t['fatx_calls'][0];assert fc['returned'] and fc['status']=='0x0' and fe['thread']==fr['thread']==fc['thread']
assert int(fr['registers']['ESP'],16)==int(fc['stack'],16)+4 and fr['registers']['EIP']==fc['return_address']
assert t['runtime_pins'][fe['resident_pin']]['module']=='xwnfatx.sys'
assert struct.unpack('<2I',bytes.fromhex(by['fsctl_return']['iosb']['bytes']))==(0,4)
mp=t['returned_mapping'];assert mp==by['fsctl_return']['returned_mapping'] and mp['requested_bytes']==mp['total_bytes']==65536
assert int.from_bytes(bytes.fromhex(by['fsctl_return']['output_after']['bytes']),'little')==int(mp['pointer'],16)
assert mp['raw']==b''.join(struct.pack('<QQ',v['byte_length'],v['volume_byte_offset']) for v in mp['pairs']).hex()
oracle=read(out/'source/cold-oracle.json');before=read(out/'before-pagefile-map.json');after=read(out/'after-pagefile-map.json')
assert oracle==before
for n in ['file_size','clusters','cluster_size','partition_offset','partition_size','requested_65536','whole_file']:assert before[n]==after[n]
assert mp['pairs']==before['requested_65536'] and len(mp['pairs'])==2 and mp['pairs'][-1]==dict(byte_length=0,volume_byte_offset=0)
assert mp['pairs'][0]==dict(byte_length=65536,volume_byte_offset=140436013056)
ctx=caller['retained_dump_context'];raw=bytes.fromhex(ctx['raw'])
assert ctx['mapping_pointer']==mp['pointer'] and ctx['mapping_bytes']==24 and ctx['requested_bytes']==65536
assert struct.unpack_from('<II',raw,0x14)==(int(mp['pointer'],16),24) and struct.unpack_from('<Q',raw,0x58)[0]==65536
assert [t['runtime_pins'][i]['rva'] for i in caller['consumer_pins']]==['0x22f71','0x22f8b','0x22fa4']
assert a['debugger'] and not a['ordinary_qualified'] and a['strict_qualification_passed'] and a['workload_and_persistence_passed'] and a['integrity_passed'] and not a['warnings_errors']
r=dict(scope=__doc__,trace_sha256=sha(out/'trace.json'),audit_sha256=sha(out/'audit.json'),cold_oracle_sha256=sha(out/'source/cold-oracle.json'),diagnostic_passed=True,events=len(ev),resident_pins=len(t['runtime_pins']),usage_status='0x0',fsctl='0x9003b',fatx_and_caller_status='0x0',runtime_extent=mp['pairs'][0],retained_mapping_bytes=24,strict_diagnostic_audit_passed=True,ordinary_qualified=False,physical_access=False,actual_crash_dump_write_qualified=False)
p=k/'trace-verification.json'
if p.exists():assert read(p)==r
else:p.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r,indent=2))
