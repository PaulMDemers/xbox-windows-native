"""Fresh ordinary guard validation; only the path-derived runner changes."""
import ast,hashlib,json,shutil
from pathlib import Path
k=Path(__file__).resolve().parent;old=k.parent/'video-installer-owner177';ws=k.parents[1]
assert not (k/'Run.ps1').exists()
for n in ['atomic_json.py','audit.py','check-leases.ps1','close-emulator.py','common.py','gdi-probe.c',
          'preflight.py','prepare.py','Run.ps1','sample_analysis.py','timing-interface.json','sites.json']:
    s=(old/n).read_text(encoding='utf-8').replace('video-installer-owner177','video-restart-guard178').replace('vowner177','vguard178').replace('xwnvo177','xwnvg178')
    if n=='Run.ps1':
        s=s.replace('debugger=$true','debugger=$false').replace('-GdbPort 4595','').replace('-Seconds 480','-Seconds 210')
    if n in ['audit.py','close-emulator.py']:
        s=s.replace('debugger=True','debugger=False')
    if n.endswith('.py'):ast.parse(s)
    (k/n).write_text(s,encoding='utf-8')
(k/'artifacts').mkdir(exist_ok=False)
for n in ['gdi-probe.exe','umpnpmgr.dll','advapi32.dll','ntdll.dll']:shutil.copyfile(old/'artifacts'/n,k/'artifacts'/n)
s=(k.parent/'video-paired-timing166/runner.c').read_text(encoding='utf-8')
s=s.replace('#include <windows.h>','#include <windows.h>\n#include "restart_gate.h"\ntypedef DWORD (WINAPI *WAIT_INSTALL)(DWORD);\nstatic WAIT_INSTALL WaitInstall;')
s=s.replace('void WINAPI mainCRTStartup(void) {', '''static uint32_t query_install(void *context,uint32_t timeout) {(void)context;return WaitInstall(timeout);}
static int request_restart(void *context) {(void)context;return ExitWindowsEx(EWX_REBOOT,0)!=0;}
static void gate_record(void *context,const char *label,uint32_t value) {
    char line[128];(void)context;wsprintfA(line,"%s %lu\\r\\n",label,(DWORD)value);record(line);
}
void WINAPI mainCRTStartup(void) {''')
s=s.replace('    record("ATTEMPT_ONCE\\r\\n");','''    record("ATTEMPT_ONCE\\r\\n");
    WaitInstall=(WAIT_INSTALL)GetProcAddress(LoadLibraryA("setupapi.dll"),"CMP_WaitNoPendingInstallEvents");
    if(!WaitInstall){record("FAIL_INSTALL_EXPORT\\r\\n");ExitProcess(12);}''')
s=s.replace('    CloseHandle(token);record("NORMAL_RESTART_REQUEST\\r\\n");\n    if(!ExitWindowsEx(EWX_REBOOT,0)){record("FAIL_RESTART\\r\\n");ExitProcess(11);}', '''    CloseHandle(token);
    status=(DWORD)xwn_guarded_restart(NULL,query_install,request_restart,gate_record);
    if(status){CloseHandle(Log);ExitProcess(status==1?13:(status==2?14:11));}''')
assert 'xwn_guarded_restart' in s and s.count('ExitWindowsEx(')==1
(k/'runner.c').write_text(s,encoding='utf-8')
# Providers are reviewed after the new compilation; no inherited review claims.
print('Fresh178 ordinary runner gate sources prepared; no guest launch')
