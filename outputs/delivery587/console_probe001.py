"""Fresh read-only E installation inventory for private delivery; no launch."""
from pathlib import Path
import importlib.util,json
K=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('pair532',K.parent/'windows-pair532/controller.py')
p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p);m=p.m
out=K/'console-probe001.json';assert not out.exists()
r={'complete':False,'console_c_accessed':False,'launch_requested':False,'writes':False}
try:
    with m.connect() as ftp:
        r['e_roots']=m.names(ftp,'/E')
        r['startup']=m.names(ftp,m.START)
        r['launcher']=m.names(ftp,'/E/Applications/XWNEBoot')
        r['normal_startup_sha256']=m.sha(m.get(ftp,m.NORMAL))
        r['normal_target_sha256']=m.sha(m.get(ftp,m.TARGET))
        r['complete']=True
except BaseException as e:r['error_type']=type(e).__name__;raise
finally:out.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({'complete':True,'startup_entries':list(r['startup']),'launcher_entries':list(r['launcher'])}))
