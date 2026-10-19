"""MIT. Fresh bounded read-only readiness check; no console launch or mutation."""
import hashlib,importlib.util,json,shutil
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf8'))
out=K/'dashboard001.json';assert not out.exists()
assert shutil.disk_usage('C:/').free-32*1024**2>=20*1024**3
prior=read(K.parent/'rct575/final001.json');assert prior['closed'] and prior['input_qualified'] and prior['cleanup_qualified']
for n,h in prior['pins'].items():assert sha(K.parent/'rct575'/n)==h,n
assert read(K.parent/'rct565/final001.json')['closed']
spec=importlib.util.spec_from_file_location('pair576probe',K.parent/'windows-pair532/controller.py')
p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p);p.verify()
r=dict(utc=p.m.utc(),completed=False,authenticated_dashboard=False,writes=[],launch_requested=False,
       console_C_accessed=False,source_sha256=sha(Path(__file__)),pc_qualification_sha256=sha(K.parent/'rct575/final001.json'))
p.m.write_json(out,r)
try:
    with p.m.connect(timeout=10) as f:
        r['authenticated_dashboard']=True;p.m.write_json(out,r)
        p.m.baseline(f,'720p');r['protected720p_exact']=True
        r['startup_listing']=p.m.startup(f)
        rows=p.m.names(f,'/E');assert not {'xwn575','xwn575-kit'}&{n.lower() for n in rows}
        r.update(fresh_console_namespaces=True,e_root_entries=len(rows),completed=True,ended_utc=p.m.utc(),
                 physical_mode='dashboard',owned_hook_present=False,free_space_measured=False)
except BaseException as e:
    r['failure_type']=type(e).__name__;raise
finally:p.m.write_json(out,r)
print('Dashboard authenticated; protected720p/startup exact, fresh test paths unused; no writes or launch.')
