"""New read-only physical baseline capture; no C access, writes or launch."""
import importlib.util
import json
import shutil
from pathlib import Path

K=Path(__file__).resolve().parent
W=K.parents[1]
P=Path('E:/xwn415/demo')
spec=importlib.util.spec_from_file_location('media407',W/'outputs/media-physical407/physical.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
out=K/'physical001.json'
assert not out.exists() and not P.exists()
assert shutil.disk_usage('E:/').free-64*1024**2>=20*1024**3
m.ticket()
prior=m.read(W/'outputs/demo-ready411/verification001.json')
expected={p:v for p,v in prior['verified'].items() if p.lower().startswith('/e/') and
          ('/system32/' in p.lower() or '/applications/xwneboot/' in p.lower() or '/startup/' in p.lower() or p==m.PLAYER)}
r=dict(started_utc=m.utc(),completed=False,physical_writes=False,launch_requested=False,
       console_C_accessed=False,files={},directories={})
m.write_json(out,r)
P.mkdir(parents=True)
try:
    with m.connect() as f:
        r['dashboard_ftp_available']=True
        for remote,v in expected.items():
            data=m.get(f,remote)
            dest=P/remote[3:];dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
            r['files'][remote]=dict(bytes=len(data),sha256=m.sha(data),prior411_exact=m.sha(data)==v['sha256'])
            m.write_json(out,r)
            assert m.sha(data)==v['sha256'],remote
        for remote in ['/E/Applications/XWNEBoot','/E/Applications/XWNEBoot/loader']:
            entries=m.names(f,remote)
            r['directories'][remote]=entries
            for name,v in entries.items():
                if v['directory'] or not name.lower().endswith(('.ini','.cfg','.conf')):
                    continue
                target=remote+'/'+name
                data=m.get(f,target);dest=P/target[3:]
                dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
                r['files'][target]=dict(bytes=len(data),sha256=m.sha(data),scope='Current boot configuration')
        for name in ['system','software']:
            remote='/E/winnt/system32/config/'+name
            data=m.get(f,remote);dest=P/remote[3:];dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
            r['files'][remote]=dict(bytes=len(data),sha256=m.sha(data),scope='Current registry for selected read-only comparison')
    r.update(completed=True,ended_utc=m.utc(),baseline_code_and_startup_exact=True)
except BaseException as exc:
    r['error']=repr(exc)
    raise
finally:
    m.write_json(out,r)
print(json.dumps(dict(completed=r['completed'],files=len(r['files']),writes=False,launch=False)))
