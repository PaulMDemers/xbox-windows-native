"""Require matched scoped pixels/actual119 coverage; report producer bytes only."""
from common import *
from upload_analysis import HOOKS,FIELDS
physical='--physical' in sys.argv;dest=k/('physical-pair-review.json' if physical else 'emulator-pair-review.json');assert not dest.exists()
cases={};pins={}
for name in ['control001','candidate001']:
 out=k/(name if physical else 'emu-'+name);a=read(out/('physical-audit.json' if physical else 'audit.json'));c=read(out/'closure.json')
 assert c['closed'] and a['scoped_display_passed'] and a['dashboard_return'] and a['normal_shutdown_count']==1
 assert not a['new_events']['application'] and not a['strict_qualification_passed']
 assert [(v['source'],v['event_id']) for v in a['warnings_errors']]==[('Ftdisk',49)]
 assert len(a['upload_samples'])==5 and all(v['passed'] and v['completed_steps']==40 and v['actual_phase_pairs']==120 for v in a['upload_samples'])
 assert all(v['passed'] and len(v['cases'])==13 for v in a['text_samples'])
 assert all(v['passed'] and v['moves']==40 and v['exact_readbacks']==40 for v in a['window_samples'])
 assert a['boundary_analysis']['helper']['targets']==([1,2,3,4] if physical else [1,2,5])
 if physical:
  assert c['baseline_restored'] and not c['startup_enabled'] and read(out/'physical-hive-audit.json')['passed'] and read(out/'restored-verification.json')['passed']
 else:assert a['integrity_passed'] and not a['debugger'] and not a['physical_access']
 cases[name]=a;pins[name]=dict(audit_sha256=sha(out/('physical-audit.json' if physical else 'audit.json')),closure_sha256=sha(out/'closure.json'))
a,b=[cases[n] for n in ['control001','candidate001']];assert a['actual_caps']==b['actual_caps'] and a['actual_modes']==b['actual_modes']
for i in range(13):
 rows=[q['cases'][i] for r in [a,b] for q in r['text_samples']]
 for f in ['changed_pixels','guard_pixels','calls','glyphs','client','origin','bounds','input_clip','clip_complexity','copied_bytes']:assert all(v[f]==rows[0][f] for v in rows),(i,f)
totals={phase:{name:{f:sum(v['phase_totals'][phase][name][f] for v in b['upload_samples']) for f in FIELDS} for name in HOOKS} for phase in ['move','paint','readback']}
assert all(v['enabled']==0 and v['total_upload_bytes']==0 for v in a['upload_samples'])
assert all(v['enabled']==1 and v['total_upload_bytes']>0 for v in b['upload_samples'])
r=dict(passed=True,actual_upload_coverage_passed=True,physical_testing_ready=not physical,physical_result=physical,cases=pins,
 candidate_phase_totals=totals,actual_caps=a['actual_caps'],actual_modes=a['actual_modes'],baseline_restored=physical,
 strict_events_passed=False,strict_qualification_passed=False,performance_qualified=False,
 limits='Five within-boot samples, control before candidate. Exact pixels/controlled steps, device-global phase attribution including background. NULL bytes do not establish waste. No FPS/speed/newmode/storage/dump/release claim; Ft49 remains strict failure.')
save(dest,r);print(json.dumps(totals,indent=2))
