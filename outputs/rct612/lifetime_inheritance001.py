"""Verify actual-game observer's event loop retains610's qualified dispatch."""
import hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;Q=K.parent/'rct610'
out=K/'lifetime-inheritance001.json';assert not out.exists()
a=(Q/'trace.c').read_text();b=(K/'trace.c').read_text()
mark='while(!exited)'
expected=a[a.index(mark):];actual=b[b.index(mark):]
assert actual.replace('started>360000','started>60000')==expected
for n in ['lifetime.h','trace_oracle.py']:assert (K/n).read_bytes()==(Q/n).read_bytes()
assert json.loads((Q/'final001.json').read_text())['passed']
out.write_text(json.dumps(dict(passed=True,qualified_event_loop_sha256=hashlib.sha256(expected.encode()).hexdigest(),actual_event_loop_sha256=hashlib.sha256(actual.encode()).hexdigest(),only_loop_difference='Qualified60-second original control versus retained360-second retail deadline; no event/ownership/dispatch change.'),indent=2)+'\n')
