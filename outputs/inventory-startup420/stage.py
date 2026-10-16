"""Stage a separate emulator-tested diagnostic; never launches or overwrites."""
import importlib.util
import json
from pathlib import Path
K = Path(__file__).resolve().parent
W = K.parents[1]
spec = importlib.util.spec_from_file_location('inventory418', W / 'outputs/hardware-inventory418/physical.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
out = K / 'stage001.json'; assert not out.exists()
smoke = m.read(K / 'smoke001.json')
assert smoke['report_scope_passed'] and smoke['trace']['complete']
assert m.read(K / 'closure001.json')['exit'] == 0
assert m.read(K / 'decoder-tests001.json')['passed']
build = m.read(K / 'build001.json'); assert build['compiled'] and build['sdk_unchanged']
data = Path('E:/xwn420/build001/bin/default.xbe').read_bytes()
expected = '7347176aac86a8ea24aea4e0113680de30394fb260dfa50f0efd5f7e37a58931'
assert m.sha(data) == expected
baseline = m.read(W / 'outputs/inventory-route419/closure001.json')
assert baseline['completed'] and baseline['protected_unchanged']
target = '/E/Applications/XWNInfo420/default.xbe'
pins = {str(p.relative_to(K)): m.sha(p.read_bytes()) for p in K.iterdir() if p.is_file()}
r = dict(started_utc=m.utc(), completed=False, writes=[], launch_sent=False,
         manual_launch_pending=False, target=target, console_C_accessed=False, inputs=pins)
m.write_json(out, r)
try:
    with m.connect() as f:
        r['protected'] = m.protected(f, baseline['protected_actual'])
        assert m.sha(m.get(f, m.TARGET)) == m.EXPECTED
        apps = m.names(f, '/E/Applications'); root = m.names(f, '/E')
        assert 'xwninfo420' not in {n.lower() for n in apps}
        assert 'xwn-trace420.bin' not in {n.lower() for n in root}
        r['reports_before'] = {n: m.sha(m.get(f, '/E/' + n)) for n in root if m.REPORT.fullmatch(n)}
        r['writes'].append('/E/Applications/XWNInfo420'); m.write_json(out, r)
        f.mkd('/E/Applications/XWNInfo420')
        r['writes'].append(target); m.write_json(out, r)
        m.put(f, target, data)
        assert m.get(f, target) == data
        m.protected(f, r['protected'])
        assert m.sha(m.get(f, m.TARGET)) == m.EXPECTED
        r.update(completed=True, ended_utc=m.utc(), xbe_sha256=expected,
                 protected_unchanged=True, original_utility_unchanged=True, manual_launch_pending=True)
except BaseException as exc:
    r['error'] = repr(exc)
    raise
finally:
    m.write_json(out, r)
print(json.dumps({k: v for k, v in r.items() if k not in ('protected', 'inputs')}, indent=2))
