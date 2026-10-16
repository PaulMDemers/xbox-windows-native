"""Read-only preflight for one manual File Explorer inventory comparison."""
import importlib.util
import json
from pathlib import Path

K = Path(__file__).resolve().parent
W = K.parents[1]
spec = importlib.util.spec_from_file_location('inventory418', W / 'outputs/hardware-inventory418/physical.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
out = K / 'prepared001.json'
assert not out.exists(), 'Consumed preflight; inspect actual records'
old = m.read(W / 'outputs/hardware-inventory418/closure001.json')
assert old['completed'] and old['protected_unchanged'] and not old['new_reports']
r = dict(started_utc=m.utc(), completed=False, physical_writes=False,
         launch_sent=False, target=m.TARGET, route='Manual UnleashX File Explorer',
         console_C_accessed=False, previous_attempt='418 FTP launch, black screen, manual reboot, no report')
m.write_json(out, r)
try:
    with m.connect() as f:
        r['protected'] = m.protected(f, old['protected_actual'])
        data = m.get(f, m.TARGET)
        assert m.sha(data) == m.EXPECTED
        r['xbe_sha256'] = m.sha(data)
        r['reports_before'] = {n: m.sha(m.get(f, '/E/' + n)) for n in m.names(f, '/E') if m.REPORT.fullmatch(n)}
        r.update(completed=True, ended_utc=m.utc(), manual_launch_pending=True)
except BaseException as exc:
    r['error'] = repr(exc)
    raise
finally:
    m.write_json(out, r)
print(json.dumps({k: v for k, v in r.items() if k != 'protected'}, indent=2))
