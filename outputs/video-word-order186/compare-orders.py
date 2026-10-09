"""Compare closed185/186 records only; no replay, normalization or promotion."""
import hashlib
import json
from pathlib import Path
k = Path(__file__).resolve().parent
old = k.parent / 'video-word-runtime185'
dest = k / 'order-comparison.json'
assert not dest.exists()
read = lambda p: json.loads(p.read_text(encoding='utf-8'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
records = []
for directory, order in [(old, ['control001', 'candidate001']),
                         (k, ['candidate001', 'control001'])]:
    pair = read(directory / 'pair-review.json')
    evidence = read(directory / 'evidence-review.json')
    assert pair['scoped_display_and_cold_checks_passed'] and evidence['passed']
    assert not pair['strict_qualification_passed']
    launch_times = {name: read(directory / name / 'launch.json')['cycles'][0]
                   ['launch_requested_utc'] for name in order}
    assert launch_times[order[0]] < launch_times[order[1]]
    cases = []
    for name in ['control001', 'candidate001']:
        a = read(directory / name / 'audit.json')
        readback = [v['intervals'][2] for v in a['dib_samples']]
        durations = [loop[3] for sample in a['samples']
                     for loop in sample['timed_loops']]
        assert len(durations) == 25
        if directory == k:
            assert min(durations) >= 1500
        cases.append(dict(case=name, loop_duration_min_ms=min(durations),
                          loop_duration_max_ms=max(durations),
                          readback_row_deltas=readback,
                          readback_no_upload_rows=all(v['fast_rows'] == 0 and
                                                      v['slow_rows'] == 0
                                                      for v in readback)))
    records.append(dict(kit=directory.name, order=order, launch_times=launch_times,
                        pair_sha256=sha(directory / 'pair-review.json'),
                        evidence_sha256=sha(directory / 'evidence-review.json'),
                        timings=pair['timings'], cases=cases))

for name in ['control001', 'candidate001']:
    previous = read(old / ('fixture-' + name + '.json'))
    current = read(k / ('fixture-' + name + '.json'))
    assert previous['display_build_sha256'] == current['display_build_sha256']
assert (old / 'sites.json').read_bytes() == (k / 'sites.json').read_bytes()
rows = []
for index, before in enumerate(records[0]['timings']):
    after = records[1]['timings'][index]
    assert before['label'] == after['label']
    rows.append(dict(label=before['label'],
                     first_order_control_over_candidate=before['control_over_candidate'],
                     reverse_order_control_over_candidate=after['control_over_candidate'],
                     candidate_lower_median_both_orders=all(v['control_over_candidate'] > 1
                                                           for v in [before, after])))
r = dict(passed=True, source_sha256=sha(Path(__file__)), records=records,
         comparisons=rows, drivers_identical_between_kits=True,
         physical_qualified=False, isolated_latency_qualified=False,
         strict_qualified=False,
         limits='Descriptive medians of two separately staged ordered pairs, '
                'with five processes per case. Coarse ticks, cache/background '
                'state and emulator translation remain. Readback is a sentinel, '
                'not a correction factor. No hardware or release promotion.')
dest.write_text(json.dumps(r, indent=2) + '\n', encoding='utf-8')
print(json.dumps(dict(comparisons=rows, cases=[v['cases'] for v in records]), indent=2))
