"""Preserve current physical setup/event state read-only, without launching Windows."""
import importlib.util,json,os,datetime
from pathlib import Path
k=Path(__file__).resolve().parent;target=k/'capture.json';assert not target.exists()
spec=importlib.util.spec_from_file_location('physical_read',k.parent/'fatx0098-soak3/physical.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
r=dict(scope=__doc__,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),physical_access=True,remote_writes=False,windows_launch=False,files=[])
try:
 with m.connect() as f:
  m.owner(f)
  for name,path in [('system','/F/winnt/system32/config/system'),('software','/F/winnt/system32/config/software'),('setupapi.log','/F/winnt/setupapi.log'),('system.evt','/F/winnt/system32/config/sysevent.evt'),('application.evt','/F/winnt/system32/config/appevent.evt')]:
   dest=k/'artifacts'/name;assert not dest.exists();data=m.get(f,path);dest.write_bytes(data)
   r['files'].append(dict(path=path,local=name,bytes=len(data),sha256=m.sha(data)))
  r['completed']=True
except Exception as error:r.update(completed=False,error=repr(error));raise
finally:target.write_text(json.dumps(r,indent=2)+'\n')
print('Physical setup snapshot captured read-only')
