"""Derive a joined playback runner without weakening the existing restart gates."""
from pathlib import Path
k=Path(__file__).resolve().parent
s=(k.parent/'setup-wizard-automation201/guardian002.c').read_text()
s=s.replace('#include "restart_gate201.h"','#include "../setup-wizard-automation201/restart_gate201.h"').replace('#include "setup_gate201.h"','#include "../setup-wizard-automation201/setup_gate201.h"')
s=s.replace('guardian201.log','runner207.log').replace('"GUARDIAN201",1','"RUNNER207",1')
anchor='    if(!OpenProcessToken(GetCurrentProcess(),TOKEN_ADJUST_PRIVILEGES|TOKEN_QUERY,&token))ExitProcess(98);'
assert s.count(anchor)==1
s=s.replace(anchor,'''    wsprintfA(path,"%s\\\\probe.exe",base);si.cb=sizeof(si);
    if(!CreateProcessA(path,NULL,NULL,NULL,FALSE,0,NULL,base,&si,&pi)){record(NULL,"FAIL_CREATE_PROBE",GetLastError());ExitProcess(102);}
    CloseHandle(pi.hThread);record(NULL,"PROBE_STARTED",pi.dwProcessId);
    status=WaitForSingleObject(pi.hProcess,180000);record(NULL,"PROBE_JOIN_RESULT",status);
    if(status!=WAIT_OBJECT_0)ExitProcess(103);
    if(!GetExitCodeProcess(pi.hProcess,&status))ExitProcess(104);
    CloseHandle(pi.hProcess);record(NULL,"PROBE_EXIT",status);
    if(status)ExitProcess(105);
    status=xwn_wait_setup_idle(NULL,query,now,pause_poll,record,30000,5000,250);
    if(status)ExitProcess(106);
'''+anchor)
(k/'runner.c').write_text(s)
