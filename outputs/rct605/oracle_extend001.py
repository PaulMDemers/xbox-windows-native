"""Extend independent oracle for one drained phase boundary and per-phase cap."""
from pathlib import Path
K=Path(__file__).resolve().parent;p=K/'trace_oracle.py';s=p.read_text()
s=s.replace('15:1}','15:1,16:1}').replace('[14,15] else','[14,15,16] else')
s=s.replace('args={};dibs={}','args={};dibs={};phase=0;phase_rows=[];pending_rows=[];phase_ends=[];cap_phases=[]')
s=s.replace("api not in [c[0] for c in caps]","(phase if api==11 else 0,api) not in [(cp,c[0]) for cp,c in zip(cap_phases,caps)]")
s=s.replace('target=target)','target=target,phase=phase)')
s=s.replace("   assert sum(c['api']==api for c in calls.values())==32;caps.append(tuple(v))","   assert sum(c['api']==api and (api!=11 or c['phase']==phase) for c in calls.values())==32\n   caps.append(tuple(v));cap_phases.append(phase if api==11 else 0)")
s=s.replace("  elif kind=='STALE':",'''  elif kind=='PHASE_PENDING':
   old,pending,seen=v;assert phase==old==0 and not pending_rows
   assert pending==sum(len(x) for x in stacks.values()) and pending>0
   assert seen==sum(c['api']==11 for c in calls.values())
   pending_rows.append(v)
  elif kind=='PHASE':
   new,seen,skipped=v;assert phase==0 and new==1 and not phase_rows and not any(stacks.values())
   assert seen==sum(c['api']==11 for c in calls.values()) and seen<=32
   phase=1;phase_rows.append(v)
  elif kind=='PHASE_END':
   assert not any(stacks.values()) and v[0]==phase;phase_ends.append(v)
  elif kind=='STALE':''')
s=s.replace(" return dict(calls=calls,args=args,bp=bp,modules=modules,caps=caps,objects=objects,words=words,outputs=outputs,dibs=dibs)"," assert len(phase_ends)==1\n return dict(calls=calls,args=args,bp=bp,modules=modules,caps=caps,objects=objects,words=words,outputs=outputs,dibs=dibs,phase_rows=phase_rows,pending_rows=pending_rows,phase_ends=phase_ends,cap_phases=cap_phases)")
s=s.replace("[c[0] for c in r['caps']]==[3]","[c[0] for c in r['caps']]==[3,11,11] and r['cap_phases']==[0,0,1]")
s=s.replace("len(groups[4])==3 and [bool(c['result']) for _,c in groups[4]]==[False,True,True]","len(groups[4])==5 and [bool(c['result']) for _,c in groups[4]]==[False,True,True,True,True]")
s=s.replace("len(groups[11])==1 and groups[11][0][1]['result']==8","len(groups[11])==64 and all(c['result']==8 for _,c in groups[11])")
s=s.replace(' validate_headers(r)',''' validate_headers(r)
 assert len(groups[16])==1 and groups[16][0][1]['result']==0x605face0
 assert r['phase_rows']==[[1,32,4]] and r['pending_rows']==[[0,1,32]] and r['phase_ends']==[[1,4,4]]
 assert [sum(c['phase']==p for _,c in groups[11]) for p in [0,1]]==[32,32]''')
s=s.replace('header_records=len(r[\'dibs\']),','phase_rows=r[\'phase_rows\'],pending_rows=r[\'pending_rows\'],phase_ends=r[\'phase_ends\'],stretch_samples_per_phase=[32,32],header_records=len(r[\'dibs\']),')
p.write_text(s,newline='\n')
p=K/'dib_oracle.py';s=p.read_text().replace("==[4,0,0,0]","==[4]+[0]*68");p.write_text(s,newline='\n')
