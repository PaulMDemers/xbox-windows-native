"""Read-only verification of the exact originals and retained candidate evidence."""
from pathlib import Path
import activate as a
K = Path(__file__).resolve().parent
out = K / 'rollback-verification001.json'; assert not out.exists()
restored = a.m.read(K / 'restore001.json')
assert restored['completed'] and restored['baseline_restored']
q, stage = a.load()
r = dict(started_utc=a.m.utc(), completed=False, physical_writes=False,
         console_C_accessed=False, launch_sent=False, loader_states={})
a.record(out, r)
try:
    with a.m.connect() as f:
        for row in q['files']:
            state = {name:a.digest(f, path) for name,path in a.paths(row).items()}
            r['loader_states'][row['relative']] = state
            assert state == dict(active=row['baseline_sha256'], used=row['candidate_sha256'], old=None, new=None)
        for remote, name in [('/E/winnt/system32/config/sysevent.evt', 'sysevent.evt'),
                             ('/E/winnt/system32/config/appevent.evt', 'appevent.evt'),
                             (a.m.START, 'xwnsetup.cmd')]:
            local = Path('E:/xwn422/after001') / name
            assert a.m.get(f, remote) == local.read_bytes()
        r.update(completed=True, ended_utc=a.m.utc(), original_loaders_exact=True,
                 retained_candidates_exact=True, event_and_startup_readback_exact=True)
except BaseException as exc:
    r['error'] = repr(exc)
    raise
finally:
    a.record(out, r)
print('Original loaders and retained .422used candidates exact; event/startup readback exact')
