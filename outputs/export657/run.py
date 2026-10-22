"""One admitted launch with an already-qualified, bounded owned UDP listener."""
import datetime,importlib.util,json,subprocess,sys,time
from pathlib import Path
K=Path(__file__).resolve().parent;P=Path('C:/xwn657')
spec=importlib.util.spec_from_file_location('physical657',K/'physical.py');d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)
out=K/'run001.json';assert not out.exists() and not (K/'launch001.json').exists()
fw=d.read(K/'firewall-open002.json');assert fw['passed']
assert datetime.datetime.fromisoformat(fw['expires_utc'].replace('Z','+00:00'))-datetime.datetime.now(datetime.timezone.utc)>datetime.timedelta(minutes=4)
assert not (P/'close-firewall.request').exists() and not (K/'firewall-close002.json').exists()
d.session();d.verify_binary();assert d.read(K/'stage001.json')['completed']
r=dict(started_utc=d.m.utc(),launch_attempts=0,receiver_pid=None,console_state='not launched',test_hook=False)
d.m.write_json(out,r);rx=None
try:
 # Read exact active rule, not only a historical success receipt.
 check=subprocess.run(['powershell','-NoProfile','-Command',"$ErrorActionPreference='Stop'; $c=Get-Content C:/xwn657/config.json -Raw|ConvertFrom-Json; $r=Get-NetFirewallRule -Name XWN657-owned-UDP -ErrorAction Stop; $p=$r|Get-NetFirewallPortFilter; $a=$r|Get-NetFirewallAddressFilter; $x=$r|Get-NetFirewallApplicationFilter; if($r.Enabled -ne 'True' -or $r.Action -ne 'Allow' -or $r.Direction -ne 'Inbound' -or $p.Protocol -ne 'UDP' -or $p.LocalPort -ne '50657' -or $a.RemoteAddress -ne $c.expected_peer -or $x.Program -ne 'C:\Python314\python.exe'){exit 2}"],capture_output=True,timeout=20)
 assert check.returncode==0,'Scoped firewall rule unavailable'
 with (P/'receiver.stdout').open('xb') as stdout,(P/'receiver.stderr').open('xb') as stderr:
  rx=subprocess.Popen([sys.executable,'-B',str(K/'listen.py')],stdout=stdout,stderr=stderr,creationflags=subprocess.CREATE_NO_WINDOW)
  r['receiver_pid']=rx.pid;d.m.write_json(out,r)
  deadline=time.monotonic()+10
  while not (P/'receiver-ready001.json').exists() and rx.poll() is None and time.monotonic()<deadline:time.sleep(.1)
  assert d.read(P/'receiver-ready001.json')['pid']==rx.pid and rx.poll() is None
  d.launch();r['launch_attempts']=1;r['console_state']='launch sent; outcome pending';d.m.write_json(out,r)
  print('One launch sent; receiver active.',flush=True)
  start=time.monotonic();time.sleep(15)
  while time.monotonic()-start<150:
   try:
    with d.m.connect(timeout=3) as f:d.check(f)
   except Exception:
    time.sleep(5);continue
   r['console_state']='dashboard reachable';d.m.write_json(out,r)
   d.collect();r['collection_complete']=True;print('Dashboard return collected once.',flush=True);break
  else:r['console_state']='offline at bounded observation; may be held, reset needed'
  try:r['receiver_exit']=rx.wait(timeout=125)
  except subprocess.TimeoutExpired:
   rx.terminate();r['receiver_exit']=rx.wait(timeout=10);r['receiver_forced_close']=True
  if (P/'capture001/summary.json').exists():r['packet_result']=d.read(P/'capture001/summary.json')['status']
except BaseException as e:r['failure']=repr(e);raise
finally:
 if rx is not None and rx.poll() is None:rx.terminate();rx.wait(timeout=10);r['receiver_forced_close']=True
 with (P/'close-firewall.request').open('x') as f:f.write('Close owned rule after657 observation.\n')
 r['ended_utc']=d.m.utc();d.m.write_json(out,r)
print(r['console_state'],r.get('packet_result'))
