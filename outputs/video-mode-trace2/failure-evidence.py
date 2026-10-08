"""Preserve what the incomplete virtual reference read actually returned."""
import json,hashlib
from pathlib import Path
k=Path(__file__).resolve().parent;out=k/'candidate001';dest=k/'failure-evidence.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
t=read(out/'trace.json');partial=out/'artifacts/reference-00.raw';cold=out/'artifacts/ref00.rgb'
a=partial.read_bytes();b=cold.read_bytes();assert len(a)==57344 and len(b)==393216
assert t['status']=='capture_incomplete' and len(t['events'])==0 and len(t['cursor_events'])==3
r=dict(diagnostic_passed=False,requested_bytes=393216,returned_bytes=len(a),partial_sha256=sha(partial),cold_sha256=sha(cold),
 prefix_matches_cold=a==b[:len(a)],whole_reference_complete=False,monitor_reply_preserved=False,
 unchanged_step_replies=sum(s['unchanged'] for s in t['single_steps']),
 teardown=t.get('guest_resumed') and not t.get('armed_breakpoints_remaining') and not t.get('resume_error'),
 trace_sha256=sha(out/'trace.json'),verification_sha256=sha(k/'verification.json'),verifier_sha256=sha(Path(__file__)),
 limits='Byte count/prefix comparison only. Missing HMP response and page-table evidence prevent attribution to paging, monitor transport or another cause. Never substitute this partial dump for a complete reference.')
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
