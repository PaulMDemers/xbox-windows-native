"""Review source deltas and raw immutable inputs before staging or boot."""
import hashlib
import json
from pathlib import Path
k = Path(__file__).resolve().parent
old = k.parent / 'video-word-runtime185'
dest = k / 'generation-review.json'
assert not dest.exists()
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
for name in ['runner.c', 'restart_gate.h', 'test-gate.c', 'xwnunused179.inf',
             'sites.json', 'artifacts/runner.exe']:
    assert (k / name).read_bytes() == (old / name).read_bytes(), name
probe = (k / 'gdi-probe.c').read_text(encoding='utf-8')
expected = (old / 'gdi-probe.c').read_text(encoding='utf-8')
expected = expected.replace('count<2000', 'count<20000')
expected = expected.replace('"XWN_GDI_PROBE_VERSION",7', '"XWN_GDI_PROBE_VERSION",8')
expected = expected.replace('XwnGdiProbeV7', 'XwnGdiProbeV8')
expected = expected.replace('scalar row stores115 - Esc cancels',
                            'scalar row stores115 longer - Esc cancels')
assert probe == expected
analysis = (k / 'sample_analysis.py').read_text(encoding='utf-8')
expected = (old / 'sample_analysis.py').read_text(encoding='utf-8')
expected = expected.replace('v7', 'v8').replace("'7','256','128'", "'8','256','128'")
expected = expected.replace('1<=v[2]<=2000 and 0<v[3]<=181000',
                            '1<=v[2]<=20000 and 1500<=v[3]<=181000')
assert analysis == expected
run = (k / 'Run.ps1').read_text(encoding='utf-8')
assert "if($Case -eq 'control001')" in run
assert "'candidate001/audit.json'" in run
assert '-Seconds 300' in run and '-GdbPort' not in run
driver = k.parent / 'video-word-store184'
review = json.loads((driver / 'driver-review.json').read_text())
pins = {}
for row in review['builds']:
    p = driver / row['case'] / 'artifacts/xwnown.dll'
    assert sha(p) == row['sha256']
    pins[row['case']] = row['sha256']
r = dict(passed=True, source_sha256=sha(Path(__file__)),
         probe_source_sha256=sha(k / 'gdi-probe.c'),
         duration_gate_source_sha256=sha(k / 'sample_analysis.py'),
         unchanged_driver_sha256=pins,
         order=['candidate001', 'control001'], measured_minimum_ms=1500,
         operation_cap=20000, guest_launch=False, physical_access=False,
         original_pixel_counter_checks_preserved=True,
         raw_guard_and_sites_bytes_identical=True,
         preserved_generation001_refusal=True)
dest.write_text(json.dumps(r, indent=2) + '\n', encoding='utf-8')
print('186 source deltas/raw pins/order reviewed before staging')
