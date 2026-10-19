import importlib.util,json
from pathlib import Path
K=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('list565',K/'controller.py');c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
c.verify();out=K/'partial-list001.json';assert not out.exists()
with c.m.connect(timeout=5) as f:
 c.startup(f,False);r=dict(utc=c.m.utc(),root=c.m.names(f,c.KIT),game=c.m.names(f,c.KIT+'/game'),writes=[])
c.m.write_json(out,r);print(json.dumps(r))
