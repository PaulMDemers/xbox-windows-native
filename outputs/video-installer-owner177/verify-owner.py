"""Post-run independent slot, close-frame and logoff cleanup verification."""
import hashlib,json,struct,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];out=k/'candidate001';dest=out/'owner-verification.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
t=read(out/'trace.json');v=read(out/'trace-verification.json');c=read(out/'closure.json')
assert c['closed'] and v['diagnostic_capture_complete']
e={x['index']:x for x in t['events']};p={x['entry']:x for x in v['creation_pairs']+v['native_api_pairs']}
acq,opened,push,cleanup,load,user,kernel,closed,before,clear=[e[i] for i in [42,43,196,202,203,204,205,208,209,210]]
token=opened['saved_token_slot']['value'];slot=opened['saved_token_slot']['address'];process=opened['owner']['process']
assert token==1896 and slot==1987795812
assert acq['function']=='owner_acquire_token_call' and opened['function']=='owner_acquire_token_return'
assert acq['saved_token_slot']['value']==0 and opened['registers']['EAX']==1
assert acq['stack_prefix'][:3]==[1884,0xf01ff,slot]
assert opened['registers']['ESP']==acq['registers']['ESP']+12
assert opened['owner']['thread']==acq['owner']['thread']
assert push['function']=='installer_token_push' and push['saved_token_slot']['value']==token
assert cleanup['function']=='owner_cleanup_entry' and cleanup['stack_prefix'][1]==5
assert load['function']=='owner_cleanup_token_load' and load['saved_token_slot']['value']==token
assert user['function']=='NtClose' and kernel['function']=='_NtClose@4'
for x in [user,kernel]:
    assert x['cross_thread_token_close'] and x['arguments']==[token] and p[x['index']]['result']==0
    assert x['owner']['thread']==cleanup['owner']['thread']!=push['owner']['thread']
    assert x['owner']['process']==process and x['outer_scope']['token_handle']==token
assert p[204]['returned']==207 and p[205]['returned']==206
assert closed['function']=='owner_cleanup_token_closed' and closed['registers']['EAX']==1
assert before['function']=='owner_cleanup_before_clear' and before['saved_token_slot']['value']==token
assert clear['function']=='owner_cleanup_after_clear' and clear['saved_token_slot']['value']==0
assert all(x['owner']['thread']==cleanup['owner']['thread'] for x in [load,closed,before,clear])
assert all(x['owner']['process']==process for x in [acq,opened,push,cleanup,load,user,kernel,closed,before,clear])
frame=user['close_wrapper_frame'];pin=t['pins'][user['higher_close_caller']['pin']]
assert not frame['previous_frame_walked'] and frame['handle']==token
assert frame['ebp']==frame['esp']+8 and frame['stack_limit']<=frame['esp'] and frame['ebp']+12<=frame['stack_base']
assert pin['module']['name']=='umpnpmgr.dll' and pin['rva']==0x599b
assert frame['return_address']==pin['address']==closed['registers']['EIP']
wrapper=t['pins'][user['close_wrapper_pin']]
assert wrapper['module']['name']=='kernel32.dll' and wrapper['rva']==0x7ea1
assert wrapper['raw'].startswith('558bec')
outer=user['outer_scope']['entry'];inner=[q for q in v['creation_pairs'] if q['function']=='CreateProcessInternalW' and q['thread']==push['owner']['thread'] and outer<q['entry']<q['returned']<p[outer]['returned']]
assert len(inner)==1 and inner[0]['result']==1
failed=[q for q in v['native_api_pairs'] if q['function']=='NtQueryInformationToken' and q['arguments'][:2]==[token,8] and q['entry']>207 and q['returned']<p[outer]['returned']]
assert len(failed)==1 and failed[0]['result']==0xc0000008
assert p[outer]['result']==0 and p[outer]['last_error']==6 and 'DEV_01B4' in p[outer]['command_line']
assert clear['index']<inner[0]['returned']<failed[0]['entry']<p[outer]['returned']

# Cold static registration is a lead paired with the actual pinned runtime handler
# and control argument. Do not rename or invent an unobserved private symbol.
sys.path.insert(0,str(ws/'work/python-packages'));import pefile
meta=read(k/'sites.json')['binaries']['umpnpmgr.dll'];file=ws/meta['path'];assert sha(file)==meta['sha256'];pe=pefile.PE(str(file))
assert pe.get_data(0x5ae5,5)==b'\x68'+struct.pack('<I',pe.OPTIONAL_HEADER.ImageBase+0x5959)
assert pe.get_data(0x5aea,6)==b'\xff\x15'+struct.pack('<I',pe.OPTIONAL_HEADER.ImageBase+0x1100)
imp=next(i for d in pe.DIRECTORY_ENTRY_IMPORT for i in d.imports if i.address-pe.OPTIONAL_HEADER.ImageBase==0x1100)
assert imp.name==b'SetConsoleCtrlHandler'
other=[dict(entry=x['index'],thread=x['owner']['thread'],argument=x['stack_prefix'][1],token=x['saved_token_slot']['value']) for x in t['events'] if x.get('function')=='owner_cleanup_entry' and x['index']>cleanup['index']]
r=dict(passed=True,debugger=True,ordinary_qualified=False,physical_qualified=False,
    sources={x.name:sha(x) for x in [Path(__file__),out/'trace.json',out/'trace-verification.json',out/'closure.json']},
    token=token,slot=slot,process=process,acquisition=[42,43],installer_push=196,control_entry=202,control_argument=5,
    closing_thread=cleanup['owner']['thread'],installer_thread=push['owner']['thread'],
    user_close=[204,207],kernel_close=[205,206],wrapper_return_ump_rva='0x599b',clear=[209,210],
    inner_creation=inner[0],invalid_query=failed[0],outer_failure=p[outer],later_controls=other,
    static_registration=dict(handler_rva='0x5959',register_call_rva='0x5aea',import_name='SetConsoleCtrlHandler',binary_sha256=sha(file)),
    conclusion='Actual console control argument5 invokes UMP cleanup; it successfully closes the saved token and clears its slot while the installer still uses the copied handle, producing the captured invalid-handle failure.',
    limits='One verified wrapper frame, not a generic walk; debugger timing is not ordinary validation. No claim that this token failure itself produces the separate shutdown popup.')
dest.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print(json.dumps({n:r[n] for n in ['passed','token','control_argument','closing_thread','installer_thread','conclusion']}))
