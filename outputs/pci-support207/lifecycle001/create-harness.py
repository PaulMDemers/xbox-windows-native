"""Derive a fresh uniquely named owned trial from retained cold-audit harness."""
from pathlib import Path
k=Path(__file__).resolve().parent;old=k.parent/'ownership001'
def write(n,s):
    p=k/n;assert not p.exists();p.write_text(s,encoding='utf-8',newline='\n')
s=(old/'prepare-emulator.py').read_text(encoding='utf-8')
s=s.replace('Fresh NT5 resource-policy function tests; no driver installation or physical access.','Fresh genuine PnP resource-only installation; no physical access or bus transactions.')
s=s.replace("build-review002.json","build-review001.json").replace('build002','build001')
s=s.replace("for name in ('resource-tests.exe',):","for name in ('xwnrsc.sys','install.exe','probe.exe','xwnrsc.inf'):")
s=s.replace("data=(k/'artifacts/build001'/name).read_bytes()","data=((k/name) if name.endswith('.inf') else (k/'artifacts/build001'/name)).read_bytes()")
s=s.replace("read(k/'build001.json')['files'] if", "(read(k/'build001.json')['files']+read(k/'build001.json')['sources']) if")
s=s.replace('xwnpciown1','xwnpcilife1')
start=s.index("data=b'@echo off")
end=s.index('\n',start)
s=s[:start]+'''data=b'@echo off\\r\\nC:\\\\xwnpcilife1\\\\install.exe\\r\\n>C:\\\\xwnpcilife1\\\\install-exit.txt echo INSTALL_EXIT %errorlevel%\\r\\nC:\\\\xwnpcilife1\\\\probe.exe\\r\\n>C:\\\\xwnpcilife1\\\\probe-exit.txt echo PROBE_EXIT %errorlevel%\\r\\nexit\\r\\n' '''.rstrip()+s[end:]
s=s.replace('no_driver_installation=True','resource_only_driver_installation=True')
s=s.replace('ownership001 emulator001 prepared','lifecycle001 emulator001 prepared')
write('prepare-emulator.py',s)
s=(old/'run-emulator.py').read_text(encoding='utf-8').replace('4734','4744').replace('4736','4746')
s=s.replace('Bounded NT5 pure resource-function test; no driver installation, physical access, or PnP qualification.','Bounded resource-only PnP installation/restart trial; no physical access.')
# Observe dashboard return after sufficient time, but require cold EventLog evidence.
s=s.replace("        time.sleep(1)\n    r['closure_reason']", """        if time.monotonic()>deadline-145:
            try:
                f=connect();f.quit();r['dashboard_return_utc']=now();break
            except ftplib.all_errors:pass
        time.sleep(1)
    r['closure_reason']""")
write('run-emulator.py',s)
s=(old/'audit-emulator.py').read_text(encoding='utf-8')
s=s.replace('Cold NT5 resource-function rehearsal; no kernel installation or allocator qualification.','Cold genuine resource-only PnP trial audit; no hardware qualification.')
s=s.replace('xwnpciown1','xwnpcilife1').replace("('resources.log','result.txt')","('install.log','lifecycle.log','install-exit.txt','probe-exit.txt')")
s=s.replace("'\\\\xwnsmb','\\\\xwnfatx'","'\\\\xwnsmb','\\\\xwnrsc','\\\\xwnfatx'")
start=s.index("r['helpers_exit_zero']")
end=s.index("save(dest,r);",start)
s=s[:start]+'''r['install_exit_zero']=r['logs'].get('install-exit.txt','').splitlines()==['INSTALL_EXIT 0']
r['lifecycle_completed']='RESOURCE_ONLY_PNP_LIFECYCLE_END' in r['logs'].get('lifecycle.log','')
r['normal_shutdown_event_count']=sum(v['source']=='EventLog' and v['event_id']==6006 for v in r['new_events']['system'])
r['whole_boot_passed']=False
r['diagnostic_usable']=r['integrity_passed']
r['limits']='Resource-only PnP test; evaluate actual devnode, resource and SetupAPI data before qualification. No telemetry or hardware qualification. Inherited Ftdisk49 retained.'
''' +"save(dest,r);print(json.dumps({key:r[key] for key in ('install_exit_zero','lifecycle_completed','integrity_passed','normal_shutdown_event_count','logs','warnings_errors')},indent=2))\n"
write('audit-emulator.py',s)
for verb in ('Prepare','Run','Audit'):
    s=(old/(verb+'-Emulator001.ps1')).read_text(encoding='utf-8').replace('ownership001','lifecycle001')
    write(verb+'-Emulator001.ps1',s)
