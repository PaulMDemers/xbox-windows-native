"""Fault-check the exact resume primitive without any network access."""
import hashlib,importlib.util,json,time
from pathlib import Path
K=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('resumehost',K/'recovery_stage002.py');r=importlib.util.module_from_spec(s);s.loader.exec_module(r)
expected=bytes(range(256))*800;cases=[]
class FTP:
 def __init__(self,b,fail=False):self.data=b;self.calls=[];self.fail=fail
 def storbinary(self,command,stream,block):
  assert command=='APPE /owned' and block==1024
  self.calls.append(command);self.data+=stream.read()
  if self.fail:raise TimeoutError('Uncertain append accepted, reply lost')
r.c.m.get=lambda f,n:f.data
for name in ['aligned','unaligned','already-complete','bad-prefix','changed-prefix','expired','uncertain']:
 prefix=expected[:32768 if name!='unaligned' else 32771]
 if name=='already-complete':prefix=expected
 if name=='bad-prefix':prefix=b'bad'
 f=FTP(prefix+b'changed' if name=='changed-prefix' else prefix,name=='uncertain')
 offsets=[]
 try:r.append_tail(f,'/owned',expected,prefix,time.monotonic()+(-1 if name=='expired' else 10),offsets.append);ok=True
 except (AssertionError,TimeoutError):ok=False
 assert ok==(name in ['aligned','unaligned','already-complete'])
 if ok:assert f.data==expected
 if name in ['bad-prefix','changed-prefix','expired','already-complete']:assert not f.calls
 if name=='uncertain':assert len(f.calls)==1 and f.data==expected[:65536]
 cases.append(dict(case=name,passed=True,append_calls=len(f.calls)))
out=K/'recovery-host002.json';assert not out.exists();out.write_text(json.dumps(dict(passed=True,cases=cases,source_sha256=hashlib.sha256((K/'recovery_stage002.py').read_bytes()).hexdigest(),scope='Host transport primitive only; no console access or boot proof'),indent=2)+'\n');print('Passed7 resume fault cases')
