"""Exercise actual bounded store/rollback code with in-memory FTP transfer faults."""
import json,inspect,hashlib
from pathlib import Path
import physical as p
K=Path(__file__).resolve().parent;case='candidate001';p.ticket=lambda:None
normal=(K.parent/'demo-validation387/artifacts/control001-before'/p.START.lstrip('/')).read_bytes()
original=(K.parent/'demo-validation387/artifacts/control001-before'/p.FATX.lstrip('/')).read_bytes()
assert p.sha(normal)==p.fixed[p.START] and p.sha(original)==p.fixed[p.FATX]
class Fake:
 def __init__(self,fail=0,corrupt=False):self.files={};self.calls=[];self.n=0;self.fail=fail;self.corrupt=corrupt
 def storbinary(self,command,fp,block):
  verb,path=command.split(' ',1);self.calls.append(path);self.n+=1
  if self.n==self.fail:raise OSError('injected transfer failure')
  self.files[path]=(b'' if verb=='STOR' else self.files[path])+fp.read()
 def retrbinary(self,command,callback,block):
  path=command.split(' ',1)[1];data=self.files[path]
  if self.corrupt and path==p.FATX:data=data[:-1]+bytes([data[-1]^1])
  callback(data)
results=[]
for fail in range(0,8):
 f=Fake(fail);r=dict(startup_enabled=True,startup_restored=False,driver_restored=False);snap=[]
 try:p.restore_baseline(f,normal,original,case,r,lambda:snap.append(dict(r)));ok=True
 except OSError:ok=False
 assert f.calls[0]==p.START and all(n in [p.START,p.FATX] for n in f.calls)
 if fail==0:
  assert ok and r['startup_restored'] and r['driver_restored'] and f.files[p.START]==normal and f.files[p.FATX]==original
 else:
  assert not ok and not r['driver_restored']
  assert r['startup_restored']==(fail>1)
 results.append(dict(failed_transfer=fail,success=ok,startup_restored=r['startup_restored'],driver_restored=r['driver_restored']))
f=Fake(corrupt=True);r=dict(driver_restored=False)
try:p.restore_baseline(f,normal,original,case,r,lambda:None)
except AssertionError:assert r['startup_restored'] and not r['driver_restored']
else:raise AssertionError('Corrupt readback accepted')
refused=0
for path,data,c in [('/C/config.xml',b'x',case),('/F/winnt/file',b'x',case),('/E/unknown',b'x',case),(p.FATX,b'bad',case),(p.START,b'bad',case),(p.FATX,original,'control001')]:
 try:p.store(Fake(),path,data,c)
 except AssertionError:refused+=1
 else:raise AssertionError('Unowned write accepted')
source=inspect.getsource(p.collect)
assert source.index('store(f,START,normal,case)')<source.index('tested=fetch(f,FATX)')<source.index('store(f,FATX,original,case)')<source.index('for n in LOGS:')
r=dict(passed=True,scope='Actual Python FTP store/rollback with modeled server only; no physical connection',transfer_cases=results,corrupt_readback_rejected=True,path_payload_case_refusals=refused,collection_restoration_order_checked=True,physical_source_sha256=hashlib.sha256((K/'physical.py').read_bytes()).hexdigest())
dest=K/'rollback-host001.json';assert not dest.exists();dest.write_text(json.dumps(r,indent=2)+'\n');print('Rollback transfer8, corruptreadback1, writeguard6 cases pass')
