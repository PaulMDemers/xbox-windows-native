"""Bounded read-only dashboard reachability; never send SITE or collect reports."""
from pathlib import Path
import datetime,time,json,ftplib
from physical import ticket
K=Path(__file__).resolve().parent;P=Path('C:/xwn735');out=K/'dashboard001.json'
assert not out.exists() and json.loads((K/'launch001.json').read_text())['requested']
c=json.loads((P/'connection.json').read_text());r={'reachable':False,'attempts':[],'deadline_seconds':180,'physical_writes':False}
start=time.monotonic()
try:
 while time.monotonic()-start<180:
  ticket();a={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()};f=ftplib.FTP()
  try:
   f.connect(c['host'],timeout=5);f.login(c['user'],c['password']);f.cwd('/E');assert f.pwd().replace('\\','/').rstrip('/').lower()=='/e'
   a['reachable']=True;r['reachable']=True
  except Exception as e:a['failure_type']=type(e).__name__
  finally:f.close();r['attempts'].append(a)
  if r['reachable']:break
  time.sleep(min(10,max(0,180-(time.monotonic()-start))))
finally:
 r['elapsed_seconds']=time.monotonic()-start;out.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r))
