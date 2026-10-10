"""Review actual closed rebalance evidence without converting a held run into PASS."""
import ast, collections, hashlib, json
from pathlib import Path
k = Path(__file__).resolve().parent
out = k / 'candidate001'
read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
b = read(k / 'build002.json')
for row in b['sources']:
    assert sha(k / row['name']) == row['sha256'], row['name']
for row in b['files']:
    assert sha(k / 'artifacts/build002' / row['name']) == row['sha256'], row['name']
assert (k / 'xwnrsc.c').read_text().replace('        /* fall through */\n', '') == (k / 'failed-build001/xwnrsc.c').read_text()
assert (k / 'compiler002.txt').read_text(encoding='utf-8-sig').split()[0] == '83015512671faaa0dbe6f043a0107f79c049f4268a67e39955388a8d9a0182e5'
br = read(k / 'build-review002.json')
assert br['passed'] and any(i['name'] == 'IoInvalidateDeviceState' for p in br['binaries'] for i in p['imports'])
assert sha(k / 'e_allocation.py') == sha(k.parent / 'halboot001/e_allocation.py')
a, p, r, t = [read(out / name) for name in ('audit.json', 'pnp-review.json', 'run.json', 'resource-trace.json')]
assert r['closed'] and r['source_unchanged']
assert a['integrity_passed'] and a['e_allocation']['allocation_consistent'] and a['e_allocation_metadata_unchanged']
lines = p['log'].splitlines()
minors = [x['profile'] for x in t['records'] if x['stage'] == 5]
counts = dict(collections.Counter(minors))
rebalance = [x for x in t['records'] if x['stage'] in (6, 7)]
runtime = bool(p['stop_cancel_qualified'] and p['cancel_remove_qualified'] and p['lifecycle_completed'] and p['hal_probe_passed'])
if runtime:
    assert all(x in lines for x in ('rebalance_disarm_ok=1', 'CANCEL_REMOVE_RECOVERED', 'remove_result=0', 'REMOVE_INTERFACE_ABSENT', 'reenumerate_result=0'))
    assert lines.count('REBALANCE_STOP_RECOVERED') == lines.count('REBALANCE_CANCEL_RECOVERED') == 1
    assert counts.get(4, 0) >= 1 and counts.get(5, 0) >= 2 and counts.get(6, 0) >= 1
    assert any(x['stage'] == 7 and x['profile'] == 5 and x['status'] == '0xc0000001' for x in rebalance)
for path in k.glob('*.py'):
    ast.parse(path.read_text(), filename=str(path))
result = dict(evidence_review_passed=True, rebalance_runtime_qualified=runtime,
    scope=__doc__, physical_access=False, closed_utc=r['closed_utc'],
    source_artifact_compiler_pins=True, resource_test_cases=read(k / 'tests002.json')['cases'],
    pnp_minor_counts=counts, diagnostic_state_and_veto_trace=rebalance,
    diagnostic_log=[x for x in lines if x.startswith(('rb_', 'rebalance_', 'REBALANCE_', 'cancel_'))],
    native_invalid_api_probe_count=lines.count('hal_export=1'),
    power_transitions=lines.count('power_status=0'), integrity_passed=True,
    normal_restart_qualified=p['normal_restart_qualified'],
    pending_setup_hold=p['restart_held_pending_setup'], probe_exit=a['logs'].get('probe-exit.txt'),
    warnings_errors=a['warnings_errors'], do_not_relaunch=True,
    evidence_sha256={name: sha(out / name) for name in ('run.json', 'audit.json', 'pnp-review.json', 'resource-trace.json')},
    limits='One fresh diagnostic emulator boot. No functional SMBus reads, terminal takeover, repeated-boot storage safety or physical qualification. Host closure is not normal shutdown.')
dest = k / 'review001.json'
assert not dest.exists()
dest.write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
