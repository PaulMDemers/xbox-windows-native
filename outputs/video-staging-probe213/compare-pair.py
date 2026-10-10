"""Matched closed buffer precursor pair, with unchanged strict event gates."""
from common import *
dest=k/'emulator-pair-review.json';assert not dest.exists()
cases={};pins={}
for name in ['control001','candidate001']:
 out=k/('emu-'+name);a=read(out/'audit.json');c=read(out/'closure.json');host=read(out/'host-state.json')
 assert c['closed'] and host['closed'] and a['scoped_display_passed']
 assert a['integrity_passed'] and a['display_workload_passed'] and a['measurement_events_passed']
 assert a['dashboard_return'] and a['normal_shutdown_count']==1 and not a['new_events']['application']
 assert [(v['source'],v['event_id']) for v in a['warnings_errors']]==[('Ftdisk',49)]
 assert not a['strict_qualification_passed'] and not a['ordinary_qualified']
 assert a['staging_probe']['passed'] and a['staging_probe']['missed']==0
 assert a['staging_probe']['mode']==int(name=='candidate001')
 assert len(a['upload_samples'])==5 and all(v['passed'] and v['enabled']==1 and v['completed_steps']==40 and v['actual_phase_pairs']==120 for v in a['upload_samples'])
 assert all(v['passed'] and len(v['cases'])==13 for v in a['text_samples'])
 assert all(v['passed'] and v['moves']==40 and v['exact_readbacks']==40 for v in a['window_samples'])
 assert a['boundary_analysis']['helper']['targets']==[1,2,5]
 assert not a['physical_access'] and not a['debugger'] and not a['gpu_transfer_qualified']
 cases[name]=a;pins[name]=dict(audit_sha256=sha(out/'audit.json'),closure_sha256=sha(out/'closure.json'))
a,b=[cases[n] for n in ['control001','candidate001']]
assert a['actual_caps']==b['actual_caps'] and a['actual_modes']==b['actual_modes']
for i in range(13):
 rows=[q['cases'][i] for r in [a,b] for q in r['text_samples']]
 for f in ['changed_pixels','guard_pixels','calls','glyphs','client','origin','bounds','input_clip','clip_complexity','copied_bytes']:
  assert all(v[f]==rows[0][f] for v in rows),(i,f)
phase_equal=all(a['upload_samples'][i]['phase_totals']==b['upload_samples'][i]['phase_totals'] for i in range(5))
r=dict(passed=True,source_sha256=sha(Path(__file__)),cases=pins,matched_text_pixels_and_scope=True,
 upload_phase_totals_equal=phase_equal,buffer_probe_passed=True,strict_qualification_passed=False,
 candidate_records=b['staging_probe']['records'],physical_qualified=False,gpu_transfer_qualified=False,performance_qualified=False,
 limits='One ordinary fresh child each, control before candidate; exact buffer OFF/ON and retained GDI/cold gates. Inherited Ftdisk49 remains strict failure. No GPU address/completion/speed/physical qualification.')
save(dest,r);print('Matched buffer/GDI/cold scope PASS; strict whole boot remains FALSE.')
