"""Create NEW200 from closed195 protocol and tested198/199; never stage or launch."""
import hashlib
import json
from pathlib import Path

k = Path(__file__).resolve().parent
ws = k.parents[1]
old = k.parent / 'video-interval-physical195'
runtime = k.parent / 'video-phase-runtime199'
driver = k.parent / 'video-phase-profile198'
read = lambda p: json.loads(p.read_text(encoding='utf-8'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert not (k / 'creation.json').exists()
assert read(runtime / 'evidence-review.json')['passed']
assert read(driver / 'driver-review.json')['passed']
for case in ['control001', 'candidate001']:
    assert read(old / case / 'closure.json')['closed']
    assert read(runtime / case / 'closure.json')['closed']
copied = []
names = ['capture.py', 'review.py', 'edit-binding.py', 'prepare-package.py',
    'physical-controller.py', 'watch-physical.py', 'finish-physical.py',
    'verify-restored.py', 'audit-physical-hives.py', 'audit-physical.py',
    'close-case.py', 'dashboard-preflight.py', 'review-physical.py',
    'interval_policy.py', 'prerequisite_policy.py', 'boundary_analysis.py',
    'runner.c', 'setup_gate.h', 'restart_gate.h',
    'test-protocol002.py', 'test-interval-policy.py', 'test-prerequisites.py', 'test-audit-boundaries.py']
for name in names:
    src = old / name
    data = src.read_bytes()
    # Keep exact proven helper/policy byte sources; only fresh kit paths in orchestrators.
    if name not in ['runner.c', 'setup_gate.h', 'restart_gate.h', 'boundary_analysis.py',
                    'interval_policy.py', 'prerequisite_policy.py']:
        data = data.replace(b'195', b'200').replace(b'video-interval-physical200', b'video-phase-physical200')
    (k / name).write_bytes(data)
    copied.append(dict(name=name, parent_sha256=sha(src), created_sha256=sha(k/name)))
for name in ['sample_analysis.py', 'dib_analysis.py', 'timing_analysis.py', 'window_analysis.py', 'gdi-probe.c']:
    (k / name).write_bytes((runtime / name).read_bytes())
    copied.append(dict(name=name, parent_sha256=sha(runtime/name), created_sha256=sha(k/name)))
art = k / 'artifacts'
art.mkdir(exist_ok=True)
for name, source in [('runner.exe', old/'artifacts/runner.exe'), ('gdi-probe.exe', runtime/'artifacts/gdi-probe.exe')]:
    (art/name).write_bytes(source.read_bytes())
assert sha(art/'runner.exe') == read(k.parent/'video-measurement-boundary194/build-review.json')['binary_sha256']
assert sha(art/'gdi-probe.exe') == read(runtime/'build-review.json')['binaries']['gdi-probe.exe']['sha256']
for name, source in [('runner.c', old/'runner.c'), ('gdi-probe.c', runtime/'gdi-probe.c')]:
    assert (k/name).read_bytes() == source.read_bytes()
for case in ['control001', 'candidate001']:
    (k/case).mkdir(exist_ok=False)
r = dict(passed=True, physical_access=False, physical_launch=False,
    runner_sha256=sha(art/'runner.exe'), probe_sha256=sha(art/'gdi-probe.exe'),
    exact194_guard=True, exact199_probe=True, scalar_stores_off_both=True,
    only_display_difference='XWN_BODY_PROFILE', copied_sources=copied,
    prerequisite199_sha256=sha(runtime/'evidence-review.json'))
(k/'creation.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
print('Created NEW200 unique namespaces; no physical write or launch')
