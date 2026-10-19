import importlib.util,json
from pathlib import Path
K=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('p565space',K.parent/'windows-pair532/controller.py');p=importlib.util.module_from_spec(s);s.loader.exec_module(p)
with p.m.connect(timeout=10) as f:
 r=dict(utc=p.m.utc(),cwd_reply=f.cwd('/E'),stat=f.sendcmd('STAT'))
(K/'space001.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
