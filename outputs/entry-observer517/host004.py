"""Exercise actual full transaction observer; CPU/kernel/read/verification callbacks modeled."""
import hashlib,json,struct
from pathlib import Path
from contracts import plan
from indicator_calls import plan as indicator_plan,transaction
K=Path(__file__).resolve().parent;out=K/'host004.json';assert not out.exists()
build=json.loads((K.parent/'entry-colocated516/build001.json').read_text());s=build['wrapper_symbols']
x=Path('C:/xwn516/build001/default.xbe').read_bytes();assert hashlib.sha256(x).hexdigest()==build['sha256']
calls=plan(x,s);pre,post,firmret=indicator_plan(x,s);indicators={c[0]:c for c in pre+post}
class FileModel:
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

class Model(FileModel):
 def __init__(self,fail=None,mutation=None):
  super().__init__(fail,mutation);self.kind=None;self.current=None
  self.handlers.update(Entry503HalWriteSMBusValue=0x80011000,Entry503KeDelayExecutionThread=0x80012000,DiagHalReturnToFirmware=0x80013000)
 def stop(self,address,label):
  for suffix in ['-entry','-return']:
   if label.endswith(suffix) and label[:-len(suffix)] in indicators:
    self.event('stop:'+label);self.kind='indicator';self.current=indicators[label[:-len(suffix)]]
    c=self.current;assert address==(self.handlers[c[1]] if suffix=='-entry' else c[4])
    return dict(EIP=address,ESP=0x2000 if suffix=='-entry' else 0x2000+4*(len(c[3])+1),EAX=1 if self.mutation==(c[0],'status') else 0)
  if label in ['file-gate-entry','file-complete-before-indicator','firmware-return-entry']:
   self.event('stop:'+label);self.kind='boundary'
   assert address=={'file-gate-entry':s['entry498_gate'],'file-complete-before-indicator':s['entry503_complete'],'firmware-return-entry':self.handlers['DiagHalReturnToFirmware']}[label]
   return dict(EIP=address,ESP=0x3000)
  self.kind='file';return super().stop(address,label)
 def read(self,address,length,label):
  if self.kind=='file':return super().read(address,length,label)
  self.event('read:'+label)
  if label=='firmware-stack':data=struct.pack('<2I',firmret,1)
  elif label.endswith('-interval'):assert address==s['entry503_interval'];data=struct.pack('<q',-20000000)
  else:
   c=self.current;assert address==0x2000;data=struct.pack('<'+'I'*(len(c[3])+1),c[4],*c[3])
  if self.mutation==('raw',label):data=bytes([data[0]^1])+data[1:]
  assert len(data)==length;return data
 def verify_entry(self,regs):self.event('verify-entry')
 def verify_complete(self,regs):self.event('verify-complete')
 def verify_terminal(self):self.event('verify-terminal')
m=Model();result=transaction(m,s,x,calls)
assert len(result['initial'])==3 and len(result['files'])==6 and len(result['terminal'])==3
assert m.events[-1]=='verify-terminal'
expected=[f'stop:{c[0]}-{v}' for c in pre for v in ['entry','return']]+['stop:file-gate-entry']+[f'stop:{c[0]}-{v}' for c in calls for v in ['entry','return']]+['stop:file-complete-before-indicator']+[f'stop:{c[0]}-{v}' for c in post for v in ['entry','return']]+['stop:firmware-return-entry']
assert [e for e in m.events if e.startswith('stop:')]==expected
failures=0
for i in range(1,len(m.events)+1):
 q=Model(fail=i)
 try:transaction(q,s,x,calls)
 except OSError:assert q.events==m.events[:i];failures+=1
 else:raise AssertionError(i)
changes=[(c[0],'status') for c in pre+post]+[('raw',c[0]+'-stack') for c in pre+post]+[('raw',c[0]+'-interval') for c in pre+post if c[2]==99]+[('raw','firmware-stack')]
rejected=0
for change in changes:
 q=Model(mutation=change)
 try:transaction(q,s,x,calls)
 except AssertionError:rejected+=1
 else:raise AssertionError(change)
r=dict(passed=True,actual_full_observer_paths=1,transport_and_callback_failure_boundaries=failures,indicator_mutations_rejected=rejected,ordered_stops=len(expected),kernel_and_transport_modeled=True,verification_callbacks_modeled=True,physical_access=False,source_sha256={n:hashlib.sha256((K/n).read_bytes()).hexdigest() for n in ['indicator_calls.py','kernel_calls.py','contracts.py','host004.py','trace001.py']})
out.write_bytes((json.dumps(r,indent=2)+'\n').encode());print(r)
