"""New read-only ownership sites and one verified CloseHandle frame; no guest patch."""
import ast,hashlib,json,shutil,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];old=k.parent/'video-installer-close176'
assert not (k/'Run.ps1').exists()
names=['atomic_json.py','audit.py','check-leases.ps1','close-emulator.py','common.py','discover_kernel.py',
       'gdi-probe.c','preflight.py','prepare.py','Run.ps1','sample_analysis.py','supervise.py',
       'timing-interface.json','build-review.json','sites.json','trace.py','verify-trace.py','scope_match.py',
       'test-pin-contract002.py','test-scope002.py','test-return-scope.py']
for name in names:
    data=(old/name).read_text(encoding='utf-8').replace('video-installer-close176','video-installer-owner177').replace('vclose176','vowner177').replace('xwnvc176','xwnvo177')
    if name=='trace.py':
        data=data.replace('from scope_match import find_close_scope,find_return_call','from scope_match import find_close_scope,find_return_call\nfrom close_frame import capture_frame')
        needle="        # Target-scope early loader and termination observations."
        assert needle in data
        data=data.replace(needle,"""        if site and site['kind']=='token_lifecycle' and who['image'].lower()!='services.exe':
            r.setdefault('lifecycle_filtered_hits',[]).append(dict(address=a,owner=who,reason='Outside services owner'))
            assert len(r['lifecycle_filtered_hits'])<=1024
            remove(a);step();arm(a);save();continue
"""+needle)
        needle="            args=struct.unpack('<'+'I'*(site['argc']+1),g.read(cpu['ESP'],4*(site['argc']+1)))"
        assert needle in data
        data=data.replace(needle,"""            if site['kind']=='token_lifecycle':
                event.update(function=site['name'],kind=site['kind'],code_site=True)
                try:
                    base=a-site['rva'];event['saved_token_slot']=dict(address=base+0x15b64,value=u32(base+0x15b64))
                    event['companion_slot']=dict(address=base+0x15b68,value=u32(base+0x15b68))
                    event['stack_prefix']=list(struct.unpack('<8I',g.read(cpu['ESP'],32)))
                except Exception as exc:event['slot_unknown']=repr(exc)
            args=struct.unpack('<'+'I'*(site['argc']+1),g.read(cpu['ESP'],4*(site['argc']+1)))""")
        # Lifecycle sites are instruction stops; stack[0] is not a call's return.
        needle="            event.update(function=site['name'],kind=site['kind'],caller=args[0],arguments=list(args[1:]))"
        data=data.replace(needle,"""            if site['kind']!='token_lifecycle':event.update(function=site['name'],kind=site['kind'],caller=args[0],arguments=list(args[1:]))""")
        needle="                call=dict(entry_index=event['index'],function=site['name'],native_api=True"
        assert needle in data
        data=data.replace(needle,"""                if site['name']=='NtClose' and event['cross_thread_token_close']:
                    try:
                        wrapper=event['caller_identity']['module'];assert wrapper['name']=='kernel32.dll'
                        pe=pes['kernel32.dll'];export=next(e for e in pe.DIRECTORY_ENTRY_EXPORT.symbols if e.name==b'CloseHandle')
                        assert ret-wrapper['base']==0x7ef0 and export.address==0x7ea1
                        meta=dict(module='kernel32.dll',name='CloseHandle_frame_contract',address=wrapper['base']+export.address,
                                  rva=export.address,validation_bytes=pe.get_data(export.address,32).hex())
                        event['close_wrapper_pin']=pin(meta,who)
                        assert pe.get_data(export.address,3)==bytes.fromhex('558bec')
                        teb=u32(who['thread']+review['teb_offset'])
                        frame=capture_frame(g.read,cpu,teb,args[1]);event['close_wrapper_frame']=frame
                        event['higher_close_caller']=caller_pin(frame['return_address'],who)
                        row=event['higher_close_caller']['module']
                        if row['name']=='umpnpmgr.dll':
                            event['saved_token_slot']=dict(address=row['base']+0x15b64,value=u32(row['base']+0x15b64))
                    except Exception as exc:event['close_frame_unknown']=repr(exc)
"""+needle)
    if name.endswith('.py'):ast.parse(data)
    (k/name).write_bytes(data.encode())
(k/'artifacts').mkdir(exist_ok=False)
for name in ['runner.exe','gdi-probe.exe','umpnpmgr.dll','advapi32.dll','ntdll.dll']:shutil.copyfile(old/'artifacts'/name,k/'artifacts'/name)
sys.path.insert(0,str(ws/'work/python-packages'));import pefile,capstone
r=json.loads((k/'sites.json').read_text());pe=pefile.PE(str(ws/r['binaries']['umpnpmgr.dll']['path']))
md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
blocks=[]
for name,v in [('owner_cleanup_entry',0x5959),('owner_cleanup_token_load',0x5989),('owner_cleanup_token_closed',0x599b),
               ('owner_cleanup_before_clear',0x59ad),('owner_cleanup_after_clear',0x59b4),
               ('owner_acquire_token_call',0x5d7c),('owner_acquire_token_return',0x5d82),('installer_token_push',0x66d2)]:
    raw=pe.get_data(v,32)
    r['sites'].append(dict(name=name,module='umpnpmgr.dll',kind='token_lifecycle',argc=0,rva=v,
                          address=pe.OPTIONAL_HEADER.ImageBase+v,validation_bytes=raw.hex()))
    blocks.append(dict(name=name,rva=v,raw=raw.hex(),instructions=[dict(rva=i.address-pe.OPTIONAL_HEADER.ImageBase,bytes=i.bytes.hex(),instruction=i.mnemonic+' '+i.op_str) for i in md.disasm(raw,pe.OPTIONAL_HEADER.ImageBase+v)]))
(k/'sites.json').write_text(json.dumps(r,indent=2)+'\n')
(k/'owner-site-review.json').write_text(json.dumps(dict(binary=r['binaries']['umpnpmgr.dll'],blocks=blocks,
    guest_changed=False,physical_access=False,limits='Static sites are leads; runtime exact code/module pins and owner/thread/slot values required. No generic frame walk.'),indent=2)+'\n')
print('Fresh177 observation kit prepared; no guest launch')
