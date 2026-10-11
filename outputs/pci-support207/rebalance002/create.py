"""Create one helper and three diagnostic arms; preserve stop001 source and binaries."""
from pathlib import Path
import shutil
k = Path(__file__).resolve().parent
old = k.parent / 'stop001'
assert not (k / 'probe.c').exists()
for name in ('probe.c', 'rebalance-test.h', 'cancel-test.h', 'remove-test.h', 'restart.h', 'power-test.h', 'e_allocation.py', 'xwnrsc.inf', 'prepare-emulator002.py', 'run-emulator002.py', 'audit-emulator002.py', 'review-pnp002.py', 'review-build002.py'):
    shutil.copy2(old / name, k / name)
(k / '.gitattributes').write_text('* -text whitespace=cr-at-eol\n')
p = k / 'probe.c'
s = p.read_text()
anchor = '#include "restart.h"'
s = s.replace(anchor, '''static void mark(const char *label)
{
    FILETIME t;GetSystemTimeAsFileTime(&t);
    text("mark=");text(label);text("\\r\\n");
    number("utc_filetime_hi=",t.dwHighDateTime);number("utc_filetime_lo=",t.dwLowDateTime);
    number("uptime_ms=",GetTickCount());
}
''' + anchor)
s = s.replace('text("RESOURCE_ONLY_PNP_LIFECYCLE_BEGIN\\r\\n");', 'text("RESOURCE_ONLY_PNP_LIFECYCLE_BEGIN\\r\\n");mark("begin");')
s = s.replace('text("PNP_RESTART_REQUEST\\r\\n");', 'mark("property_change_begin");text("PNP_RESTART_REQUEST\\r\\n");')
s = s.replace('if(!exercise_power() || !query())ExitProcess(28);', 'mark("power_begin");if(!exercise_power() || !query())ExitProcess(28);mark("power_end");')
s = s.replace('if(!exercise_remove(dev.DevInst,capabilities))ExitProcess(29);', 'mark("remove_begin");if(!exercise_remove(dev.DevInst,capabilities))ExitProcess(29);mark("remove_end");')
p.write_text(s)
p = k / 'rebalance-test.h';s = p.read_text()
s = s.replace('BOOL ok=FALSE,ready;', 'BOOL ok=FALSE,ready;char mode_text[4];DWORD mode;')
s = s.replace('    set=SetupDiGetClassDevsA', '''    clear_bytes(mode_text,sizeof(mode_text));
    if(GetEnvironmentVariableA("XWN_REBALANCE_MODE",mode_text,sizeof(mode_text))!=1 || mode_text[0]<'0' || mode_text[0]>'2')return FALSE;
    mode=(DWORD)(mode_text[0]-'0');number("rebalance_mode=",mode);mark("rebalance_begin");
    if(!mode){text("REBALANCE_SKIP_CONTROL\\r\\n");Sleep(10000);mark("rebalance_end");return query();}
    set=SetupDiGetClassDevsA''', 1)
s = s.replace('for(phase=0;phase<2;++phase)', 'for(phase=mode-1;phase<mode;++phase)')
s = s.replace('CloseHandle(file);return ok;', 'CloseHandle(file);mark("rebalance_operation_end");Sleep(10000);mark("rebalance_end");return ok;')
p.write_text(s)
for name in ('prepare-emulator002.py', 'run-emulator002.py', 'audit-emulator002.py', 'review-pnp002.py'):
    p = k / name;s = p.read_text().replace("('control','candidate')", "('skip','allow','veto')")
    s = s.replace("k/'build-review002.json'", "k/'build-review001.json'").replace("k/'build002.json'", "k/'build001.json'").replace("k/'artifacts/build002'", "k/'artifacts/build001'").replace("k/'artifacts/build002/xwnrsc.sys'", "k/'artifacts/build001/xwnrsc.sys'")
    s = s.replace("variant=='control'", 'False').replace("int(variant=='candidate')", '1')
    s = s.replace('4804', '4814').replace('4806', '4816')
    s = s.replace("print('stop001 emulator001", "print('rebalance002 emulator001")
    if name == 'prepare-emulator002.py':
        s = s.replace("(art/'startup.cmd').write_bytes(data)", "data=data.replace(b'@echo off\\r\\n',b'@echo off\\r\\nset XWN_REBALANCE_MODE='+str(('skip','allow','veto').index(variant)).encode()+b'\\r\\n')\n(art/'startup.cmd').write_bytes(data)")
    if name == 'run-emulator002.py':
        s = s.replace('print(json.dumps(r))', "print(json.dumps({x:r.get(x) for x in ('launch_requested_utc','closed_utc','closed','closure_reason','source_unchanged','dashboard_return_utc','failure')}))")
    if name == 'audit-emulator002.py':s = s.replace("'normal_shutdown_event_count','logs','warnings_errors'", "'normal_shutdown_event_count','warnings_errors'")
    p.write_text(s)
p = k / 'review-build002.py';s = p.read_text().replace('build002','build001').replace('build-review002','build-review001').replace("assert read(k/'tests002.json')['passed']", "assert sha(k/'artifacts/build001/xwnrsc.sys')=='3c906ae0cb7cb7af794de7caeabb99e52d15e00b8bc10135f8e28a8632ce1a92'")
(k / 'review-build.py').write_text(s)
s = (old / 'Continue-002.ps1').read_text().replace('pipeline002','pipeline001').replace('Build-002','Build-001').replace('review-build002.py','review-build.py').replace('/stop001/','/rebalance002/').replace("@('candidate')", "@('skip','allow','veto')")
s = s.replace(' -or !$r.stop_cancel_qualified','')
(k / 'Continue-001.ps1').write_text(s)
