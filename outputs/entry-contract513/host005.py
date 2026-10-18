"""Actual observer sequencing with explicitly modeled kernel/transport interfaces."""
import hashlib,json,struct
from pathlib import Path
from contracts import plan
from kernel_calls import observe
K=Path(__file__).resolve().parent;out=K/'host005.json';assert not out.exists()
build=json.loads((K.parent/'entry-trampoline510/build001.json').read_text());s=build['wrapper_symbols']
x=Path('C:/xwn510/build001/default.xbe').read_bytes();assert hashlib.sha256(x).hexdigest()==build['sha256']
calls=plan(x,s)
class Model:
 def __init__(self,fail=None,mutation=None):
  self.handlers={c[1]:0x80010000+c[2]*32 for c in calls};self.events=[];self.fail=fail;self.mutation=mutation;self.index=-1;self.returned=False;self.saved=[]
 def event(self,kind):
  self.events.append(kind)
  if len(self.events)==self.fail:raise OSError('modeled transport failure')
 def stop(self,address,label):
  self.event('stop:'+label)
  if label.endswith('-entry'):
   self.index+=1;self.returned=False;assert address==self.handlers[calls[self.index][1]]
   return {'ESP':0x1000,'EAX':77}
  self.returned=True;assert address==calls[self.index][4]
  return {'ESP':0x1000+4*(calls[self.index][3]+1),'EAX':1 if self.mutation==(self.index,'status') else 0}
 def record(self,row):self.event('record');self.saved.append(row.copy())
 def read(self,address,length,label):
  self.event('read:'+label);c=calls[self.index];name=c[0];h=0x100
  if address==0x1000:
   if name=='create':args=[s['entry498_handle'],0x40100000,s['entry498_object'],s['entry498_iosb'],0,0x80,0,2,0x62]
   elif name in ('body','trailer'):args=[h,0,0,0,s['entry498_iosb'],s['entry498_record'] if name=='body' else s['entry498_trailer'],96 if name=='body' else 16,0]
   elif name.startswith('flush'):args=[h,s['entry498_iosb']]
   else:args=[h]
   data=struct.pack('<'+'I'*(len(args)+1),c[4],*args)
  elif address==s['entry498_handle']:data=struct.pack('<I',h if self.returned or self.index else 0)
  elif address==s['entry498_iosb']:data=struct.pack('<II',0,2 if name=='create' else 96 if name=='body' else 16 if name=='trailer' else 0)
  elif address in (s['entry498_object'],s['entry498_name'],s['entry498_path']):data=x[address-0x10000:address-0x10000+length]
  else:raise AssertionError((address,label))
  if self.mutation==(self.index,label):data=bytes(length) if label=='create-handle-after' else bytes([data[0]^1])+data[1:]
  assert len(data)==length
  return data
m=Model();rows=observe(m,s,calls);assert len(rows)==6 and m.index==5 and m.returned
assert [e for e in m.events if e.startswith('stop:')]==[f'stop:{c[0]}-{v}' for c in calls for v in ('entry','return')]
failures=0
for n in range(1,len(m.events)+1):
 q=Model(fail=n)
 try:observe(q,s,calls)
 except OSError:assert q.events==m.events[:n];failures+=1
 else:raise AssertionError(n)
mutations=0
cases=[(i,'status') for i in range(6)]+[(i,c[0]+'-stack') for i,c in enumerate(calls)]+[(i,c[0]+'-iosb-after') for i,c in enumerate(calls) if c[0]!='close']+[(0,n) for n in ('object','name','path','create-handle-after')]
for change in cases:
 q=Model(mutation=change)
 try:observe(q,s,calls)
 except AssertionError:mutations+=1
 else:raise AssertionError(('mutation survived',change))
r=dict(passed=True,actual_observer_success_paths=1,transport_failure_boundaries=failures,mutations_rejected=mutations,model_events=len(m.events),kernel_and_transport_modeled=True,physical_access=False,source_sha256={n:hashlib.sha256((K/n).read_bytes()).hexdigest() for n in ['kernel_calls.py','contracts.py','host005.py']})
out.write_bytes((json.dumps(r,indent=2)+'\n').encode());print(r)
