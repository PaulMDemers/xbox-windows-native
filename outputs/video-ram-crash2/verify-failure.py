"""Preserve missing-residency observer failure despite a visible completed dump."""
import hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;out=k/'crash001';read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
t=read(out/'trace.json');a=read(out/'audit.json');c=read(out/'closure.json');pre=read(out/'preflight.json');res=read(out/'residency-analysis.json')
assert t['status']=='capture_incomplete' and t['error']=="AssertionError('E14')" and t['guest_resumed'] and not t['armed_breakpoints_remaining']
assert len(t['events'])==1 and len(t['runtime_pins'])==2 and t['runtime_pins'][1]['rva']=='0x2ac4e'
for n,h in pre['sources'].items():assert sha(out/'source'/n)==h
assert c['private_disk_sha256']==a['crash_disk_sha256']==sha(Path(c['private_disk']))
assert a['integrity_passed'] and a['intent_exact'] and a['dump_header_matches'] and a['event_history_preserved'] and not a['warnings_errors'] and not a['new_events']['application']
assert not a['dump_write_evidence_passed'] and not a['dump_routine_success'] and a['alias_unchanged'] and not a['alias_writes']
assert len(res['processes'])==18 and all('absent PTE' in v.get('read_error','') for v in res['processes'])
assert len(set(v['pde'] for v in res['processes']))==1
r=dict(passed=False,failure_preserved=True,ordinary_qualified=False,physical_access=False,reason=t['error'],
 first_display_text_page_mapped=False,process_directories_checked=18,guest_resumed=True,breakpoints_removed=True,
 cold_integrity_passed=True,intended_cold_dump_header=True,runtime_dump_return_observed=False,
 visible_screen='Assistant viewed intended E058D103 cookie and physical-memory-dump-complete text.',
 screen_sha256=sha(out/'artifacts/crash.png'),audit_sha256=sha(out/'audit.json'),trace_sha256=sha(out/'trace.json'),residency_sha256=sha(out/'residency-analysis.json'),
 limits='Post-failure physical snapshot cannot replace missing before-crash observation or dump callback trace. Original full-display-text residency gate failed; no waiver or recovery boot.')
dest=k/'failure-verification.json';assert not dest.exists();dest.write_text(json.dumps(r,indent=2)+'\n');print('Second observer failure preserved; strict FALSE')
