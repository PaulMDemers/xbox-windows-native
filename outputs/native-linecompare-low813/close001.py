"""Close the already collected813 attempt; no console access."""
from pathlib import Path
import json, hashlib, datetime
K=Path(__file__).resolve().parent
read=lambda n:json.loads((K/n).read_text())
sha=lambda n:hashlib.sha256((K/n).read_bytes()).hexdigest()
assert read('audit002.json')['passed'] and read('photo-review001.json')['passed']
assert read('collection001.json')['completed']
r=dict(closed=True,passed=True,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
 attempt='813physical001',launch_count=1,collection_count=1,
 evidence={n:sha(n) for n in ['audit002.json','photo-review001.json','photo001.json','launch001.json','collection001.json','dashboard002.json','observation001.json']},
 console_state='authenticated UnleashX after user photograph and power off/on',
 manual_power_cycle=True,normal_windows_shutdown=False,windows_launched=False,
 owned_hook=False,owned_host_processes=[],owned_vms=[],
 CR18_before_after_restored=[255,255,255],displayed_recovery_masks=8,
 other_recovery_masks_aggregate_only=25,same_value_write_effectiveness_proved=False,
 full_mode_switch_proved=False,preserved_failure='audit001.json: stale photo_review003.py path; corrected by audit_collection002.py without recollection')
with (K/'closed001.json').open('x') as f:json.dump(r,f,indent=2);f.write('\n')
note='''# Native813 CLOSED PASS; remaining mode controls next

Native813 photo independently decoded and reviewed: CR18 FF -> FF -> FF,
eight displayed recovery masks clear; 25 other masks aggregate-only through
final status 0x813. Same-value write effectiveness remains unproved.
User reported green and back at dash after the standing photo/power-off-on
workflow. Dashboard002 authenticated; nine preparation phases collected once;
audit002 PASS. Audit001 stale photo-review filename failure is preserved.
No startup hook, Windows launch, normal Windows shutdown, or owned host VM.
Never relaunch, recollect, or runtime-parent CLOSED813.

Next: fresh kernel-context remaining mode-control qualification, starting with
CR1A (target04), then qualified native counterpart. CR25/28/2D, combined native
visible mode, and Windows handoff remain unproved. Review the pinned704 sequence
and evidence for baseline values before admitting any new writes. Source-only
reuse with pins is permitted. User renewed work tonight; automation stays PAUSED.

'''
for p in [K/'README.md',K/'NEXT.md',K.parent/'engineering-notes/CONTINUATION.md',K.parent/'engineering-notes/STATUS.md']:
 p.write_bytes(note.encode()+p.read_bytes())
print('CLOSED813 PASS; no console access')
