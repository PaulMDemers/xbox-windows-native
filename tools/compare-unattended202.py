"""Descriptive physical profiling results; five samples per boot, no speedup claim."""
import hashlib
import json
import statistics
from pathlib import Path

ws = Path(__file__).resolve().parents[1]
k = ws / 'outputs/video-unattended202'
read = lambda p: json.loads(p.read_text(encoding='utf-8'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
dest = k / 'physical-comparison.json'
assert not dest.exists()
audits = {}
pins = {}
for case in ['control001', 'candidate001']:
    out = k / case
    assert read(k / ('raw-review-' + case + '.json'))['passed']
    assert read(out / 'closure.json')['closed']
    a = read(out / 'physical-audit.json')
    assert a['scoped_display_passed'] and a['warnings_are_documented_baseline_only']
    assert read(out / 'restored-verification.json')['passed']
    assert read(out / 'physical-hive-audit.json')['passed']
    assert not a['strict_qualification_passed'] and not a['strict_events_passed']
    assert len(a['samples']) == len(a['phase_samples']) == len(a['window_samples']) == 5
    audits[case] = a
    pins.update({p.relative_to(ws).as_posix(): sha(p) for p in [out / 'physical-audit.json', out / 'closure.json', k / ('raw-review-' + case + '.json')]})
assert audits['control001']['actual_caps'] == audits['candidate001']['actual_caps']
assert audits['control001']['actual_modes'] == audits['candidate001']['actual_modes']

def describe(values):
    assert len(values) == 5
    return dict(samples=values,median=statistics.median(values),minimum=min(values),maximum=max(values))

labels = ['PatBlt fill', 'DIB to screen', 'screen to DIB', 'overlap down/right', 'overlap up/left']
loops = []
for kind,label in enumerate(labels):
    rates = {}
    for case,a in audits.items():
        values = [s['intervals'][kind] for s in a['samples']]
        assert all(v['kind'] == kind and v['ms'] > 0 and v['operations'] > 0 for v in values)
        rates[case] = describe([v['operations'] * 1000 / v['ms'] for v in values])
    phases = [s['intervals'][kind] for s in audits['candidate001']['phase_samples']]
    phase_ms = {label:describe([p['elapsed_ms'][i] for p in phases]) for i,label in enumerate(phases[0]['labels'])}
    per_call_us = {}
    for i,name in enumerate(phases[0]['labels']):
        if all(p['body_calls'][i] > 0 for p in phases):
            per_call_us[name] = describe([p['elapsed_ms'][i] * 1000 / p['body_calls'][i] for p in phases])
    loops.append(dict(kind=kind,label=label,operations_per_second=rates,enabled_profiling_rate_change_percent=(rates['candidate001']['median']/rates['control001']['median']-1)*100,global_inclusive_phase_ms=phase_ms,global_phase_us_per_observed_call=per_call_us))
windows = {case:dict(wall_ms=describe([s['wall_ms'] for s in a['window_samples']]),upload_bytes=describe([s['global_bytes'] for s in a['window_samples']]),upload_calls=describe([s['global_uploads'] for s in a['window_samples']])) for case,a in audits.items()}
result = dict(passed=True,physical_observation=True,physical_access=False,performance_improvement_qualified=False,strict_qualified=False,source_sha256=sha(Path(__file__)),evidence_pins=pins,loops=loops,window_fixture=windows,actual_modes=audits['control001']['actual_modes'],limits='One OFF boot and one ON boot, five within-boot samples each. Rates include GdiFlush/messages/clipping checks; enabled-profile difference is instrumentation cost/noise, not optimization. Global phase elapsed includes background/preemption; wrapper nests copy body, so totals are not additive or exclusive CPU time. Window wall includes exact readback, not drag FPS. Calibration is direct clock queries, no calibration subtraction. Inherited whole-boot errors retained; no full storage/mode/release qualification.')
dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps({v['label']:{name:v['median'] for name,v in v['global_phase_us_per_observed_call'].items()} for v in loops},indent=2))
