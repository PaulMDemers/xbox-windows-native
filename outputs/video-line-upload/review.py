"""Link the reviewed source, binary and completed ordinary evidence without a rerun."""
import hashlib
import json
from pathlib import Path

k = Path(__file__).resolve().parent
ws = k.parents[1]
read = lambda p: json.loads(p.read_text(encoding='utf-8'))

def sha(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

dest = k / 'review.json'
assert not dest.exists()
patch = read(k / 'patch-review.json')
changed = []
for name, digest in patch['source_files'].items():
    assert sha(k / 'display' / name) == digest
    if digest != patch['original_files'][name]:
        changed.append(name)
assert sorted(changed) == ['enable.c', 'shadow.c']
assert sha(k / '0110-line-upload-bounds.patch') == patch['patch_sha256']
build = read(k / 'build-report.json')
assert build['status'] == 'compiled' and build['parent_tree'] == patch['parent_tree']
assert build['patch_sha256'] == patch['patch_sha256']
binary = build['builds'][0]['files'][0]
assert sha(k / 'candidate001/artifacts' / binary['name']) == binary['sha256']
host = read(k / 'host-tests.json')
assert host['passed'] and host['cases'] == 241
for name, digest in host['pins'].items():
    assert sha(k / name) == digest
bounds = k.parent / 'video-line-bounds'
assert sha(bounds / 'bounds-evidence.json') == patch['bounds_evidence_sha256']
evidence = read(bounds / 'bounds-evidence.json')
assert evidence['bounds_evidence_verified'] and not evidence['full_diagnostic_qualified']
assert sha(bounds / 'candidate001/trace.json') == evidence['trace_sha256']
assert not read(bounds / 'verification.json')['passed']
pair = read(k.parent / 'video-line-regression/pair-review.json')
assert pair['passed'] and pair['only_display_payload_differs']
for name, digest in pair['pins'].items():
    assert sha(ws / name.replace('\\', '/')) == digest
checks = []
for kit, case in [('video-line-regression', 'control001'),
                  ('video-line-regression', 'candidate001'),
                  ('video-line-gdi', 'candidate001')]:
    root = k.parent / kit
    out = root / case
    v = read(out / 'verification.json')
    assert v['passed'] and v['ordinary_qualified'] and not v['physical_qualified']
    for name, digest in v['pins'].items():
        assert sha(out / name) == digest
    frozen = read(out / 'preflight.json')
    for name, digest in frozen['sources'].items():
        assert sha(out / 'source' / name) == digest
    if case == 'candidate001':
        assert frozen['display_sha256'] == binary['sha256']
    closure = read(out / 'closure.json')
    assert sha(Path(closure['private_disk'])) == closure['private_disk_sha256']
    run = Path(closure['private_disk']).parent
    for name, digest in closure['run_metadata_sha256'].items():
        assert sha(run / name) == digest
    checks.append(dict(kit=kit, case=case, verification_sha256=sha(out / 'verification.json'),
                       pixels=v['compared_pixels'], ordinary_passed=True))
gdi = read(k.parent / 'video-line-gdi/candidate001/verification.json')
assert len(gdi['cases']) == 26 and gdi['mode_reset']['api_success']
assert not gdi['lifecycle_qualified']
report = dict(passed=True, changed_source_files=changed, candidate_sha256=binary['sha256'],
              source_tree=build['source_tree'], actual_source_host_cases=241,
              ordinary_runs=checks, full_bounds_diagnostic_passed=False,
              bounds_intervals_verified=True, physical_access=False,
              byte_volume_only=True, no_owned_run_active=True,
              source_sha256=sha(Path(__file__)),
              limits='Closed emulator evidence only. No new physical, FPS, independent cursor pixels or surface-lifetime claim.')
dest.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
print(json.dumps(report, indent=2))
