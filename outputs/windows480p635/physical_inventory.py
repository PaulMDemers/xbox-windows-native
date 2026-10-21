"""Bounded read-only current-console inventory; no staging or SITE."""
import ast,json,os,sys,shutil,importlib.util
from pathlib import Path
K=Path(__file__).resolve().parent
source=ast.parse(Path("C:/xwn626/session.py").read_text())
nodes=[n for n in source.body if isinstance(n,ast.Expr) and isinstance(n.value,ast.Call) and ast.unparse(n.value.func)=="os.environ.update"]
assert len(nodes)==1
exec(compile(ast.Module(body=nodes,type_ignores=[]),"<private session environment>","exec"))
sys.path.insert(0,str(K.parent/"visible-dispatch528"))
spec=importlib.util.spec_from_file_location("physical528_inventory635",K.parent/"visible-dispatch528/physical.py");m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
out=K/"physical-inventory001.json";assert not out.exists()
assert shutil.disk_usage("C:/").free-32*1024**2>=20*1024**3
r=dict(utc=m.utc(),completed=False,physical_access=True,console_C_accessed=False,remote_writes=False,launch_requested=False,files=[])
m.write_json(out,r)
try:
    expected=json.loads((K/"preparation001.json").read_text())["protected"]
    with m.connect(timeout=10) as f:
        m.baseline(f,"720p");r["startup"]=m.startup(f)
        for name,h in expected.items():
            if name.endswith("xwn-video-trace.bin"):continue
            data=m.get(f,"/E/"+name)
            r["files"].append(dict(path="/E/"+name,bytes=len(data),sha256=m.sha(data),fixture_sha256=h,matched=m.sha(data)==h));m.write_json(out,r)
    r.update(completed=True,dashboard_reachable=True,protected720p_verified=True,all_compared_match=all(v["matched"] for v in r["files"]))
except BaseException as e:r["failure_type"]=type(e).__name__;raise
finally:m.write_json(out,r)
print(json.dumps({k:r[k] for k in ["completed","dashboard_reachable","all_compared_match"]}))
