"""Close the already collected 800 evidence without console or runtime access."""
from pathlib import Path
import datetime, hashlib, json
K = Path(__file__).resolve().parent
read = lambda n: json.loads((K/n).read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
a = read('audit001.json')
assert a['passed'] and read('collection001.json')['completed']
assert read('dashboard003.json')['reachable']
v = a['result']['crtc_vblank_bit']
assert [v[x] for x in ['before','after','restored']] == [96,64,96]
indices = [30,100,108,121,129,138,148,158,169,181,193,205,221,237,261,285,315,345,375,405,435,465,495,525,555,585,615,645]
assert len(a['raw_result']) == 670 and all(a['raw_result'][i] == 0 for i in indices)
assert not (K/'closed001.json').exists()
record = dict(closed=True, passed=True, utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    pins={n:sha(K/n) for n in ['audit001.json','audit-lineage001.json','collection001.json','dashboard002.json','dashboard003.json','launch001.json','sources001.json']},
    one_launch=True, one_collection=True, hook=False, owned_host_processes=[], owned_running_vms=[],
    console='Authenticated UnleashX after recorded restart request; automatic return inferred',
    CR09_before_after_restored=[96,64,96], recovery_mask_indices=indices, all_28_recovery_masks_clear=True,
    visual_result_observed=False, normal_windows_shutdown=False, full_mode_replay=False,
    preserved_failures=['Early dashboard002 connection refusal; later dashboard003 authenticated',
        'Frozen auditor expected dashboard002; separately named audit_collection002 selects dashboard003 only'],
    no_relaunch_recollection_or_runtime_parent=True)
(K/'closed001.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
note = '''# Test800 CLOSED PASS: kernel CR09 vertical-blank-start bit5

One accepted launch, one collection of seven fresh reports through restart_requested.
CR09 60 -> 40 -> 60; all 28 recovery masks clear and eight neighbors unchanged.
Audit001 passed exact frozen source/build/stage and unrelated E entries. Visual
result was not observed; automatic return inferred from restart record plus
authenticated dashboard003. Preserve early dashboard002 connection refusal and
audit-lineage001: separately named auditor selects dashboard003, no frozen edit.
No hook or owned running host process/VM. No normal Windows shutdown, full mode
switch, Windows 1.6 desktop or acceleration claim. This runtime is CLOSED.

Next: prepare fresh native801 from closed799 frontend and closed800 probe SOURCES
ONLY. Measure payload first:799 uses23416 of23424 payload bytes inside32KiB;
the new transaction/result cannot inherit that admission without new bounds.
Resolve code size/layout, then qualify direct ELF, full bridge, stack/guards,
ownership/page/CPU, optical and linked bytes before any stage or launch.
User standing watch/photo/reset authorization persists. Console1.6 .66 HDMI is
at the dashboard. No801 stage or launch. Never reopen closed runtimes.

'''
for name in ['CONTINUATION.md','STATUS.md']:
    p=K.parent/'engineering-notes'/name
    p.write_bytes(note.encode()+p.read_bytes())
(K/'NEXT.md').write_text(note,encoding='utf-8')
print('Closed800 PASS; no physical access; native801 memory qualification next')
