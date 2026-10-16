"""Bounded dashboard observer only; never sends launch or writes console files."""
import importlib.util
import json
import time
from pathlib import Path
K = Path(__file__).resolve().parent
W = K.parents[1]
s = importlib.util.spec_from_file_location('inventory418', W / 'outputs/hardware-inventory418/physical.py')
m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
out = K / 'physical-return001.json'; assert not out.exists()
assert m.read(K / 'physical-launch001.json')['launch_requested']
r = dict(started_utc=m.utc(), returned=False, observations=[], launch_sent=False)
deadline = time.monotonic() + 90
while time.monotonic() < deadline:
    try:
        with m.connect(timeout=3) as f:
            entries = m.names(f, '/E')
            r.update(returned=True, ended_utc=m.utc(), trace_present='xwn-trace420.bin' in entries,
                     reports=[n for n in entries if m.REPORT.fullmatch(n)])
            break
    except Exception as exc:
        r['observations'].append(dict(utc=m.utc(), error=type(exc).__name__))
        m.write_json(out, r)
    time.sleep(5)
r.update(closed=True, ended_utc=m.utc())
m.write_json(out, r)
print(json.dumps(r, indent=2))
