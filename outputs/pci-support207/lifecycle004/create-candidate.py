"""Fresh Unicode CM removal trial; preserve the closed ANSI API failure."""
from pathlib import Path
k=Path(__file__).resolve().parent;old=k.parent/'lifecycle003'
names='xwnrsc.c resources.h install.c probe.c restart.h power-test.h remove-test.h resource-log.h xwnrsc.inf Build-001.ps1 review-build.py prepare-emulator.py run-emulator.py audit-emulator.py review-pnp.py Prepare-Emulator001.ps1 Run-Emulator001.ps1 Audit-Pnp001.ps1 Continue-001.ps1 test-start.c resource-tests.h vectors.h start-vector.h'.split()
for name in names:
    p=k/name;assert not p.exists()
    s=(old/name).read_text().replace('lifecycle003','lifecycle004').replace('xwnpcilife3','xwnpcilife4').replace('4764','4774').replace('4766','4776')
    if name=='xwnrsc.inf':s=s.replace('0.1.0.223','0.1.0.224')
    if name=='remove-test.h':
        s=s.replace('char name[MAX_PATH];','WCHAR name[MAX_PATH];char utf8[MAX_PATH*3];')
        s=s.replace('CM_Query_And_Remove_SubTreeA(instance,&veto,name,sizeof(name),','CM_Query_And_Remove_SubTreeW(instance,&veto,name,MAX_PATH,')
        s=s.replace('text("remove_veto_name=");text(name);', 'name[MAX_PATH-1]=0;clear_bytes(utf8,sizeof(utf8));\n    if(!WideCharToMultiByte(CP_UTF8,0,name,-1,utf8,sizeof(utf8),NULL,NULL))number("veto_conversion_error=",GetLastError());\n    text("remove_veto_name=");text(utf8);')
    if name=='xwnrsc.c':
        needle='    switch(sp->MinorFunction) {'
        assert s.count(needle)==1
        s=s.replace(needle,'    /* Stage5 records actual PnP minor dispatches, including query/remove. */\n    trace_resources(5,sp->MinorFunction,0,NULL,0,NULL,0);\n'+needle)
    if name=='run-emulator.py':s=s.replace("'-m','64','-no-shutdown','-no-reboot',","'-m','64',")
    if name=='review-pnp.py':
        start=s.index("r['limits']=")
        end=s.index('\nsave(dest,r)',start)
        s=s[:start]+"r['limits']='Resource-only test. Stage5 trace records PnP dispatch minor codes; completed removal requires interface absence and successful re-enumeration/query. No telemetry, HAL candidate boot, ordinary cold-boot or physical qualification.'"+s[end:]
    p.write_text(s,newline='\n')
(k/'.gitattributes').write_text('* -text whitespace=cr-at-eol\n')
