"""Close the scoped physical diagnostic and retain exploratory historical timings."""
import hashlib
import json
from pathlib import Path

k = Path(__file__).resolve().parent
ws = k.parents[1]
read = lambda p: json.loads(p.read_text(encoding='utf-8'))
dest = k/'physical-summary.json'
assert not dest.exists()
a = read(k/'physical-audit.json')
h = read(k/'physical-hive-audit.json')
r = read(k/'restored-verification.json')
c = read(k.parent/'video-physical-rehearsal162/control001/audit.json')
fields = ['source', 'event_id', 'type', 'strings', 'data_hex']
same = len(a['warnings_errors']) == len(c['warnings_errors']) and all(all(x[f] == y[f] for f in fields) for x, y in zip(a['warnings_errors'], c['warnings_errors']))
historical_path = k.parent/'video-next/physical-gdi-003/qualification.json'
historical = read(historical_path)
timings = []
for v in a['timed_loops']:
    kind, count, ms = map(int, v[1:])
    before = next(x for x in historical['timings'] if x['kind'] == kind)
    per = ms/count
    timings.append(dict(kind=kind, operation=before['operation'], count=count, milliseconds=ms,
        ms_per_operation=per, historical_ms_per_operation=before['ms_per_operation'],
        historical_to_candidate_rate_ratio=before['ms_per_operation']/per))
result = dict(physical_result=True, scoped_display_diagnostic_passed=
    a['workload_passed'] and a['preserved_files_exact'] and a['deployed_payloads_exact'] and
    a['shared_acquire_success'] and h['passed'] and r['passed'] and a['event_history_preserved'] and
    same and not a['new_events']['application'] and not any(v['source'] == 'Application Popup' for v in a['new_events']['system']),
    strict_qualification_passed=False, release_qualified=False, performance_qualified=False,
    same_baseline_error_signature=same, timings=timings,
    historical_comparator_sha256=hashlib.sha256(historical_path.read_bytes()).hexdigest(),
    comparison_scope='Same v3 probe and 1024x576x32/60 caps, but a historical single baseline run, not a fresh paired timing trial; operations include GDI flush, message handling and visibility checks.',
    next_step='Fresh paired physical baseline/candidate measurements, including fill/upload regressions and repeat-run variance, before changing installed display stack.',
    owned_processes_closed=True, additional_launches_issued=0, original_display_and_system_restored=r['passed'])
dest.write_bytes((json.dumps(result, indent=2)+'\n').encode('utf-8'))
print(json.dumps(result, indent=2))
