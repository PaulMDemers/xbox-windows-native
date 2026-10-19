"""MIT. Bounded chunked upload to one owned temporary file; no boot/hook."""
import importlib.util,json,time
from pathlib import Path
K=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('transport565',K/'controller.py');c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
c.verify();assert c.read(K/'supervisor-stage.json')['closed'];assert not (K/'launch001.json').exists()
out=K/'transport-probe001.json';assert not out.exists()
r=dict(utc=c.m.utc(),completed=False,hook_installed=False,launches=0,console_C_accessed=False)
c.m.write_json(out,r)
with c.m.connect(timeout=10) as f:
 c.startup(f,False);st=c.read(K/'stage001.json')
 assert c.m.sha(c.m.get(f,c.KIT+'/owner.json'))==st['staged'][c.KIT+'/owner.json']['sha256']
 r['partial_listing']=c.m.names(f,c.KIT+'/game');c.m.write_json(out,r)
 path=c.KIT+'/transport-probe.bin';assert c.m.get(f,path,True) is None
 data=bytes(range(256))*2048;start=time.monotonic()
 r['path']=path;r['bytes']=len(data);r['sha256']=c.m.sha(data);r['write_requested']=True;c.m.write_json(out,r)
 c.m.put(f,path,data);r['elapsed_seconds']=time.monotonic()-start;r['verified']=True;c.m.write_json(out,r)
 f.delete(path);assert c.m.get(f,path,True) is None
 r.update(completed=True,removed=True,ended_utc=c.m.utc());c.m.write_json(out,r)
print(json.dumps({n:r[n] for n in ['completed','bytes','elapsed_seconds','verified','removed']}))
