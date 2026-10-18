"""Actual finite waiter with explicitly modeled probe, clock, sleep and record sink."""
import hashlib,json
from pathlib import Path
from probe import ProbeFailure
from waiter import wait_control
K=Path(__file__).resolve().parent;out=K/'host003.json';assert not out.exists()
valid=dict(passed=True,authenticated_control=True,receipt_size=112,live_receipt_bytes_verified=False,events=[])
class Model:
 def __init__(self,success=None,record_fail=None,bad=None):self.now=0.;self.success=success;self.calls=0;self.deadlines=[];self.events=[];self.record_fail=record_fail;self.bad=bad
 def clock(self):return self.now
 def sleep(self,n):assert n<=.5;self.now+=n
 def probe(self,port,credentials,path,size,deadline):
  assert deadline<=45 and self.now<deadline;self.deadlines.append(deadline);self.calls+=1;self.now=min(deadline,self.now+.25)
  if self.calls==self.success:
   v=dict(valid)
   if self.bad:v[self.bad[0]]=self.bad[1]
   return v
  raise ProbeFailure('login',TimeoutError('model'),[])
 def record(self,row):
  self.events.append(row)
  if len(self.events)==self.record_fail:raise OSError('modeled evidence sink failure')
 def run(self):return wait_control(6076,('fixture','fixture'),'/E/Applications/XWNBoot504a/entry.bin',self.record,attempt=self.probe,clock=self.clock,sleep=self.sleep)
passed=0
for n in [1,2,5,20,60]:
 m=Model(success=n);assert m.run()==valid and m.calls==n;passed+=1
m=Model()
try:m.run()
except TimeoutError:assert m.now==45 and m.calls==60;passed+=1
else:raise AssertionError('deadline accepted')
for n in [1,2,5]:
 m=Model(record_fail=n)
 try:m.run()
 except OSError:assert m.calls==n and len(m.events)==n;passed+=1
 else:raise AssertionError('sink failure ignored')
for change in [('passed',False),('authenticated_control',False),('receipt_size',111),('live_receipt_bytes_verified',True)]:
 m=Model(success=1,bad=change)
 try:m.run()
 except AssertionError:assert m.calls==1;passed+=1
 else:raise AssertionError(change)
r=dict(passed=True,paths=passed,actual_waiter_executed=True,probe_clock_sleep_sink_modeled=True,physical_access=False,guest_access=False,sources={n:hashlib.sha256((K/n).read_bytes()).hexdigest() for n in ['waiter.py','probe.py','host003.py']})
out.write_bytes((json.dumps(r,indent=2)+'\n').encode());print(r)
