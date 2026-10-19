"""Read normal-startup dependencies, without changing the source installation."""
from pathlib import Path
import importlib.util,json
K=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('pair532',K.parent/'windows-pair532/controller.py')
p=importlib.util.module_from_spec(s);s.loader.exec_module(p);m=p.m
out=K/'supplement001.json';assert not out.exists()
P=Path('C:/xwn587/startup-dependency001');P.mkdir(exist_ok=False)
r={'completed':False,'writes_to_console':False,'files':{}}
try:
    with m.connect(timeout=20) as f:
        rows=m.names(f,'/E/xwndemo372');r['listing']=rows
        for name in ('display-settings.exe','outline-applied.txt'):
            assert name in rows and not rows[name]['directory'] and rows[name]['bytes']<1024*1024
            data=m.get(f,'/E/xwndemo372/'+name);assert data==m.get(f,'/E/xwndemo372/'+name)
            dest=P/name;dest.write_bytes(data)
            r['files'][name]={'path':str(dest),'bytes':len(data),'sha256':m.sha(data)}
    r['completed']=True
except BaseException as e:r['error_type']=type(e).__name__;raise
finally:out.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r))
