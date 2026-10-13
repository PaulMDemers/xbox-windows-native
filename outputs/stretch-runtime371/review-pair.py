"""Join closed matched runs, preserving strict failures and negative speed evidence."""
import hashlib
import json
import statistics
import sys
from pathlib import Path

k = Path(__file__).resolve().parent
ws = k.parents[1]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text())
dest = k / 'pair-review.json'
assert not dest.exists()
sys.path.insert(0, str(k.parent / 'stretch-probe370'))
from analysis import analyze

build = read(k.parent / 'stretch-bounds369/build001.json')['cases']
diff = [n for n in build['control001']['definitions']
        if build['control001']['definitions'][n] != build['candidate001']['definitions'][n]]
assert diff == ['XWN_STRETCH_BOUNDS']
assert build['control001']['definitions']['XWN_STRETCH_BOUNDS'] == 'OFF'
assert build['candidate001']['definitions']['XWN_STRETCH_BOUNDS'] == 'ON'
records = []
all_pins = {}
for case in ('control001', 'candidate001'):
    out = k / case
    a, c, f, p, completion = [read(out / n) for n in
        ('audit.json', 'closure.json', 'fixture.json', 'preparation.json', 'audit-completion.json')]
    assert c['closed'] and sha(out / 'audit.json') == c['audit_sha256']
    assert a['scoped_combined_passed'] and a['stretch_passed'] and a['orderly_host_exit']
    assert a['normal_shutdown_count'] == 1 and a['dashboard_return']
    assert completion['completed'] and completion['existing_outputs_unchanged']
    assert p['same_never_executed_parent'] and p['hives_and_trace_unchanged']
    assert p['driver']['sha256'] == build[case]['sha256']
    frozen = read(out / 'emulator-frozen.json')
    supplemental = completion['supplemental_dependencies']
    for name, digest in {**frozen, **supplemental}.items():
        assert sha(ws / name) == digest, name
        if name in all_pins:
            assert all_pins[name] == digest, name
        all_pins[name] = digest
    samples = [analyze((out / 'artifacts' / ('sample%d' % i) / 'gdi-baseline.txt').read_text()) for i in range(5)]
    assert samples == a['stretch_samples'] and all(v['passed'] for v in samples)
    allocation = read(out / 'allocation.json')
    assert allocation['allocation_consistent'] and not allocation['errors'] and not allocation['orphan_cluster_count']
    records.append(dict(case=case, audit_sha256=sha(out / 'audit.json'),
        frozen_inputs=len(frozen), supplemental_inputs=len(supplemental),
        scoped_combined_passed=True, strict_qualification_passed=a['strict_qualification_passed'],
        warnings_errors=a['warnings_errors'], parent=f['parent'], parent_sha256=f['parent_sha256'],
        preparation=p, allocation=allocation, samples=samples))

control, candidate = records
assert control['parent'] == candidate['parent'] and control['parent_sha256'] == candidate['parent_sha256']
assert control['preparation']['changes'] == candidate['preparation']['changes']
assert control['preparation']['startup'] == candidate['preparation']['startup']
results = []
for ident in range(12):
    pair = [[sample['cases'][ident] for sample in record['samples']] for record in records]
    values = [[row['bytes'] for row in group] for group in pair]
    # Independent area arithmetic for this owned source/destination/clip design.
    area = (64*32, 48*24, 2*16*24)[ident // 4]
    minimum = area * 4 * 16
    for group in pair:
        assert all(sum(row['calls']) >= 16 and row['bytes'] >= minimum for row in group)
    results.append(dict(case=ident, geometric_minimum_bytes=minimum,
        control_bytes=values[0], candidate_bytes=values[1],
        control_calls=[row['calls'] for row in pair[0]], candidate_calls=[row['calls'] for row in pair[1]],
        control_uploads=[row['uploads'] for row in pair[0]], candidate_uploads=[row['uploads'] for row in pair[1]],
        median_byte_reduction=statistics.median(values[0])-statistics.median(values[1]),
        control_already_minimum=all(v == minimum for v in values[0]),
        candidate_at_minimum=all(v == minimum for v in values[1])))
r = dict(scoped_matched_graphics_audio_integrity_passed=True,
         actual_stretch_calls_per_run=[sum(sum(row['calls']) for s in v['samples'] for row in s['cases']) for v in records],
         byte_reduction_observed=any(v['median_byte_reduction'] > 0 for v in results),
         strict_pair_passed=all(v['strict_qualification_passed'] for v in records),
         physical_access=False, physical_qualified=False, performance_qualified=False,
         cases=results, runs=records, frozen_union_count=len(all_pins),
         limits='Five samples per sequential emulator run; global counters may include background work. Mirrored pixel reference uses driver-free GDI, not a separately implemented rasterizer. No hardware timing or ordinary desktop improvement follows.')
dest.write_text(json.dumps(r, indent=2) + '\n')
print(json.dumps({n:r[n] for n in ('scoped_matched_graphics_audio_integrity_passed', 'actual_stretch_calls_per_run', 'byte_reduction_observed', 'strict_pair_passed')}, indent=2))
