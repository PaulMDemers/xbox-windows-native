"""Require exact pixels and real scalar coverage; retain raw fixed-work timing."""
import statistics
from common import *
physical='--physical' in sys.argv
dest=k/('physical-pair-review.json' if physical else 'emulator-pair-review.json');assert not dest.exists()
cases={};pins={}
for case in ['control001','candidate001']:
 out=k/(case if physical else 'emu-'+case)
 a=read(out/('physical-audit.json' if physical else 'audit.json'));c=read(out/'closure.json')
 assert c['closed'] and a['scoped_display_passed'] and a['dashboard_return'] and a['normal_shutdown_count']==1
 assert not a['new_events']['application']
 assert [(v['source'],v['event_id']) for v in a['warnings_errors']]==[('Ftdisk',49)]
 assert not a['strict_qualification_passed']
 if physical:
  assert c['baseline_restored'] and not c['startup_enabled']
  assert a['physical_result'] and a['warnings_are_documented_baseline_only'] and not a['strict_error_waiver']
  assert read(out/'physical-hive-audit.json')['passed'] and read(out/'restored-verification.json')['passed']
  for p,h in c['evidence_pins'].items():assert sha(out/p)==h
 else:assert a['integrity_passed'] and not a['debugger'] and not a['physical_access']
 group=a['row_samples' if physical else 'dib_samples'];assert len(group)==5 and all(v['passed'] for v in group)
 assert all(v['passed'] and len(v['cases'])==13 for v in a['text_samples'])
 assert all(v['passed'] and v['moves']==40 and v['exact_readbacks']==40 for v in a['window_samples'])
 assert a['boundary_analysis']['helper']['targets']==([1,2,3,4] if physical else [1,2,5])
 cases[case]=a;pins[case]={'audit_sha256':sha(out/('physical-audit.json' if physical else 'audit.json')),'closure_sha256':sha(out/'closure.json')}
a,b=[cases[c] for c in ['control001','candidate001']]
assert a['actual_caps']==b['actual_caps'] and a['actual_modes']==b['actual_modes']
for i in range(13):
 values=[q['cases'][i] for r in [a,b] for q in r['text_samples']]
 for field in ['changed_pixels','guard_pixels','calls','glyphs','client','origin','bounds','input_clip','clip_complexity','copied_bytes']:
  assert all(v[field]==values[0][field] for v in values),(i,field)
operations=[]
for kind,name in enumerate(['fill','DIB upload','unchanged readback','overlap right/down','overlap left/up']):
 series=[]
 for r in [a,b]:
  vals=[s['timed_loops'][kind] for s in r['samples']]
  assert len(vals)==5 and all(v[1]==kind and 1<=v[2]<=20000 and 1500<=v[3]<=181000 for v in vals)
  series.append([dict(count=v[2],milliseconds=v[3],ms_per_operation=v[3]/v[2]) for v in vals])
 left,right=[[v['ms_per_operation'] for v in q] for q in series];x,y=map(statistics.median,[left,right])
 operations.append(dict(operation=name,control_samples=series[0],candidate_samples=series[1],control_median_ms=x,candidate_median_ms=y,
  elapsed_reduction_percent=100*(1-y/x),control_range_ms=[min(left),max(left)],candidate_range_ms=[min(right),max(right)]))
save(dest,dict(passed=True,actual_scalar_coverage_passed=True,physical_testing_ready=not physical,physical_result=physical,
 operations=operations,cases=pins,actual_caps=a['actual_caps'],actual_modes=a['actual_modes'],
 baseline_restored=physical,strict_events_passed=False,strict_qualification_passed=False,performance_qualified=False,
 limits='Matched exact pixels and scalar execution. Five samples per boot, control first, identical operation order. Fixed-work GDI includes flush/messages/background. Raw elapsed distributions are descriptive; unchanged readback discriminates background effects. Not desktop FPS, full storage/dump or release qualification; inherited Ft49 strict failure remains.'))
print(json.dumps(operations,indent=2))
