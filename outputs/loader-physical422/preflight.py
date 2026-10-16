"""Read-only current-state check before the unconsumed 416 activation."""
import importlib.util
import json
from pathlib import Path
K = Path(__file__).resolve().parent
W = K.parents[1]
s = importlib.util.spec_from_file_location('activate416', W / 'outputs/loader-correspondence416/activate.py')
a = importlib.util.module_from_spec(s); s.loader.exec_module(a)
out = K / 'preflight001.json'; assert not out.exists()
assert not (a.K / 'activation001.json').exists()
assert not (a.K / 'restore001.json').exists()
q, stage = a.load()
r = dict(started_utc=a.m.utc(), completed=False, physical_writes=False,
         launch_sent=False, console_C_accessed=False, protected={}, staged={}, loader_states={})
a.record(out, r)
try:
    with a.m.connect() as f:
        for p, h in stage['protected'].items():
            actual = a.digest(f, p); r['protected'][p] = actual
            assert actual == h, p
        for p, v in stage['verified'].items():
            actual = a.digest(f, p); r['staged'][p] = actual
            assert actual == v['sha256'], p
        for row in q['files']:
            state = {name:a.digest(f, p) for name,p in a.paths(row).items()}
            r['loader_states'][row['relative']] = state
            assert state['active'] == row['baseline_sha256']
            assert all(state[n] is None for n in ('old', 'new', 'used'))
        r.update(completed=True, ended_utc=a.m.utc())
except BaseException as exc:
    r['error'] = repr(exc)
    raise
finally:
    a.record(out, r)
print('Current code, startup, registry, staged candidates and rollback names match; no writes or launch')
