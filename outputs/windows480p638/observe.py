"""Bounded dashboard-return observer, then one cleanup/collection call."""
import datetime,importlib.util,json,os,socket,time
from pathlib import Path
K=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('trial638_observe',K/'physical.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.session()
launch=m.read(K/'launch001.json');began=datetime.datetime.fromisoformat(launch['utc']).timestamp()
out=K/'observation001.json';assert not out.exists()
r=dict(utc=m.m.utc(),samples=[],site_requests=0,collection_requested=False)
def save():m.m.write_json(out,r)
save()
while time.time()-began<600:
 elapsed=round(time.time()-began,1)
 if elapsed<25:time.sleep(5);continue
 ready=False
 try:
  with socket.create_connection((os.environ['XWN_FTP_HOST'],21),timeout=3) as sock:
   ready=sock.recv(512).startswith(b'220')
 except OSError:pass
 r['samples'].append(dict(elapsed=elapsed,ftp_banner_ready=ready));save()
 if ready:
  r['collection_requested']=True;save()
  try:m.collect();r['collection_completed']=True
  except Exception as e:r['collection_completed']=False;r['failure_type']=type(e).__name__
  r['ended_utc']=m.m.utc();save();break
 time.sleep(15)
else:r.update(ended_utc=m.m.utc(),deadline_reached=True,console_state='FTP unavailable; actual screen unknown',owned_hook_outstanding=True);save()
