"""Test the actual single-request primitive with fake transport, then pin sources."""
import importlib.util,json,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
s=importlib.util.spec_from_file_location('save588',K/'controller.py');c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
P=Path('C:/xwn588/host001');assert not P.exists();P.mkdir()
cases=[]
for uncertain in (False,True):
 out=P/('uncertain.json' if uncertain else 'accepted.json')
 class Socket:
  def settimeout(self,n):assert n==20
 class FTP:
  sock=Socket();calls=0
  def sendcmd(self,command):
   self.calls+=1;assert command==c.pair.COMMAND and json.loads(out.read_text())['requested']
   if uncertain:raise TimeoutError('modeled')
   return '200 modeled'
 f=FTP();c.pair.request_once(f,out,{'ordinal':1});assert f.calls==1
 try:c.pair.request_once(f,out,{})
 except FileExistsError:pass
 else:raise AssertionError('duplicate request admitted')
 assert f.calls==1;cases.append('uncertain-no-resend' if uncertain else 'accepted-no-resend')
paths={K/'controller.py',K/'host001.py',W/'tools/e-display-policy.json',W/'outputs/demo-integration399/accepted-state.json'}
for mod in list(sys.modules.values())+[c,c.pair,c.m]:
 p=getattr(mod,'__file__',None)
 if p and Path(p).resolve().is_relative_to(W) and Path(p).suffix=='.py':paths.add(Path(p).resolve())
r=dict(passed=True,cases=cases,pins={str(p):c.m.sha(p.read_bytes()) for p in sorted(paths)},
 scope='Host request semantics only; no guest code changed or executed; no physical access.')
out=K/'host001.json';assert not out.exists();out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':True,'cases':cases,'pins':len(paths)}))
