import importlib.util,tempfile,json
from pathlib import Path
k=Path('outputs/windows720p643');s=importlib.util.spec_from_file_location('test643',k/'physical.py');b=importlib.util.module_from_spec(s);s.loader.exec_module(b)
class S:
 def settimeout(self,n):assert n==20
class F:
 def __init__(self,fail):self.sock=S();self.fail=fail;self.calls=[]
 def sendcmd(self,cmd):
  self.calls.append(cmd);assert cmd==r'SITE EXEC E:\Applications\XWNEBoot\default.xbe'
  if self.fail:raise TimeoutError('synthetic')
  return '200 synthetic'
with tempfile.TemporaryDirectory() as d:
 for i in range(2):
  f=F(bool(i));p=Path(d)/str(i);b.request_once(f,p)
  assert len(f.calls)==1
  try:b.request_once(f,p)
  except FileExistsError:pass
  else:raise AssertionError('Repeated request')
  assert len(f.calls)==1
out=k/'host001.json';assert not out.exists();out.write_text(json.dumps(dict(passed=True,physical_access=False,accepted_and_uncertain_one_shot=True,controller_sha256=b.m.sha((k/'physical.py').read_bytes())),indent=2)+'\n');print('643 host checks PASS')
