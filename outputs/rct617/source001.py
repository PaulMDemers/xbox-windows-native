"""Original continuously running subject: qualify phase ordering before retail."""
import hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not (K/'source001.json').exists()
pins={}
def copy(n):
 p=K.parent/'rct616'/n;pins[n]=sha(p);s=p.read_text()
 for pre in ['xwn','XWN','rct','run','RUN','subject','trace','TIMING','STAMP','hit','stamp']:
  s=s.replace(pre+'616',pre+'617')
 return s.replace('choices=[616]','choices=[617]').replace("'616'","'617'")
def put(n,s):(K/n).write_text(s,encoding='utf-8',newline='\n')
for n in ['actions002.py','cold002.py','counter.h','dib_header.h','dib_oracle.py',
 'calls.h','lifetime.h','phase.h','trace_oracle.py','serial_host.py','login001.py',
 'input_transport001.py','edition.json','prepare001.py','event_timestamps002.py',
 'process_review001.py','vm.py']:
 put(n,copy(n))
put('build001.py',copy('build002.py').replace('build002','build001'))
put('media001.py',copy('media001.py').replace('build002','build001'))
t=copy('timing.h').replace('STAMP617 rows[128];','STAMP617 rows[128];\n unsigned int hit_ticks[2][4096];')
t=t.replace('s->last[phase]=tick;s->hits[phase]++;','s->last[phase]=tick;s->hit_ticks[phase][s->hits[phase]]=tick;s->hits[phase]++;')
put('timing.h',t)
t=copy('trace.c').replace('id[0]=pi.dwProcessId;id[1]=GetCurrentProcessId();',
 'zero(&ct,sizeof(ct));id[0]=pi.dwProcessId;id[1]=GetCurrentProcessId();')
t=t.replace('DWORD status,count=0,i,exitcode=99','DWORD status,count=0,i,j,exitcode=99')
t=t.replace('event("COST_HIT_END",i,timing.last[i],timing.hits[i]);',
 '''event("COST_HIT_END",i,timing.last[i],timing.hits[i]);
        for(j=0;j<timing.hits[i];j++)event("COST_HIT",i,j,timing.hit_ticks[i][j]);''')
put('trace.c',t)
s=copy('subject.c')
s=s.replace('for(j=0;j<75;j++){','for(j=0;j<512;j++){')
s=s.replace('if(!SetEvent(ready)||WaitForSingleObject(go,30000)!=WAIT_OBJECT_0)goto finish;','if(!SetEvent(ready))goto finish;')
s=s.replace('   if(!SetEvent(request)||(!which&&!SetEvent(ack)))goto finish;','')
s=s.replace('  if(j>=35)Sleep(125);','  if(j>=35){Sleep(125);if(WaitForSingleObject(release,0)==WAIT_OBJECT_0){j++;break;}}')
s=s.replace('if(WaitForSingleObject(ack,0)!=WAIT_OBJECT_0||!SetEvent(done)||WaitForSingleObject(release,30000)!=WAIT_OBJECT_0)goto finish;',
 'if(j>=512||!SetEvent(done))goto finish;')
put('subject.c',s)
r=copy('runner.c')
r=r.replace('static SNAP sample_subject[512],sample_tracer[512];','#include "window.h"')
r=r.replace('DWORD j,n=0,id[4],got,wait,sc=99,tc=99;','DWORD j,n=0,id[4],got,sc=99,tc=99;')
r=r.replace(' SNAP a,b,ta,tb,oa,ob;BOOL ok=FALSE,identityread;NAMEFN namefn;',' BOOL ok=FALSE,identityread;NAMEFN namefn;')
r=r.replace(' zero(&ta,sizeof(ta));zero(&tb,sizeof(tb));','')
start=r.index(' if(!snap(GetCurrentProcess(),&oa,TRUE)')
end=r.index(' if(!SetEvent(ev[3])',start)
r=r[:start]+''' if(which){
  phase[0]=OpenEventA(EVENT_MODIFY_STATE,FALSE,"XWN617PhaseRequest");
  phase[1]=OpenEventA(SYNCHRONIZE,FALSE,"XWN617PhaseAck");
  if(!phase[0]||!phase[1])goto finish;
 }
 if(!window617(subject,which?pi.hProcess:0,which?phase[0]:0,which?phase[1]:0,which+1,&n))goto finish;
'''+r[end:]
put('runner.c',r)
put('source001.json',json.dumps(dict(passed=True,parent='rct616',sources=pins,
 scope='Original free-running coordination, exact counter/core ancestry; no retail or physical access.'),indent=2)+'\n')
