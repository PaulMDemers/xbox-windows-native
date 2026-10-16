"""Preserve raw physical trace/report before interpretation; never relaunch."""
import importlib.util
import json
from pathlib import Path
from decode import decode
K = Path(__file__).resolve().parent
W = K.parents[1]
s = importlib.util.spec_from_file_location('inventory418', W / 'outputs/hardware-inventory418/physical.py')
m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
out = K / 'physical-collection001.json'; assert not out.exists()
assert m.read(K / 'physical-launch001.json')['launch_requested']
stage = m.read(K / 'stage001.json')
r = dict(started_utc=m.utc(), completed=False, physical_writes=False, launch_sent=False,
         console_C_accessed=False, files={}, inventory_passed=False, whole_disk_audited=False)
with m.connect() as f:
    private = Path('E:/xwn420/physical001'); private.mkdir(exist_ok=False)
    m.write_json(out, r)
    try:
        entries = m.names(f, '/E')
        selected = [n for n in entries if m.REPORT.fullmatch(n) or n.lower() == 'xwn-trace420.bin']
        for name in selected:
            data = m.get(f, '/E/' + name)
            path = private / name; path.write_bytes(data)
            row = dict(path=str(path), bytes=len(data), sha256=m.sha(data),
                       repeated_readback_exact=data == m.get(f, '/E/' + name))
            r['files'][name] = row; m.write_json(out, r)
            try:
                if name.lower() == 'xwn-trace420.bin': row['decoded'] = decode(data)
                else: row['decoded'] = m.load(path)
                row['valid'] = True
            except Exception as exc:
                row.update(valid=False, decode_error=repr(exc))
            m.write_json(out, r)
        r['trace_present'] = any(n.lower() == 'xwn-trace420.bin' for n in selected)
        r['protected_actual'] = {p: m.sha(m.get(f, p)) for p in stage['protected']}
        r['protected_mismatches'] = [p for p, h in stage['protected'].items() if r['protected_actual'][p] != h]
        r['protected_unchanged'] = not r['protected_mismatches']
        r['diagnostic_unchanged'] = m.sha(m.get(f, stage['target'])) == stage['xbe_sha256']
        r['original_utility_unchanged'] = m.sha(m.get(f, m.TARGET)) == m.EXPECTED
        r.update(completed=True, ended_utc=m.utc())
    except BaseException as exc:
        r['error'] = repr(exc)
        raise
    finally:
        m.write_json(out, r)
print(json.dumps({k: v for k, v in r.items() if k != 'protected_actual'}, indent=2))
