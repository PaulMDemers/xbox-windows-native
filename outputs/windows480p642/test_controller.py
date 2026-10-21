"""No hardware: one-shot request and cleanup-order tests."""
import importlib.util,json,tempfile
from pathlib import Path
K=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('trial642',K/'physical.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class Socket:
 def settimeout(self,n):assert n==20
class FTP:
 def __init__(self,fail=False):self.sock=Socket();self.calls=[];self.fail=fail
 def sendcmd(self,command):
  self.calls.append(command);assert command==m.COMMAND
  if self.fail:raise TimeoutError('synthetic accepted/uncertain response')
  return '200 synthetic accepted'
with tempfile.TemporaryDirectory() as tmp:
 for i,fail in enumerate([False,True]):
  f=FTP(fail);p=Path(tmp)/('launch%d.json'%i);m.request_once(f,p)
  assert len(f.calls)==1 and m.read(p)['requested']
  try:m.request_once(f,p)
  except FileExistsError:pass
  else:raise AssertionError('Attempt repeated')
  assert len(f.calls)==1
assert m.HOOK_BYTES==b'@echo off\r\nC:\\xwn480p642\\probe.exe\r\nexit\r\n'
# Execute the cleanup path using a fake transport and missing result. It must
# remove its hook before any baseline reads, and never claim a probe success.
original=m.K
with tempfile.TemporaryDirectory() as tmp:
 m.K=Path(tmp);m.P=Path(tmp)/'private';m.P.mkdir()
 (m.K/'launch001.json').write_text('{"requested":true}')
 (m.K/'stage001.json').write_text('{"before":{}}')
 class C:
  def __enter__(self):return self
  def __exit__(self,*args):pass
  def delete(self,path):assert path==m.HOOK;events.append('delete');self.removed=True
  removed=False
 events=[];f=C()
 m.m.connect=lambda **kw:f
 def get(f,path,optional=False):
  events.append(('get',path))
  if path==m.HOOK:return None if f.removed else m.HOOK_BYTES
  assert f.removed
  if path in [m.PROBE+'/result.txt',m.PROBE+'/input.txt']:return None
  raise AssertionError(path)
 m.m.get=get;m.startup=lambda f:events.append('startup');m.m.baseline=lambda *a:events.append('baseline');m.protected=lambda:[]
 m.collect();r=m.read(m.K/'collection001.json')
 assert events[:3]==[('get',m.HOOK),'delete',('get',m.HOOK)]
 assert r['completed'] and r['hook_removed'] and not r['probe_present'] and not r['input_present']
 m.K=original
out=K/'host002.json';assert not out.exists()
out.write_text(json.dumps(dict(passed=True,physical_access=False,one_shot_success_and_uncertain_guard=True,hook_removed_first=True,missing_result_not_pass=True,controller_sha256=m.m.sha((K/'physical.py').read_bytes())),indent=2)+'\n')
print('642 controller host checks PASS')
