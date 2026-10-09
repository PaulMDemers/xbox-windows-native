"""Fresh cross-thread/kernel close observation; no changed guest state."""
import ast,hashlib,json,shutil,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];old=k.parent/'video-installer-token175'
assert not (k/'Run.ps1').exists()
names=['atomic_json.py','audit.py','check-leases.ps1','close-emulator.py','common.py','discover_kernel.py','freeze.py',
       'gdi-probe.c','preflight.py','prepare.py','Run.ps1','sample_analysis.py','supervise.py','timing-interface.json','build-review.json',
       'sites.json','site-disassembly.json','trace.py','test-pin-contract.py','verify-trace.py']
for name in names:
    data=(old/name).read_text(encoding='utf-8').replace('video-installer-token175','video-installer-close176').replace('vtoken175','vclose176').replace('xwnvk175','xwnvc176')
    if name=='trace.py':
        data=data.replace('from discover_kernel import discover','from discover_kernel import discover\nfrom scope_match import find_close_scope')
        needle="                sites[site['address']]=site;arm(site['address'])"
        assert needle in data
        data=data.replace(needle,"""                if site['kind']=='native_api':
                    if site['address']!=original['address']:api_sites.pop(original['address'],None)
                    api_sites[site['address']]=site
                else:sites[site['address']]=site;arm(site['address'])""")
        needle="        if site and site['kind']=='native_api' and who['thread'] not in api_scopes:"
        assert needle in data
        data=data.replace(needle,"""        borrowed_scope=None
        if site and site['kind']=='native_api' and who['thread'] not in api_scopes and site['name'] in ['NtClose','_NtClose@4']:
            handle=u32(cpu['ESP']+4)
            borrowed_scope=find_close_scope(api_scopes,who['process'],handle)
        if site and site['kind']=='native_api' and who['thread'] not in api_scopes and borrowed_scope is None:""")
        data=data.replace("scope=api_scopes[who['thread']];event['outer_scope']=dict(scope)","scope=api_scopes.get(who['thread'],borrowed_scope);assert scope is not None;event['outer_scope']=dict(scope);event['cross_thread_token_close']=who['thread']!=scope['thread']")
        data=data.replace("ret=args[0];assert 0x10000<=ret<0x80000000\n                try:event['caller_identity']=caller_pin(ret,who)","ret=args[0];assert (0x80000000<=ret<=0xffffffff) if site['module']=='ntoskrnl.exe' else (0x10000<=ret<0x80000000)\n                try:event['caller_identity']=caller_pin(ret,who)",1)
        assert 'from scope_match import' in data and 'borrowed_scope' in data
    if name.endswith('.py'):ast.parse(data)
    (k/name).write_bytes(data.encode())
(k/'artifacts').mkdir(exist_ok=False)
for name in ['runner.exe','gdi-probe.exe','umpnpmgr.dll','advapi32.dll','ntdll.dll']:shutil.copyfile(old/'artifacts'/name,k/'artifacts'/name)
sys.path.insert(0,str(ws/'work/python-packages'));import pefile,capstone
r=json.loads((k/'sites.json').read_text());pubs=json.loads((k.parent/'native-windows-nt5-kernel/kernel-publics.json').read_text())['symbols']
pe=pefile.PE(str(ws/r['binaries']['ntoskrnl.exe']['path']));v=pubs['_NtClose@4']['rva'];raw=pe.get_data(v,32)
r['sites'].append(dict(name='_NtClose@4',module='ntoskrnl.exe',kind='native_api',argc=1,rva=v,address=r['kernel_base_expected']+v,validation_bytes=raw.hex()))
(k/'sites.json').write_text(json.dumps(r,indent=2)+'\n')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
(k/'api-scope-review.json').write_text(json.dumps(dict(parent_trace_sha256=sha(old/'trace.py'),new_trace_sha256=sha(k/'trace.py'),
    change='Inside active outer calls only, user/kernel close from another thread may be observed when exact token handle AND current thread owner process pointer match active scope. Unrelated process handle values excluded. Unknown attached-process contexts not claimed.',
    kernel_close_rva=v,guest_changed=False,bounds_unchanged=True,physical_access=False),indent=2)+'\n')
print('New176 cross-thread/kernel close observer; no guest launch')
