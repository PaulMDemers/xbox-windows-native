"""Validate the recorded non-advancing step without assigning an emulator cause."""
import hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;out=k/'candidate001';dest=k/'step-evidence.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
t=read(out/'trace.json');s=t['single_steps'][-1];hit=t['last_cursor_hit'];prior=t['cursor_events'][-1]
assert t['status']=='capture_incomplete' and len(t['events'])==1 and len(t['cursor_events'])==4
assert s['before']==s['after']==hit['registers'] and s['before_owner']==s['after_owner']==hit['owner']
assert s['before']['EIP'] not in s['armed'] and hit['args']==prior['args'] and hit['args'][:2]==[1,0]
assert hit['expected_cursor']==[1,1] and hit['expected_restored']==1
pin=next(p for p in reversed(t['pins']) if p['module']=='probe.exe' and p['base']+p['rva']==s['before']['EIP'])
assert bytes.fromhex(pin['resident'])[0]==0x55 # actual pinned PUSH EBP at entry
r=dict(diagnostic_passed=False,evidence_consistent=True,registers=s['before'],owner=s['before_owner'],step_reply=s['reply'],
 removed_breakpoint_absent=True,observed_instruction='55 PUSH EBP; a retired push would change ESP/EIP',
 same_marker_args=hit['args'],expected_next=hit['expected_cursor'],trace_sha256=sha(out/'trace.json'),verifier_sha256=sha(Path(__file__)),
 limits='Observed no progress then repeated marker; no conclusion about GDB transport, pending traps or emulator root cause. No retroactive deduplication or conversion of failed run to PASS.')
dest.write_text(json.dumps(r,indent=2)+'\n');print('Pinned non-advancing PUSH EBP and repeated marker verified')
