"""Compare bounded physical GDI observations, never emulator timing or drag FPS."""
import json, statistics
from pathlib import Path

k=Path(__file__).resolve().parent
baseline=k.parent/'video-trace-reuse-settled'
old=[json.loads((baseline/f'physical-cycle{i}-qualification.json').read_text()) for i in [1,2]]
new=json.loads((k/'physical-cycle1-qualification.json').read_text())
assert all(v['physical_result'] and v['passed'] for v in old)
assert new['physical_result'] and new['pixel_checks_passed'] and new['probe_passed']
assert new['expected_binaries_match'] and new['direct_ram_uc_verified']
rows=[]
for value in new['timings']:
    kind=value['kind']
    samples=[next(t['ms_per_operation'] for t in report['timings'] if t['kind']==kind) for report in old]
    current=value['ms_per_operation'];assert current>0
    rows.append(dict(operation=value['operation'],baseline_samples_ms=samples,
                     baseline_median_ms=statistics.median(samples),candidate_ms=current,
                     ratio_to_baseline_median=statistics.median(samples)/current))
report=dict(scope=__doc__,baseline_candidate='0093',candidate='0096',
            baseline_runs=2,candidate_runs=1,strict_candidate_passed=new['passed'],rows=rows,
            limits='Earlier two baseline boots versus one later candidate boot; not randomized A/B, confidence intervals, whole-window responsiveness, GPU bandwidth or long-term stability. Driver changes the access path while retaining UC; no cache-type optimization claimed.')
(k/'physical-comparison.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
