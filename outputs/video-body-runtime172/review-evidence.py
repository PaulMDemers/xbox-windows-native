"""Read-only final review of closed build/host-failure/ordinary timing evidence."""
import hashlib
import json
from pathlib import Path

k = Path(__file__).resolve().parent
ws = k.parents[1]
read = lambda p: json.loads(p.read_text(encoding='utf-8'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
dest = k / 'evidence-review.json'
assert not dest.exists(), 'Review is one-shot; preserve completed evidence.'
r = dict(physical_access=False, physical_qualified=False, performance_qualified=False,
         cases=[], pins={}, failed_evidence_preserved=True)

def pin(p):
    r['pins'][p.relative_to(ws).as_posix()] = sha(p)

def frozen(kit, case):
    entries = read(kit / 'frozen-inputs.json')
    for path, digest in entries.items():
        assert sha(ws / path) == digest, path
    for p in (case / 'source').iterdir():
        assert p.read_bytes() == (kit / p.name).read_bytes(), p
    return len(entries)

def closed(kit, name):
    case = kit / name
    c = read(case / 'closure.json')
    assert c['closed'] and c['source_snapshot_exact'] and not c['ordinary_qualified']
    assert not c['physical_access'] and not c['debugger']
    assert sha(case / 'audit.json') == c['audit_sha256']
    cleanup = ws / 'work/runs' / c['run'] / 'cleanup.json'
    assert sha(cleanup) == c['cleanup_sha256']
    assert frozen(kit, case) == c['source_pins_checked']
    for p in [case / 'closure.json', case / 'audit.json', cleanup,
              case / 'launch.json', case / 'allocation.json']:
        pin(p)
    return case, c, read(case / 'audit.json')

t = k.parent / 'video-body-timing170'
h = read(t / 'host-tests.json')
assert h['passed'] and h['asan_ubsan'] and h['checks'] == 4142
for path, digest in h['pins'].items():
    assert sha(t / path) == digest
    pin(t / path)
src = read(t / 'source-review.json')
for path, digest in src['source_files'].items():
    assert sha(t / 'display' / path) == digest, path
assert sha(t / '0113-body-timing.patch') == src['patch_sha256']
d = read(t / 'driver-review.json')
assert d['passed'] and d['actual_nt5_imports_checked']
assert d['only_definition_difference'] == 'XWN_BODY_PROFILE'
definitions = []
for row in d['builds']:
    b = read(t / row['case'] / 'build.json')
    assert b['source_tree'] == d['source_tree'] == row['source_tree']
    assert sha(t / row['case'] / 'artifacts/xwnown.dll') == row['sha256'] == b['files'][0]['sha256']
    assert all(s['section'] == '.text' for s in row['resident_sites'])
    assert {'EngQueryPerformanceCounter', 'EngQueryPerformanceFrequency'} <= set(row['imports']['win32k.sys'])
    definitions.append({key: value for key, value in b['definitions'].items() if key != 'XWN_BODY_PROFILE'})
    pin(t / row['case'] / 'build.json')
assert definitions[0] == definitions[1]
failure = read(t / 'build001-integrity-failure.json')
assert not failure['compiled'] and not failure['guest_launched']
assert len(failure['mismatches']) == 3 and all(x['normalized_bytes_equal'] for x in failure['mismatches'])
assert sha(t / 'build001-expected/build-report.json') == failure['failed_build_report_sha256']
for name in ['host-tests.json', 'source-review.json', 'driver-review.json', 'build-review.json',
             'build001-integrity-failure.json', 'REPORT.md', 'NEXT.md', 'DESIGN.md', '0113-body-timing.patch']:
    pin(t / name)

old = k.parent / 'video-body-runtime171'
case, c, a = closed(old, 'control001')
assert not read(case / 'launch.json')['cycles']
assert not a['workload_passed'] and a['integrity_passed'] and not a['strict_qualification_passed']
assert all(not s['probe_passed'] and not s['timed_loops'] and not s['actual_caps'] for s in a['samples'])
assert all(not p['passed'] and not p['intervals'] for p in a['profiles'])
assert not (old / 'candidate001/launch.json').exists()
assert not (old / 'candidate001/runner-start.json').exists()
assert not (ws / 'work/runs/nt5-vbody171-candidate001').exists()
tests = read(old / 'analysis-tests.json')
assert tests['passed'] and tests['positive_modes'] == 2 and len(tests['negative_cases']) == 16
for path, digest in tests['pins'].items():
    assert sha(old / path) == digest
assert (old / 'timing_analysis.py').read_bytes() == (k / 'timing_analysis.py').read_bytes()
for name in ['REPORT.md', 'NEXT.md', 'analysis-tests.json']:
    pin(old / name)
r['cases'].append(dict(kit=old.name, case='control001', windows_launches=0,
                      workload_passed=False, integrity_passed=True, strict_passed=False,
                      frozen_closure_fixed_counts_are_planned_only=True))

contract = read(k / 'host-contract.json')
assert contract['passed'] and not contract['guest_launched']
for row in contract['checks']:
    assert row['case_values'] == ['control001', 'candidate001']
    assert sha(k / row['file']) == row['sha256']

signatures = []
for name, mode in [('control001', 0), ('candidate001', 1)]:
    case, c, a = closed(k, name)
    assert c['source_pins_checked'] == 46
    assert (c['samples'], c['copy_checks'], c['solid_checks'], c['timed_loops'], c['scanout_checks']) == (5, 20, 10, 25, 50)
    assert a['workload_passed'] and a['integrity_passed'] and a['profile_contract_passed']
    assert not any(a[key] for key in ['strict_qualification_passed', 'ordinary_qualified', 'physical_qualified', 'performance_qualified'])
    assert a['normal_shutdown_count'] == 1 and a['dashboard_return'] and a['runner_normal_restart']
    assert a['startup_unchanged'] and all(f['matched'] for f in a['files'])
    assert len(a['hives']) == 5 and all(h['parsed'] for h in a['hives'])
    launch = read(case / 'launch.json')['cycles']
    assert len(launch) == 1 and launch[0]['status'] == 'accepted' and launch[0]['dashboard_return']
    allocation = read(case / 'allocation.json')
    assert allocation['capture_complete'] and allocation['allocation_consistent']
    assert (allocation['directories'], allocation['files'], allocation['directory_clusters'], allocation['orphan_cluster_count']) == (322, 6721, 323, 0)
    assert not allocation.get('errors')
    assert len(a['profiles']) == 5
    assert all(p['passed'] and p['mode'] == mode and p['frequency'] == 1125000 and p['calibration_pairs'] == 128 for p in a['profiles'])
    assert len(a['warnings_errors']) == 1 and a['warnings_errors'][0]['source'] == 'Ftdisk' and a['warnings_errors'][0]['event_id'] == 49
    popups = [e for e in a['new_events']['system'] if e['source'] == 'Application Popup']
    assert len(popups) == 1 and popups[0]['event_id'] == 26 and popups[0]['type'] == 4
    assert popups[0]['strings'] == ['rundll32.exe - DLL Initialization Failed', 'The application failed to initialize because the window station is shutting down. ']
    assert not a['new_events']['application']
    signatures.append([{key: e[key] for key in ['source', 'event_id', 'type', 'strings', 'data_hex']} for e in a['warnings_errors'] + popups])
    r['cases'].append(dict(kit=k.name, case=name, windows_launches=1, workload_passed=True,
                          integrity_passed=True, timer_contract_passed=True, strict_passed=False))
assert signatures[0] == signatures[1]
pair = read(k / 'pair-analysis.json')
assert pair['functional_timer_contract_passed'] and not pair['strict_qualification_passed']
assert not pair['physical_qualified'] and not pair['performance_qualified']
assert 'AND enabled tick/read accounting' in pair['limits']
for name in ['host-contract.json', 'HOST-REFUSALS.md', 'INTERPRETATION.md', 'pair-analysis.json',
             'analyze-pair.py', 'review-evidence.py', 'REPORT.md', 'NEXT.md']:
    pin(k / name)
r['limits'] = 'Evidence review PASS is not strict ordinary/performance/physical qualification. Frozen narrower timing wording and planned171 counts are corrected by retained interpretation/reports; no evidence overwritten.'
r['passed'] = True
dest.write_text(json.dumps(r, indent=2) + '\n', encoding='utf-8')
print(json.dumps(r['cases']))
