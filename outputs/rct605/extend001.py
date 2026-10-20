"""New phase mechanism; preserve frozen parent source files untouched."""
from pathlib import Path
K=Path(__file__).resolve().parent
p=K/'fixture.c';s=p.read_text();s+='\nDWORD __cdecl probe_phase605(HANDLE request) {return SetEvent(request)?0x605face0u:0;}\n';p.write_text(s,newline='\n')
p=K/'subject002.c';s=p.read_text().replace('#include "dib_control.h"','#include "dib_control.h"\n#include "phase_control.h"')
s=s.replace('if(!graphics601())InterlockedIncrement(&failures);','if(!graphics601())InterlockedIncrement(&failures);\n    if(!phasecontrol605(control))InterlockedIncrement(&failures);');p.write_text(s,newline='\n')
p=K/'trace.c';s=p.read_text().replace('#include "dib_header.h"','#include "dib_header.h"\n#include "phase.h"')
s=s.replace('seen[16],resolved[16]','seen[17],resolved[17]').replace('nargs[16]={0,1,2,9,6,3,1,3,4,1,2,13,0,6,2,1}','nargs[17]={0,1,2,9,6,3,1,3,4,1,2,13,0,6,2,1,1}')
s=s.replace('static BOOL readmem(','''static PHASE605 phase_state;static HANDLE phase_request,phase_ack;
static DWORD phase_caps[2],phase_skipped[2];static BOOL defer_reported;
static BOOL phasecheck605(void) {
    DWORD wait,i,pending=0;int result;
    wait=WaitForSingleObject(phase_request,0);
    if(wait!=WAIT_OBJECT_0&&wait!=WAIT_TIMEOUT)return FALSE;
    for(i=0;i<64;i++)pending+=threads[i].stack.depth;
    result=phase605(&phase_state,wait==WAIT_OBJECT_0,pending);
    if(result<0)return FALSE;
    if(result==1&&!defer_reported){event("PHASE_PENDING",0,pending,seen[11]);defer_reported=TRUE;}
    if(result==2){
        event("PHASE",1,seen[11],phase_skipped[0]);seen[11]=0;
        if(!SetEvent(phase_ack))return FALSE;
    }
    return !failed;
}
static BOOL readmem(''')
s=s.replace('if(!lstrcmpA(text,"probe_dib604"))return 15;','if(!lstrcmpA(text,"probe_dib604"))return 15;\n    if(!lstrcmpA(text,"probe_phase605"))return 16;')
s=s.replace('f.api==14||f.api==15','f.api==14||f.api==15||f.api==16')
old='''            bp[index].enabled=FALSE;event("CAP",bp[index].api,seen[bp[index].api],bp[index].address);return TRUE;'''
new='''            if(bp[index].api==11){
                if(!phase_caps[phase_state.phase]){event("CAP",11,seen[11],bp[index].address);phase_caps[phase_state.phase]=1;}
                phase_skipped[phase_state.phase]++;return TRUE;
            }
            bp[index].enabled=FALSE;event("CAP",bp[index].api,seen[bp[index].api],bp[index].address);return TRUE;'''
assert old in s;s=s.replace(old,new)
s=s.replace('if(!observe(index,t,&c)||!holdothers','if(!phasecheck605()||!observe(index,t,&c)||!holdothers')
s=s.replace('    zero(&si,sizeof(si));zero(&pi,sizeof(pi));si.cb=sizeof(si);','''    SetLastError(0);phase_request=CreateEventA(0,TRUE,FALSE,"XWN605PhaseRequest");
    if(!phase_request||GetLastError()==ERROR_ALREADY_EXISTS){event("EVENT_FAIL",1,0,0);ExitProcess(92);}
    SetLastError(0);phase_ack=CreateEventA(0,TRUE,FALSE,"XWN605PhaseAck");
    if(!phase_ack||GetLastError()==ERROR_ALREADY_EXISTS){event("EVENT_FAIL",2,0,0);ExitProcess(93);}
    zero(&si,sizeof(si));zero(&pi,sizeof(pi));si.cb=sizeof(si);''')
s=s.replace('    event("TOTAL",requests,returns,bp_count);','    event("PHASE_END",phase_state.phase,phase_skipped[0],phase_skipped[1]);\n    event("TOTAL",requests,returns,bp_count);')
s=s.replace('FlushFileBuffers(logfile);CloseHandle(logfile);CloseHandle(process);','FlushFileBuffers(logfile);CloseHandle(logfile);CloseHandle(process);CloseHandle(phase_request);CloseHandle(phase_ack);')
p.write_text(s,newline='\n')
