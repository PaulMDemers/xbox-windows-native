"""Close the already-collected Test799; no console or runtime access."""
from pathlib import Path
import datetime, hashlib, json

K = Path(__file__).resolve().parent
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda n: json.loads((K / n).read_text())
assert read('audit001.json')['passed']
assert read('photo-review001.json')['passed']
assert read('collection001.json')['completed']
assert read('dashboard001.json')['authenticated']
assert read('audit001.json')['native_CR12_display_before_after_restored'] == [207, 223, 207]
assert not (K / 'closed001.json').exists()
utc = datetime.datetime.now(datetime.timezone.utc).isoformat()
record = dict(closed=True, passed=True, utc=utc,
    pins={n: sha(K/n) for n in ['audit001.json', 'photo001.json', 'photo-review001.json',
         'collection001.json', 'dashboard001.json', 'launch001.json', 'sources001.json']},
    single_launch=True, single_collection=True, hook=False,
    console='Authenticated UnleashX after standing photo-then-manual-power-cycle workflow',
    owned_host_processes=[], owned_running_vms=[], normal_windows_shutdown=False,
    native_CR12_before_after_restored=[207, 223, 207],
    displayed_recovery_masks_clear=8, omitted_masks_aggregate_only=19,
    no_relaunch_recollection_or_runtime_parent=True,
    preserved_failures=['payload006 reserve rejection; original rejected-layout001 sources retained'],
    limits=['Native result is photo-only; nine disk reports establish preparation through handoff_armed',
            'No full mode switch, Windows 1.6 desktop, acceleration, or normal shutdown proof'])
(K/'closed001.json').write_text(json.dumps(record, indent=2)+'\n', encoding='utf-8')
source = K.parent/'xcal-transaction704/gpu_legacy.c'
lines = source.read_text().splitlines()
needle = 'NvSetCrtc(pbRegs, 9, b | (((gpu->yres - 1)>> 4) & 0x20));'
line = next(i+1 for i,s in enumerate(lines) if s.strip()==needle)
assert lines[line-2].strip() == 'b = NvGetCrtc(pbRegs, 9) & 0xdf;'
plan = dict(preparation_only=True, physical_access=False,
    source=str(source.relative_to(K.parents[1])).replace('\\','/'), source_sha256=sha(source),
    source_line=line, operation=needle,
    next_attempt='Fresh kernel800 CR09 vertical-blank-start bit5 control, then independently qualified native801',
    source_only_derivation='closed798 source, with corrected model002/physical002/audit_collection003',
    baseline_CR09=96, target_formula='(saved_CR09 & 0xdf) | (((480 - 1) >> 4) & 0x20)',
    target_CR09=(96 & 0xdf) | (((480-1)>>4) & 0x20),
    expected_before_after_restored=[96,64,96],
    basis='799 audited kernel-preparation CR09 baseline and completed CR12 prefix; new actual baseline admission required',
    required=['Pin all source bytes and new attributes before staging',
              'Add actual-baseline and neighboring CRTC admission/readback checks; reverse CR09 before CR12',
              'Exercise forward mismatch, dropped write, neighbor disturbance, and restoration failures',
              'Qualify fresh layout, source, linked binary, clock, and full kernel harness before one launch',
              'Use unique owned E path; stage/readback; one SITE with 20-second reply bound',
              'Collect/audit automatic-return kernel control before native qualification'],
    new_build_stage_launch=False, closed_runtime_reuse=False)
(K/'next-control-plan001.json').write_text(json.dumps(plan, indent=2)+'\n', encoding='utf-8')
note = '''# Test799 CLOSED PASS: native CR12 display-end low byte

Photo decoded CF -> DF -> CF; all eight displayed recovery masks clear, final799
passed. Nineteen omitted masks are aggregate-only. Independent optical review
passed all416bits with352 adjacent-row checks. One accepted launch and one collection
of nine preparation reports through handoff_armed; audit001PASS exact source/build/
stage, allocation boundaries and unrelated E entries. Native result is photo-only.
Dashboard authenticated after standing photo-then-manual-power-cycle workflow.
No hook, owned host process or running VM. No normal Windows shutdown claim.
Preserve payload006 reserve rejection and rejected-layout001; no gate waiver.

Next: fresh kernel800 CR09 vertical-blank-start bit5 control from closed798 SOURCE
ONLY, exact pinned704 operation; intended60 ->40 ->60 after CR12=DF. Independently
qualify fresh harness, fault tests, bounds, linked binary and stage readback before
one automatic-return launch. Then separately qualify native801. See799/NEXT.md and
next-control-plan001.json. No800 build/stage/launch yet. All earlier attempts CLOSED;
never rerun/recollect/runtime-parent. Full mode switching and Windows1.6 remain unproved.

'''
for name in ['CONTINUATION.md','STATUS.md']:
    p=K.parent/'engineering-notes'/name
    p.write_bytes(note.encode('utf-8')+p.read_bytes())
(K/'NEXT.md').write_text('''# Test799 CLOSED PASS

One launch, one collection, independent photo review and audit001 passed.
CR12 CF -> DF -> CF; eight displayed masks clear, final799 passed; nineteen
omitted masks aggregate-only. Manual power-cycle, authenticated dashboard,
no hook or owned running process/VM. No native disk-result or Windows claim.
Do not relaunch, recollect, or reuse this runtime. Preserve rejected payload006.

Next operation is pinned704 CR09 vertical-blank-start bit5, immediately after
CR12. Fresh kernel800 should admit CR09=60 and calculate40 for yres480, then
restore its saved60 before reversing CR12 and the earlier prefix. See
next-control-plan001.json for the exact source hash/line and qualification gates.
No800 build/stage/launch has occurred. Native801 requires a separate qualified
bridge and fresh physical attempt after kernel800 collection/audit.
''', encoding='utf-8')
print(json.dumps({'closed': True, 'next_source_line': line, 'next_target_CR09': plan['target_CR09']}))
