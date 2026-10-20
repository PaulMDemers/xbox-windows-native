"""Fresh original timing/identity control; no game assets or closed runtime reuse."""
import hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;out=K/'source001.json';assert not out.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
sources={}
def copy(n,old):
 p=K.parent/f'rct{old}'/n;s=p.read_text(encoding='utf-8')
 sources[n]=dict(path=str(p),sha256=sha(p))
 for prefix in ['xwn','XWN','rct','run','RUN','subject','trace']:
  s=s.replace(prefix+str(old),prefix+'616')
 s=s.replace(f'choices=[{old}]','choices=[616]').replace("'"+str(old)+"'","'616'")
 return s
def write(n,s):(K/n).write_text(s,encoding='utf-8',newline='\n')
for n in ['calls.h','dib_header.h','phase.h','lifetime.h','trace_oracle.py','dib_oracle.py']:
 write(n,copy(n,610))
for n in ['serial_host.py','prepare001.py','cold002.py','vm.py','login001.py','actions002.py',
          'input_transport001.py','edition.json','media001.py','event_timestamps002.py',
          'process_review001.py']:
 write(n,copy(n,614))
vm=(K/'vm.py').read_text().replace("if time.monotonic()>=capture:","if time.monotonic()>=capture and not serial.lines.rows:")
write('vm.py',vm)
media=(K/'media001.py').read_text().replace('len(copies)==2','len(copies)==3').replace("==2\n","==3\n")
write('media001.py',media)
sam=(K.parent/'rct614/sampler.c').read_text()
def part(a,b):return sam[sam.index(a):sam.index(b)]
counter=part('typedef BOOL','#ifdef WORKER')+part('static HANDLE serialh;','void WINAPI mainCRTStartup(void)')
write('counter.h','/* MIT. Exact614 counter and bounded COM1 primitives. */\n'+counter)
trace=copy('trace.c',610)
trace=trace.replace('#include "lifetime.h"','#include "lifetime.h"\n#include "timing.h"\nstatic TIMING616 timing;')
trace=trace.replace('    if(bp[index].api) {','    if(bp[index].api) {\n        if(bp[index].api==11&&!hit616(&timing,phase_state.phase,GetTickCount()))return FALSE;')
trace=trace.replace('        bp[retindex].refs++;seen[f.api]++;',
 '''        bp[retindex].refs++;seen[f.api]++;
        if(f.api==11&&!stamp616(&timing,0,f.id,phase_state.phase,GetTickCount()))return FALSE;''')
trace=trace.replace('        returns++;','        returns++;\n        if(f.api==11&&!stamp616(&timing,1,f.id,phase_state.phase,GetTickCount()))return FALSE;')
trace=trace.replace('DWORD status,count=0,i,exitcode=99,killat=0;char cmd[]="subject616 traced";',
 'DWORD status,count=0,i,exitcode=99,killat=0;char cmd[]="subject616 1";HANDLE pf;DWORD id[4],written;FILETIME ct,et,kt,ut;')
trace=trace.replace('    process=pi.hProcess;CloseHandle(pi.hThread);started=GetTickCount();',
 '''    process=pi.hProcess;CloseHandle(pi.hThread);started=GetTickCount();
    id[0]=pi.dwProcessId;id[1]=GetCurrentProcessId();
    if(!GetProcessTimes(process,&ct,&et,&kt,&ut))failed=TRUE;
    id[2]=ct.dwLowDateTime;id[3]=ct.dwHighDateTime;
    pf=CreateFileA("C:\\\\xwn616\\\\identity.bin",GENERIC_WRITE,0,0,CREATE_NEW,FILE_FLAG_WRITE_THROUGH,0);
    if(pf==INVALID_HANDLE_VALUE)failed=TRUE;
    else {if(!WriteFile(pf,id,sizeof(id),&written,0)||written!=sizeof(id)||!FlushFileBuffers(pf))failed=TRUE;CloseHandle(pf);}
    event("COST_PID",id[0],id[1],0);event("COST_CREATED",id[2],id[3],0);''')
trace=trace.replace('    event("TOTAL",requests,returns,bp_count);',
 '''    for(i=0;i<2;i++){
        event("COST_HIT_START",i,timing.first[i],timing.hits[i]);
        event("COST_HIT_END",i,timing.last[i],timing.hits[i]);
    }
    for(i=0;i<timing.count;i++)event(timing.rows[i].kind?"COST_RETURN":"COST_CALL",timing.rows[i].id,timing.rows[i].phase,timing.rows[i].tick);
    event("TOTAL",requests,returns,bp_count);''')
write('trace.c',trace)
out.write_text(json.dumps(dict(passed=True,sources=sources,counter_source_sha256=sha(K.parent/'rct614/sampler.c'),
 scope='Original subject/counter timing identity control; no retail or physical access.'),indent=2)+'\n')
