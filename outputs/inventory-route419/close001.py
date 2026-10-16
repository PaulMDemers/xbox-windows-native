"""Read-only post-manual-reboot capture, including missing or invalid reports."""
import importlib.util
import json
from pathlib import Path

K = Path(__file__).resolve().parent
s = importlib.util.spec_from_file_location('inventory418', K.parents[1] / 'outputs/hardware-inventory418/physical.py')
m = importlib.util.module_from_spec(s)
s.loader.exec_module(m)
out = K / 'closure001.json'
assert not out.exists(), 'Closure already recorded'
stage = m.read(K / 'prepared001.json')
assert stage['completed'] and stage['manual_launch_pending']
r = dict(started_utc=m.utc(), completed=False, physical_writes=False,
         launch_requested=False, console_C_accessed=False, whole_disk_audited=False,
         user_observation='User reports manual File Explorer launch stayed black; manually restarted.',
         automatic_return_verified=False, inventory_test_passed=False,
         script_sha256=m.sha(Path(__file__).read_bytes()), reports={})
m.write_json(out, r)
try:
    with m.connect() as f:
        r['dashboard_ftp_available'] = True
        entries = m.names(f, '/E')
        r['report_listing'] = {n: row for n, row in entries.items() if m.REPORT.fullmatch(n)}
        r['new_reports'] = sorted(set(r['report_listing']) - set(stage['reports_before']))
        m.write_json(out, r)
        for n in r['report_listing']:
            data = m.get(f, '/E/' + n)
            again = m.get(f, '/E/' + n)
            dest = Path('E:/xwn419/closure001') / n
            dest.parent.mkdir(parents=True, exist_ok=True)
            with dest.open('xb') as handle:
                handle.write(data)
            row = dict(path=str(dest), bytes=len(data), sha256=m.sha(data),
                       repeated_readback_exact=(data == again))
            try:
                row['report'] = m.load(dest)
                row['schema_valid'] = True
            except Exception as exc:
                row.update(schema_valid=False, validation_error=str(exc))
            r['reports'][n] = row
            m.write_json(out, r)
        r['protected_actual'] = {p: m.sha(m.get(f, p)) for p in stage['protected']}
        r['protected_mismatches'] = [p for p, h in stage['protected'].items()
                                     if r['protected_actual'][p] != h]
        r['utility_sha256'] = m.sha(m.get(f, m.TARGET))
        r['utility_unchanged'] = r['utility_sha256'] == m.EXPECTED
        r['protected_unchanged'] = not r['protected_mismatches']
        r.update(completed=True, ended_utc=m.utc())
except BaseException as exc:
    r['error'] = repr(exc)
    raise
finally:
    m.write_json(out, r)
print(json.dumps({k: v for k, v in r.items() if k != 'protected_actual'}, indent=2))
