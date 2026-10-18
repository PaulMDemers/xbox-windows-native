"""Read current protected state only; no experiment, launch or remote write."""
import datetime
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

K=Path(__file__).resolve().parent
W=K.parents[1]
sys.dont_write_bytecode=True
sys.path.insert(0,str(W/'outputs/field-scanout428'))
import physical as shared

out=K/'dashboard003.json'
assert not out.exists()
r=dict(started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
       completed=False,read_only=True,remote_writes=[],launch_requested=False,
       console_C_accessed=False,source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
sys.path.insert(0,str(W/'outputs/surface-bridge260'))
from atomic_json import write_json
def save():
    write_json(out,r)
save()
try:
    with shared.connect(timeout=10) as f:
        r['dashboard_authenticated']=True
        entries=shared.names(f,shared.START)
        r['startup_listing']=entries
        r['unexpected_startup_names']=sorted(set(n.lower() for n in entries)-{'xwnsetup.cmd','desktop.ini'})
        save()
        assert not r['unexpected_startup_names'],'unexpected startup file requires ownership review'
        expected={shared.NORMAL:'da47fdf32e29b81ba9f5148d86f291ed708c9432c268b1682668c5b50883aa43',
                  shared.TARGET:'6240a801d97c4894e56d516a934059da056446fb77cf895b5364bdd6cd24be9a'}
        r['protected_hashes']={}
        for name,digest in expected.items():
            data=shared.get(f,name)
            assert data==shared.get(f,name),'protected file changed during paired read'
            h=hashlib.sha256(data).hexdigest()
            assert h==digest,name
            r['protected_hashes'][name]=h
        mode,details=shared.selector.inspect(f,shared.policy)
        assert mode=='720p'
        r['display_mode']=mode
        r['mode_inspection']=dict(launcher_bytes=len(details),launcher_sha256=hashlib.sha256(details).hexdigest(),prerequisite_pins_verified=True)
        apps=shared.names(f,'/E/Applications')
        assert 'xwndispatch528' not in {n.lower() for n in apps},'528 namespace unexpectedly present'
        r['physical528_namespace_absent']=True
        r['temporary_startup_hook_present']=False
        r['hook_removal_needed']=False
        r['console_state']='Dashboard FTP authenticated; Windows screen/power state not independently observed'
        r['completed']=True
except Exception as exc:
    r['error_type']=type(exc).__name__
    raise
finally:
    r['ended_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
    save()
print('PASS read-only dashboard/startup/launcher/720p closure; no hook or physical528 stage')
