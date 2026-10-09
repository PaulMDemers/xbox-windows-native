"""Read-only cross-case review; no launch, collection, or source rewriting."""
import hashlib
import json
from pathlib import Path

k = Path(__file__).resolve().parent
ws = k.parents[1]
dest = k / 'evidence-review.json'
assert not dest.exists()
read = lambda p: json.loads(p.read_text(encoding='utf-8'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
expected = {
    'video-installer-startup173': (182,181,14,0,1,False,41),
    'video-installer-target174': (63,62,29,0,1,True,40),
    'video-installer-token175': (180,179,27,61,0,True,40),
    'video-installer-close176': (222,201,27,82,0,True,51),
}
rows = []
for name, counts in expected.items():
    kit = ws / 'outputs' / name
    case = kit / 'candidate001'
    t, v, a, c, allocation = [read(case / n) for n in
        ['trace.json','trace-verification.json','audit.json','closure.json','allocation.json']]
    actual = (len(t['events']),len(t['pins']),len(v['creation_pairs']),
        len(v.get('native_api_pairs',[])),len(v['popups']),v['diagnostic_capture_complete'],c['source_pins_checked'])
    assert actual == counts, (name,actual)
    assert c['closed'] and c['never_relaunch_or_recollect']
    assert c['audit_sha256'] == sha(case / 'audit.json')
    cleanup = ws / 'work' / 'runs' / c['run'] / 'cleanup.json'
    assert sha(cleanup) == c['cleanup_sha256']
    assert t['breakpoints_after_teardown'] == [] and t['guest_resumed'] and not t['pending_returns']
    assert not a['physical_access'] and a['debugger']
    assert a['workload_passed'] and a['integrity_passed'] and a['startup_unchanged']
    assert a['normal_shutdown_count'] == 1 and a['dashboard_return']
    assert not a['strict_events_passed'] and not a['strict_qualification_passed']
    assert not a['new_events']['application']
    assert len(a['hives']) == 5 and all(f['matched'] for f in a['files'])
    assert allocation['capture_complete'] and allocation['allocation_consistent']
    assert not allocation['errors'] and allocation['orphan_cluster_count'] == 0
    assert (allocation['directories'],allocation['files'],allocation['directory_clusters']) == (322,6721,323)
    ft = [e for e in a['warnings_errors'] if e['source'] == 'Ftdisk']
    assert len(ft) == 1 and ft[0]['event_id'] == 49 and ft[0]['type'] == 1
    assert ft[0]['strings'] == ['\\Device\\HarddiskVolume6']
    assert len(a['warnings_errors']) == 1
    assert len([e for e in a['new_events']['system'] if e['source'] == 'Application Popup']) == counts[4]
    for popup in v['popups']:
        assert popup['event_id'] == 26 and popup['type'] == 4
        assert popup['strings'] == ['rundll32.exe - DLL Initialization Failed',
            'The application failed to initialize because the window station is shutting down. ']
    frozen = read(kit / 'frozen-inputs.json')
    assert len(frozen) == counts[-1]
    for path, digest in frozen.items():
        assert sha(ws / path) == digest, path
    for source in (case / 'source').iterdir():
        assert source.read_bytes() == (kit / source.name).read_bytes()
    for n in ['pin-contract-tests.json'] if name != 'video-installer-close176' else [
        'pin-contract-tests002.json','scope-tests002.json','return-scope-tests.json']:
        test = read(kit / n)
        assert test['passed']
    rows.append(dict(kit=name,events=counts[0],resident_pins=counts[1],creation_pairs=counts[2],
        native_pairs=counts[3],popups=counts[4],capture_complete=counts[5],source_pins=counts[6],
        workload_integrity_passed=True,strict_qualification_passed=False,closed=True,
        evidence_hashes={n:sha(case/n) for n in ['trace.json','trace-verification.json','audit.json','closure.json','allocation.json']}))

# Initial scope review deliberately pins the preserved initial source, not the
# final return-selector source. Never rewrite frozen review bytes to hide this.
scope = read(k / 'api-scope-review.json')
assert scope['new_trace_sha256'] == sha(k / 'trace-before-return-scope.txt')
assert scope['new_trace_sha256'] != sha(k / 'trace.py')
old = read(k / 'pin-contract-tests.json')
assert old['pins']['trace.py'] == sha(k / 'trace-before-return-scope.txt')
old_scope = read(k / 'scope-tests.json')
assert old_scope['pins']['scope_match.py'] == sha(k / 'scope_match-before-return-scope.txt')
new = read(k / 'pin-contract-tests002.json')
assert new['pins']['trace.py'] == sha(k / 'trace.py')
for n in ['scope-tests002.json','return-scope-tests.json']:
    assert read(k / n)['pins']['scope_match.py'] == sha(k / 'scope_match.py')
race = read(k / 'candidate001/token-race-verification.json')
assert race['passed'] and not race['ordinary_qualified'] and not race['physical_qualified']
for n,digest in race['sources'].items():
    file = k / n if n == 'verify-token-race.py' else k / 'candidate001' / n
    assert sha(file) == digest
r = dict(passed=True,physical_access=False,guest_changes=False,cases=rows,
    final176_scope_provenance_verified=True,token_close_race_verified=True,
    verifier_sha256=sha(Path(__file__)),
    limits='Diagnostic timing/coverage differs across runs; strict failures remain failures, popup absence is not a fix, and no physical qualification is inferred.')
dest.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
print(json.dumps(r))
