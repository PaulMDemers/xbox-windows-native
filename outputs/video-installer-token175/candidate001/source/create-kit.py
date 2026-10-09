"""New thread-scoped native API observation, unchanged guest and old failures."""
import ast,hashlib,json,shutil,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];old=k.parent/'video-installer-target174'
assert not (k/'Run.ps1').exists()
names=['atomic_json.py','audit.py','check-leases.ps1','close-emulator.py','common.py','discover_kernel.py','freeze.py',
       'gdi-probe.c','preflight.py','prepare.py','Run.ps1','sample_analysis.py','supervise.py','timing-interface.json','build-review.json',
       'sites.json','site-disassembly.json','trace.py','test-pin-contract.py']
for name in names:
    data=(old/name).read_text(encoding='utf-8').replace('video-installer-target174','video-installer-token175').replace('vtarget174','vtoken175').replace('xwnvt174','xwnvk175')
    if name=='freeze.py':data=data.replace("k/'observer-scope-review.json'","k/'api-scope-review.json'")
    if name=='trace.py':
        data=data.replace("sites={v['address']:v for v in review['sites'] if v['module']!='ntoskrnl.exe'}", "sites={v['address']:v for v in review['sites'] if v['module']!='ntoskrnl.exe' and v['kind']!='native_api'}")
        data=data.replace(';shutdown_seen=False',';shutdown_seen=False;api_scopes={};api_sites={v[\'address\']:v for v in review[\'sites\'] if v[\'kind\']==\'native_api\'}')
        data=data.replace("        # Target-scope early loader", """        if site and site['kind']=='native_api' and who['thread'] not in api_scopes:
            r.setdefault('native_filtered_hits',[]).append(dict(address=a,owner=who,reason='Outside active services installer outer call'))
            assert len(r['native_filtered_hits'])<=1024
            remove(a);step();arm(a);save();continue
        # Target-scope early loader""")
        needle="            if site['kind'] in ['create_inner','create_outer']:"
        assert needle in data
        data=data.replace(needle,"""            if site['kind']=='native_api':
                scope=api_scopes[who['thread']];event['outer_scope']=dict(scope)
                ret=args[0];assert 0x10000<=ret<0x80000000
                try:event['caller_identity']=caller_pin(ret,who)
                except Exception as exc:event['caller_identity_unknown']=repr(exc)
                call=dict(entry_index=event['index'],function=site['name'],native_api=True,thread=who['thread'],parent_pid=who['pid'],stack=cpu['ESP'],stack_delta=4*(site['argc']+1),
                    return_address=ret,return_bytes=g.read(ret,16).hex(),arguments=list(args[1:]),outer_scope=dict(scope),returned=False)
                pending.setdefault((who['thread'],ret),[]).append(call);arm(ret)
                if site['name']=='NtSetInformationProcess':
                    try:
                        assert args[4]<=4096;event['information_prefix']=g.read(args[3],min(args[4],32)).hex()
                    except Exception as exc:event['information_unknown']=repr(exc)
            elif site['kind'] in ['create_inner','create_outer']:""")
        needle="                pending.setdefault((who['thread'],ret),[]).append(call);arm(ret);event['creation_flags']=args[7]"
        assert needle in data
        data=data.replace(needle,needle+"""
                if site['kind']=='create_outer' and who['image'].lower()=='services.exe' and 'rundll32' in (event.get('command_line') or '').lower():
                    assert who['thread'] not in api_scopes
                    api_scopes[who['thread']]=dict(entry=event['index'],thread=who['thread'],process=who['process'],pid=who['pid'],token_handle=args[1],command_line=event.get('command_line'))
                    for addr,meta in api_sites.items():sites[addr]=meta;arm(addr)""")
        needle="            if cpu['EAX'] and call['process_info']:"
        assert needle in data
        data=data.replace(needle,"            if not call.get('native_api') and cpu['EAX'] and call['process_info']:")
        needle="        assert len(r['events'])<1024;r['events'].append(event);save()"
        assert needle in data
        data=data.replace(needle,"""        if not site and call.get('native_api'):
            event['native_status']=hex(cpu['EAX']);event['outer_scope']=call['outer_scope']
            if cpu['EAX']<0x80000000:
                try:
                    if call['function']=='NtDuplicateToken':event['output_handle']=u32(call['arguments'][5])
                    elif call['function']=='NtQueryInformationToken':event['output_prefix']=g.read(call['arguments'][2],min(call['arguments'][3],32)).hex()
                except Exception as exc:event['output_unknown']=repr(exc)
        if not site and call['function']=='CreateProcessAsUserW' and who['thread'] in api_scopes:
            assert not any(v.get('native_api') and v['thread']==who['thread'] for vals in pending.values() for v in vals)
            del api_scopes[who['thread']]
            if not api_scopes:
                for addr in api_sites:remove(addr);sites.pop(addr,None)
        assert len(r['events'])<1024;r['events'].append(event);save()""")
    if name.endswith('.py'):ast.parse(data)
    (k/name).write_bytes(data.encode())
(k/'artifacts').mkdir(exist_ok=False)
for name in ['runner.exe','gdi-probe.exe','umpnpmgr.dll','advapi32.dll','ntdll.dll']:shutil.copyfile(old/'artifacts'/name,k/'artifacts'/name)
sys.path.insert(0,str(ws/'work/python-packages'));import pefile,capstone
pe=pefile.PE(str(k/'artifacts/ntdll.dll'));exports={e.name.decode():e for e in pe.DIRECTORY_ENTRY_EXPORT.symbols if e.name}
review=json.loads((k/'sites.json').read_text());dis=json.loads((k/'site-disassembly.json').read_text());md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
for name,argc in [('NtQueryInformationToken',5),('NtDuplicateToken',6),('NtSetInformationProcess',4),('NtClose',1)]:
    e=exports[name];assert not e.forwarder;raw=pe.get_data(e.address,32)
    ins=list(md.disasm(raw,pe.OPTIONAL_HEADER.ImageBase+e.address))
    assert ins[2].mnemonic=='int' and ins[2].op_str=='0x2e' and ins[3].address-pe.OPTIONAL_HEADER.ImageBase==e.address+11
    assert ins[3].mnemonic=='ret' and int(ins[3].op_str,0)==argc*4
    review['sites'].append(dict(name=name,module='ntdll.dll',kind='native_api',argc=argc,rva=e.address,address=pe.OPTIONAL_HEADER.ImageBase+e.address,validation_bytes=raw.hex()))
    dis.append(dict(module='ntdll.dll',name=name,rva=e.address,argc=argc,verified_stdcall_stack_delta=4*(argc+1),instructions=[dict(rva=i.address-pe.OPTIONAL_HEADER.ImageBase,bytes=i.bytes.hex(),instruction=i.mnemonic+' '+i.op_str) for i in ins[:4]]))
(k/'sites.json').write_text(json.dumps(review,indent=2)+'\n');(k/'site-disassembly.json').write_text(json.dumps(dis,indent=2)+'\n')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
(k/'api-scope-review.json').write_text(json.dumps(dict(parent_trace_sha256=sha(old/'trace.py'),new_trace_sha256=sha(k/'trace.py'),
    native_api_breakpoints='Armed only inside actual services rundll32 CreateProcessAsUserW; record originating ETHREAD, exact entry/return stack and outer token/command. Other-thread hits excluded and retained; no global NtClose observation.',
    bounds_unchanged=True,driver_or_settings_changed=False,physical_access=False),indent=2)+'\n')
print('175 scoped native API diagnostic prepared; no guest launch')
