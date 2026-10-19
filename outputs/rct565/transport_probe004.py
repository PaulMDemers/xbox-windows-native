"""MIT. Measure small-block continuous FTP, bounded to ten seconds per transfer."""
import importlib.util,io,json,time,socket
from pathlib import Path
K=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('transport565b',K/'controller.py');c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
c.verify();assert not (K/'launch001.json').exists()
out=K/'transport-probe004.json';assert not out.exists();r=dict(utc=c.m.utc(),completed=False,launches=0,hook_installed=False)
c.m.write_json(out,r);path=c.KIT+'/transport-probe4.bin';data=bytes(range(256))*16384
f=c.m.connect(timeout=2)
try:
 c.startup(f,False);assert c.m.get(f,path,True) is None
 start=time.monotonic();r.update(path=path,bytes=len(data),write_requested=True);c.m.write_json(out,r)
 def progress(block):
  time.sleep(.001)
  if time.monotonic()-start>10:raise TimeoutError('Transfer budget')
 f.storbinary('STOR '+path,io.BytesIO(data),4096,callback=progress)
 r['elapsed_seconds']=time.monotonic()-start;r['verified']=c.m.get(f,path)==data;assert r['verified']
except Exception as e:r['error']=type(e).__name__;r['elapsed_seconds']=time.monotonic()-start
finally:f.close();c.m.write_json(out,r)
with c.m.connect(timeout=5) as f:
 c.startup(f,False)
 if c.m.get(f,path,True) is not None:f.delete(path)
 assert c.m.get(f,path,True) is None
r.update(completed=True,removed=True,ended_utc=c.m.utc());c.m.write_json(out,r);print(json.dumps(r))
