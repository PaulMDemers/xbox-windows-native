"""Close observer failure without interpreting an unobserved crash as success."""
import hashlib,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;out=k/'crash001';ws=k.parents[1]
sys.path.insert(0,str(ws/'work/python-packages'));import pefile
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
t=read(out/'trace.json');a=read(out/'audit.json');c=read(out/'closure.json');pre=read(out/'preflight.json')
assert t['status']=='capture_incomplete' and 'DIRECTORY_ENTRY_BASERELOC' in t['error']
assert not t['events'] and not t['runtime_pins'] and t['guest_resumed'] and not t['armed_breakpoints_remaining']
assert sha(out/'source/trace.py')==t['source_sha256']
for n,h in pre['sources'].items():assert sha(out/'source'/n)==h
p=k/'artifacts/probe.exe';pe=pefile.PE(str(p));assert not hasattr(pe,'DIRECTORY_ENTRY_BASERELOC')
assert pe.OPTIONAL_HEADER.ImageBase==4194304
assert sha(p)==read(k/'build-review.json')['binaries']['probe.exe']['sha256']
assert c['private_disk_sha256']==a['crash_disk_sha256']==sha(Path(c['private_disk']))
assert not a['integrity_passed'] and not a['allocation_passed']
allocation=read(out/'allocation.json');assert allocation['orphan_cluster_count']==12 and len(allocation['errors'])==4
assert a['event_history_preserved'] and not a['warnings_errors']
assert all(v['parsed'] for v in a['hives']) and all(v['matched'] for v in a['protected']+a['payloads'])
assert not a['dump_write_evidence_passed'] and not a['dump_routine_success'] and not a['dump_header_matches']
assert all(v['header8']==b'PAGEPAGE'.hex() for v in a['pagefiles']) and a['alias_unchanged']
assert not a['intent_exact'] and 'TRIGGER_ONCE' not in (a['intent'] or '')
before,after=[read(out/(phase+'-pagefile-map.json')) for phase in ['before','after']]
assert before['clusters']==after['clusters'] and before['requested_65536']==after['requested_65536']
r=dict(passed=False,failure_preserved=True,ordinary_qualified=False,physical_access=False,
 reason=t['error'],kernel_discovery=t['kernel_discovery'],breakpoints_removed=True,guest_resumed=True,
 fixed_image_probe_has_relocations=False,cold_integrity_passed=False,dump_observed=False,
 allocation_errors=allocation['errors'],orphan_cluster_count=12,
 intent=a['intent'],captured_screen='Assistant viewed Windows desktop with Getting Started dialog; no crash screen.',
 screen_sha256=sha(out/'artifacts/crash.png'),audit_sha256=sha(out/'audit.json'),trace_sha256=sha(out/'trace.json'),
 limits='Host observer failed before the trigger. Supervisor closed after30 seconds, before35-second trigger delay completed. No crash/handoff qualification and no relaunch of this disk.')
dest=k/'failure-verification.json';assert not dest.exists();dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
