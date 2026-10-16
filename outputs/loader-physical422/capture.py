"""Preserve current mutable hives/events; require unchanged code and staging."""
import importlib.util
from pathlib import Path
K = Path(__file__).resolve().parent
W = K.parents[1]
s = importlib.util.spec_from_file_location('activate416', W / 'outputs/loader-correspondence416/activate.py')
a = importlib.util.module_from_spec(s); s.loader.exec_module(a)
out = K / 'capture001.json'; assert not out.exists()
private = Path('E:/xwn422/before001'); assert not private.exists()
q, stage = a.load()
r = dict(started_utc=a.m.utc(), completed=False, physical_writes=False,
         console_C_accessed=False, files={}, protected={}, staged={}, loader_states={})
private.mkdir(parents=True)
a.record(out, r)
try:
    with a.m.connect() as f:
        for path, old in stage['protected'].items():
            data = a.m.get(f, path); current = a.m.sha(data)
            r['protected'][path] = current
            if '/config/' in path.lower():
                dest = private / path.rsplit('/', 1)[1]; dest.write_bytes(data)
                assert data == a.m.get(f, path)
                r['files'][path] = dict(path=str(dest), sha256=current, previous_sha256=old, repeated_read_exact=True)
            else:
                assert current == old, path
        for path in ['/E/winnt/system32/config/sysevent.evt', '/E/winnt/system32/config/appevent.evt', a.m.START]:
            data = a.m.get(f, path); dest = private / path.rsplit('/', 1)[1]; dest.write_bytes(data)
            assert data == a.m.get(f, path)
            r['files'][path] = dict(path=str(dest), sha256=a.m.sha(data), repeated_read_exact=True)
        for path, v in stage['verified'].items():
            actual = a.digest(f, path); r['staged'][path] = actual
            assert actual == v['sha256'], path
        for row in q['files']:
            state = {name:a.digest(f, p) for name,p in a.paths(row).items()}
            r['loader_states'][row['relative']] = state
            assert state['active'] == row['baseline_sha256']
            assert all(state[n] is None for n in ('old', 'new', 'used'))
        r.update(completed=True, ended_utc=a.m.utc(), code_unchanged=True, staged_files_unchanged=True)
except BaseException as exc:
    r['error'] = repr(exc)
    raise
finally:
    a.record(out, r)
print('Current hives/events preserved twice; active code and inactive candidate/rollback exact')
