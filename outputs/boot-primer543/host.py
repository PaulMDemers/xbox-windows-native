"""MIT. Admission and exact inherited single-request contract; modeled FTP only."""
import importlib.util,json,hashlib
from pathlib import Path
K=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('primer543',K/'controller.py');c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
P=Path('C:/xwn543/host001');assert not P.exists();P.mkdir(parents=True)
cases=[]
for manual,normal in [(False,True),(True,False),(False,False)]:
 c.admit_after(dict(at_dashboard=True,user_report_received=True,manual_reset=manual,normal_windows_restart=normal));cases.append('admit_'+str((manual,normal)))
for key in ['at_dashboard','user_report_received']:
 o=dict(at_dashboard=True,user_report_received=True,manual_reset=False,normal_windows_restart=True);o[key]=False
 try:c.admit_after(o)
 except AssertionError:cases.append('reject_'+key)
 else:raise AssertionError(key)
try:c.admit_after(dict(at_dashboard=True,user_report_received=True,manual_reset=True,normal_windows_restart=True))
except AssertionError:cases.append('reject_conflicting_reset')
else:raise AssertionError('reset conflict')
for uncertain in [False,True]:
 out=P/('uncertain.json' if uncertain else 'accepted.json')
 class Socket:
  def settimeout(self,n):assert n==20
 class FTP:
  sock=Socket();calls=0
  def sendcmd(self,cmd):
   self.calls+=1;assert cmd==r'SITE EXEC E:\Applications\XWNEBoot\default.xbe'
   assert json.loads(out.read_text())['requested']
   if uncertain:raise TimeoutError('modeled')
   return '200 modeled'
 f=FTP();c.pair.request_once(f,out,{});assert f.calls==1
 try:c.pair.request_once(f,out,{})
 except FileExistsError:pass
 else:raise AssertionError('duplicate request')
 assert f.calls==1;cases.append('single_request_'+str(uncertain))
r=dict(passed=True,cases=cases,scope='Modeled FTP/evidence, no console access',controller_sha256=hashlib.sha256((K/'controller.py').read_bytes()).hexdigest())
out=K/'host001.json';assert not out.exists();out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
