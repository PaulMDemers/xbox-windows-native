"""Own one fresh receiver and one launch. Deliberate console hold; no collection."""
import importlib.util,json,subprocess,sys,time
from pathlib import Path
K=Path(__file__).resolve().parent;P=Path('C:/xwn672')
spec=importlib.util.spec_from_file_location('physical672',K/'physical.py');d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)
out=K/'run001.json';assert not out.exists() and not (K/'launch001.json').exists()
assert d.read(K/'ready001.json')['available_to_reset']
d.session();d.verify_binary();assert d.read(K/'stage001.json')['completed']
r=dict(started_utc=d.m.utc(),launch_attempts=0,receiver_pid=None,test_hook=False,console_state='not launched',collection_owned_by_controller=False)
d.m.write_json(out,r);rx=None
try:
 verify=K/'firewall-verify001.json';assert not verify.exists()
 check=subprocess.run(['powershell','-NoProfile','-File',str(K.parents[1]/'tools/Set-XboxDiagnosticFirewall.ps1'),'-Action','Verify','-Receipt',str(verify)],capture_output=True,timeout=25)
 assert check.returncode==0 and d.read(verify)['passed'],'Persistent rule unavailable'
 with (P/'receiver001.stdout').open('xb') as stdout,(P/'receiver001.stderr').open('xb') as stderr:
  rx=subprocess.Popen([sys.executable,'-B',str(K/'listen.py')],stdout=stdout,stderr=stderr,creationflags=subprocess.CREATE_NO_WINDOW)
  r['receiver_pid']=rx.pid;d.m.write_json(out,r)
  deadline=time.monotonic()+10
  while not (P/'receiver-ready001.json').exists() and rx.poll() is None and time.monotonic()<deadline:time.sleep(.1)
  assert d.read(P/'receiver-ready001.json')['pid']==rx.pid and rx.poll() is None
  d.launch();r['launch_attempts']=1;r['console_state']='launch sent; deliberate hold expected; actual observation separate';d.m.write_json(out,r)
  print('One launch sent; receiver active; console observation and recovery are separate.',flush=True)
  try:r['receiver_exit']=rx.wait(timeout=205)
  except subprocess.TimeoutExpired:
   rx.terminate();r['receiver_exit']=rx.wait(timeout=10);r['receiver_forced_close']=True
  if (P/'capture001/summary.json').exists():r['packet_result']=d.read(P/'capture001/summary.json')['status']
except BaseException as e:r['failure']=repr(e);raise
finally:
 if rx is not None and rx.poll() is None:rx.terminate();rx.wait(timeout=10);r['receiver_forced_close']=True
 r['persistent_rule_intentionally_retained']=True;r['ended_utc']=d.m.utc();d.m.write_json(out,r)
print(r.get('packet_result','no capture summary'))
