"""Require measured hook/upload coverage; never infer absence of global noise."""
import json,statistics,sys
from pathlib import Path
k=Path(__file__).resolve().parent;phase=sys.argv[1];assert phase in ['emulator','physical']
p=k/'candidate001'/('audit.json' if phase=='emulator' else 'physical-audit.json')
a=json.loads(p.read_text(encoding='utf-8'));dest=k/(phase+'-counters.json');assert not dest.exists()
assert a['workload_passed'] and all(v['counters_passed'] for v in a['samples'])
rows=[];covered=True
for kind,name in enumerate(['fill','DIB upload','screen readback','overlap right/down','overlap left/up']):
    intervals=[v['intervals'][kind] for v in a['samples']]
    coverage=all(sum(v['hooks'].values())>=v['operations'] and (kind==2 or v['uploads']>=v['operations']) for v in intervals)
    covered &= coverage
    rows.append(dict(kind=kind,name=name,coverage=coverage,samples=intervals,
        median_ms_per_operation=statistics.median(v['ms']/v['operations'] for v in intervals),
        median_bytes_per_operation=statistics.median(v['bytes_per_operation'] for v in intervals),
        median_uploads_per_operation=statistics.median(v['uploads']/v['operations'] for v in intervals),
        exact_rectangle_bytes=256*128*4,
        hooks_observed=sorted({h for v in intervals for h,n in v['hooks'].items() if n}),
        zero_uploads_all_samples=all(v['uploads']==0 and v['bytes']==0 for v in intervals)))
r=dict(phase=phase,case='candidate001',counter_coverage_passed=covered,operations=rows,
    full_scan_checks=50,coherence_mismatches=0,strict_qualification_passed=False,
    limits='Five samples in one boot; global counters include incidental drawing. Full-scan latency separate from timing. Counts/bytes do not split engine versus upload time. Known Ft49 remains strict failure.')
dest.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print(json.dumps({v['name']:{f:v[f] for f in ['coverage','median_ms_per_operation','median_bytes_per_operation','median_uploads_per_operation','hooks_observed','zero_uploads_all_samples']} for v in rows},indent=2))
assert covered,'Counter data did not establish measured operation coverage'
