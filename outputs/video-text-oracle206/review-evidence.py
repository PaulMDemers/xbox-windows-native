"""Verify closed206 evidence and frozen inputs without console access or new runs."""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parent
workspace = root.parents[1]
read = lambda p: json.loads(p.read_text(encoding='utf-8'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
dest = root / 'evidence-review.json'
assert not dest.exists()
checked = 0

def pins(base, rows):
    global checked
    for name, digest in rows.items():
        assert sha(base / name) == digest, name
        checked += 1

pins(workspace, read(root / 'emulator-frozen.json'))
ready = read(root / 'physical-ready.json')
pins(root, ready['source_pins'])
pins(workspace, ready['input_pins'])
package = read(root / 'package-review.json')
pins(root / 'artifacts', package['helpers'])
assert sha(root / 'artifacts/gdi-probe.exe') == package['helpers']['replay.exe']
for kit in ['video-text-bounds203', 'video-text-clip205']:
    parent = root.parent / kit
    pins(parent / 'display', read(parent / 'source-review.json')['source_files'])
    assert read(parent / 'build-review.json')['passed']

cases = {}
for name in ['control001', 'candidate001']:
    out = root / name
    closure = read(out / 'closure.json')
    assert closure['closed'] and closure['scoped_display_passed'] and closure['baseline_restored']
    pins(out, closure['evidence_pins'])
    state = read(out / 'physical.json')
    for group in ['before', 'after', 'before_payloads']:
        for row in state[group].values():
            if row:
                assert sha(workspace / row['path']) == row['sha256']
                checked += 1
    assert not state['startup_enabled'] and state['baseline_restored']
    finish = read(out / 'finish-state.json')
    assert finish['closed'] and finish['status'] == 'collected_restored_audited_closed'
    assert all(v['exit_code'] == 0 for v in finish['steps'])
    cases[name] = dict(physical_closure_sha256=sha(out / 'closure.json'),
                       finish_sha256=sha(out / 'finish-state.json'))
    emu = root / ('emu-' + name)
    closed = read(emu / 'closure.json')
    assert closed['closed'] and closed['audit_sha256'] == sha(emu / 'audit.json')
    cases[name]['emulator_closure_sha256'] = sha(emu / 'closure.json')

resume = read(root / 'control001/prelaunch-resume.json')
assert resume['status'] == 'launch_recorded' and resume['alias_matches_pinned_replay']
assert resume['source_sha256'] == sha(root / 'resume-prelaunch.py')
preflight = read(root / 'candidate001/alias-preflight.json')
assert preflight['source_sha256'] == sha(root / 'launch-candidate.py')
assert preflight['alias_sha256'] == package['helpers']['replay.exe']
assert preflight['control_closure_sha256'] == sha(root / 'control001/closure.json')
assert read(root / 'physical-pair-review.json')['passed']
assert read(root / 'emulator-pair-review.json')['passed']
old = root.parent / 'video-text-runtime204'
assert read(old / 'emu-control001/closure.json')['closed']
assert not read(old / 'emu-control001/audit.json')['scoped_display_passed']
assert not (workspace / 'work/runs/nt5-text204-candidate001/launch.json').exists()
assert not (old / 'emu-candidate001/runner-start.json').exists()
assert not (old / 'emu-candidate001/launch.json').exists()

result = dict(passed=True, checked_pins=checked, cases=cases,
    manual_source_review=dict(bounds_before_eng=True, no_glyph_or_extra_walk=True,
        invalid_metadata_full_clip_fallback=True, rendering_and_existing_clip_enumeration_unchanged=True,
        per_call_actual_row_bytes=True, atomic_input_clip_and_stats=True,
        accounting_lock_never_spans_eng_or_copy=True, mode_cache_scalar_policy_unchanged=True),
    pair_pins={name:sha(root / name) for name in ['emulator-pair-review.json', 'physical-pair-review.json']},
    source_sha256=sha(Path(__file__)),
    strict_whole_boot_qualified=False, baseline_restored=True, physical_access=False,
    limits='Integrity/source review of recorded scopes. No launches, collections, new runtime tests, storage scan, release promotion or timing inference.')
dest.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
print(json.dumps(result, indent=2))
