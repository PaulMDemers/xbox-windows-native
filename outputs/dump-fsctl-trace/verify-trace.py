"""Replay frozen resident pins and the actual kernel/FATX FSCTL boundary."""
import hashlib,json,struct,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];out=k/'trace001'
sys.path.insert(0,str(ws/'work/python-packages'));import pefile
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
t=read(out/'trace.json');pre=read(out/'preflight.json');a=read(out/'audit.json')
for name,digest in pre['sources'].items():assert sha(out/'source'/name)==digest
assert sha(out/'source/trace.py')==t['source_sha256']
for name,digest in t['input_sha256'].items():assert sha(out/'source'/name)==digest
mods=read(out/'source/modules.json');pes={}
for name,m in mods.items():
    assert sha(Path(m['path']))==m['sha256'];pes[name]=pefile.PE(m['path'])
for pin in t['runtime_pins']:
    m=mods[pin['module']];p=pes[pin['module']];rva=int(pin['rva'],16);base=int(pin['base'],16)
    assert pin['source_sha256']==m['sha256'] and int(pin['address'],16)==base+rva
    assert any(v['base']==base and v['name'].lower()==pin['module'] and v['size']==((m['image_size']+4095)&~4095) for v in t['module_list'])
    raw=p.get_data(rva,len(bytes.fromhex(pin['raw'])));assert raw.hex()==pin['raw'];data=bytearray(raw)
    rel=[e.rva-rva for b in p.DIRECTORY_ENTRY_BASERELOC for e in b.entries if e.type==3 and rva<=e.rva<rva+len(data)]
    assert rel==pin['relocations']
    for off in rel:struct.pack_into('<I',data,off,(struct.unpack_from('<I',data,off)[0]+base-p.OPTIONAL_HEADER.ImageBase)&0xffffffff)
    assert data.hex()==pin['resident']
assert t['status']=='failure_path_captured' and t['guest_resumed'] and not t['armed_breakpoints_remaining']
assert not t['pending_calls'] and not t['unreturned_fatx_calls']
ev=t['events'];assert [v['index'] for v in ev]==list(range(len(ev)))
assert len({v['kind'] for v in ev})==len(ev);by={v['kind']:v for v in ev}
assert [v['kind'] for v in ev]==['configure_entry','configure_handle_return','stack_entry','stack_usage_call','stack_usage_return','stack_final_return','dump_stack_return','complete_call','entry','handle_return','query_call','query_return','fsctl_call','fatx_entry','fatx_return','fsctl_return','return','caller_status','caller_error']
assert len(t['calls'])==len(t['fatx_calls'])==1
for v in ev:assert t['runtime_pins'][v['resident_pin']]['address']==v['registers']['EIP']
for name in ['configure_handle_return','stack_usage_return','stack_final_return','dump_stack_return','handle_return','query_return']:assert by[name]['status']=='0x0'
usage=bytes.fromhex(by['stack_usage_call']['usage_stack']['bytes'])
assert usage[:2]==b'\x1b\x16' and usage[4]==1 and struct.unpack_from('<I',usage,8)[0]==3
call=t['calls'][0];ret=by['return'];caller=by['caller_status']
assert call['completed'] and ret['thread']==caller['thread']==call['thread']
assert ret['registers']['ESP']==call['stack'] and caller['registers']['EIP']==call['return_address']
assert int(caller['registers']['ESP'],16)==int(call['stack'],16)+8
fs=by['fsctl_call'];fe=by['fatx_entry'];fr=by['fatx_return'];args=[int(v,16) for v in fs['arguments']]
assert args[5]==0x9003b and args[7]==8 and args[9]==4
assert fs['input']['address']==hex(args[6]) and fs['input']['length']==8
assert bytes.fromhex(fs['input']['bytes'])==struct.pack('<Q',65536)
sl=bytes.fromhex(fe['stack_location'])
assert sl[0]==0x0d and sl[1] in [0,4] # IRP_MJ_FILE_SYSTEM_CONTROL
assert struct.unpack_from('<4I',sl,4)==(4,8,0x9003b,args[6])
assert fe['input']==fs['input'] and fe['requestor_mode']==0 and fe['user_buffer']==hex(args[8])
fc=t['fatx_calls'][0];assert fc['returned'] and fe['thread']==fr['thread']==fc['thread']
assert int(fr['registers']['ESP'],16)==int(fc['stack'],16)+4 and fr['registers']['EIP']==fc['return_address']
assert t['runtime_pins'][fe['resident_pin']]['module']=='xwnfatx.sys'
for name in ['fatx_return','fsctl_return','return','caller_status','caller_error']:assert by[name]['status']=='0xc0000010'
assert call['status']==fc['status']=='0xc0000010'
assert by['fsctl_return']['input_after']==fs['input']
assert by['fsctl_return']['output_after']==fs['output_before']
# This immediate error returns in EAX; the caller IOSB remains the previous
# successful 24-byte standard-information query. Do not treat it as success.
assert by['fsctl_return']['iosb']==fs['iosb_before']
assert struct.unpack('<2I',bytes.fromhex(fs['iosb_before']['bytes']))==(0,24)
assert a['debugger'] and not a['ordinary_qualified'] and a['workload_and_persistence_passed'] and a['integrity_passed']
assert not a['strict_qualification_passed'] and [(v['source'],v['event_id']) for v in a['warnings_errors']]==[('Ftdisk',44),('Ftdisk',49)]
r=dict(scope=__doc__,trace_sha256=sha(out/'trace.json'),audit_sha256=sha(out/'audit.json'),diagnostic_passed=True,events=len(ev),resident_pins=len(t['runtime_pins']),complete_calls=1,fatx_calls=1,usage_status='0x0',fsctl='0x9003b',requested_map_bytes=65536,input_length=8,output_length=4,requestor_mode='KernelMode',fatx_status='0xc0000010',final_status='0xc0000010',output_untouched=True,strict_qualification_passed=False,ordinary_qualified=False,physical_access=False)
path=k/'trace-verification.json'
if path.exists():assert read(path)==r
else:path.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r,indent=2))
