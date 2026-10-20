"""Qualify explicit absent GDI outputs without weakening other output checks."""
import hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;S=K.parent/'rct605';out=K/'source001.json';assert not out.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();sources={}
names=['fixture.c','subject002.c','graphics002.h','dib_header.h','dib_control.h','calls.h','phase.h','phase_control.h','host_calls.c','host_dib.c','host_phase.c','trace.c','runner002.c','build002.py','binary_review001.py','media001.py','prepare001.py','cold002.py','vm.py','login001.py','actions002.py','input_transport001.py','edition.json','dib_oracle.py','event_timestamps001.py']
for n in names+['trace_oracle.py','review001.py','oracle_tests001.py','phase_oracle_tests001.py']:
 src={'trace_oracle.py':'trace_oracle002.py','review001.py':'review002.py','oracle_tests001.py':'oracle_tests002.py','phase_oracle_tests001.py':'phase_oracle_tests002.py'}.get(n,n)
 p=S/src;s=p.read_text(encoding='utf-8')
 for a,b in [('xwn605','xwn607'),('XWN605','XWN607'),('rct605','rct607'),('run605','run607'),('subject605','subject607'),('trace605','trace607'),('choices=[605]','choices=[607]'),("'605'","'607'"),('trace_oracle002','trace_oracle'),('review002.json','review001.json'),('oracle-tests002.json','oracle-tests001.json')]:s=s.replace(a,b)
 (K/n).write_text(s,encoding='utf-8',newline='\n');sources[n]=dict(source=str(p),sha256=sha(p))
p=K/'trace.c';s=p.read_text();needle='if(!address||!readmem(address,&pointer,4))return FALSE;';assert s.count(needle)==1
s=s.replace(needle,'if(f->api==4&&!address){event("OUTPUT_ABSENT",f->id,f->api,0);return !failed;}\n        '+needle);p.write_text(s,encoding='utf-8',newline='\n')
p=K/'subject002.c';s=p.read_text();needle='#include "phase_control.h"';assert needle in s;s=s.replace(needle,needle+'\n#include "null_control.h"')
needle='if(!phasecontrol605(control))InterlockedIncrement(&failures);'
assert needle in s;s=s.replace(needle,needle+'\n    if(!nullcontrol607())InterlockedIncrement(&failures);');p.write_text(s,encoding='utf-8',newline='\n')
p=K/'trace_oracle.py';s=p.read_text();needle="  elif kind=='OUTPUT':";assert s.count(needle)==1
s=s.replace(needle,"""  elif kind=='OUTPUT_ABSENT':
   ident,api,address=v;assert ident in calls and ident not in outputs and api==calls[ident]['api']==4
   assert 'result' in calls[ident] and address==args[ident][3]==0
   outputs[ident]=None
"""+needle)
s=s.replace("if api==4 and value:assert outputs[ident]","if api==4 and value and args[ident][3]:assert outputs[ident]")
s=s.replace("len(groups[4])==5 and [bool(c['result']) for _,c in groups[4]]==[False,True,True,True,True]","len(groups[4])==8 and [bool(c['result']) for _,c in groups[4]]==[False,True,True,True,True,True,True,False]")
s=s.replace("assert r['outputs'][groups[4][0][0]]==0","assert r['outputs'][groups[4][0][0]]==0\n assert all(r['outputs'][i] is None and args[i][3]==0 for i,c in groups[4][-3:])")
p.write_text(s,encoding='utf-8',newline='\n')
p=K/'dib_oracle.py';s=p.read_text();s=s.replace("assert [r['dibs'][i]['status'] for i,c in actual]==[4]+[0]*68","assert [r['dibs'][i]['status'] for i,c in actual]==[4]+[0]*68+[0,8,4]")
s=s.replace('for i,c in actual[1:]:','for i,c in actual[1:-3]:')
p.write_text(s,encoding='utf-8',newline='\n')
p=K/'review001.py';s=p.read_text().replace("PHASE605 PASS: 71 exact copies, pending request, duplicate request\\nSUBJECT601 PASS\\n","PHASE605 PASS: 71 exact copies, pending request, duplicate request\\nNULL607 PASS: RGB and masks objects, invalid header, no output pointers\\nSUBJECT601 PASS\\n")
# The source contains escaped newline text, not actual multiline literals.
s=s.replace(r"PHASE605 PASS: 71 exact copies, pending request, duplicate request\nSUBJECT601 PASS\n",r"PHASE605 PASS: 71 exact copies, pending request, duplicate request\nNULL607 PASS: RGB and masks objects, invalid header, no output pointers\nSUBJECT601 PASS\n")
p.write_text(s,encoding='utf-8',newline='\n')
(K/'.gitattributes').write_text('* -text whitespace=cr-at-eol\n')
out.write_text(json.dumps(dict(passed=True,sources=sources,physical_access=False,scope='New original NT5 absent-output control;606 failed game remains immutable.'),indent=2)+'\n')
print('607 sources prepared; actual NULL output behavior still untested')
