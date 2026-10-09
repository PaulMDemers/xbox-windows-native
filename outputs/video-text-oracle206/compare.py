"""Require two complete new text scopes; compare copied bytes, not emulator FPS."""
from common import *
dest=k/'emulator-pair-review.json';assert not dest.exists()
cases={}
for case in ['control001','candidate001']:
 out=k/('emu-'+case);a=read(out/'audit.json');c=read(out/'closure.json')
 assert c['closed'] and c['audit_sha256']==sha(out/'audit.json')
 assert a['scoped_display_passed'] and a['integrity_passed'] and a['display_workload_passed']
 assert not a['debugger'] and not a['physical_access'] and a['normal_shutdown_count']==1 and a['dashboard_return']
 assert a['boundary_analysis']['helper']['targets']==[1,2,5]
 assert all(v['passed'] and len(v['cases'])==13 for v in a['text_samples'])
 assert all(v['moves']==40 and v['exact_readbacks']==40 for v in a['window_samples'])
 assert len(a['warnings_errors'])==1 and [(v['source'],v['event_id']) for v in a['warnings_errors']]==[('Ftdisk',49)]
 assert not a['strict_qualification_passed'];cases[case]=a
assert cases['control001']['actual_caps']==cases['candidate001']['actual_caps'] and cases['control001']['actual_modes']==cases['candidate001']['actual_modes']
table=[]
for index in range(13):
 a=[v['cases'][index] for v in cases['control001']['text_samples']];b=[v['cases'][index] for v in cases['candidate001']['text_samples']]
 assert all(q['changed_pixels']==a[0]['changed_pixels'] and q['guard_pixels']==a[0]['guard_pixels'] for q in a+b)
 assert all(q['calls']==a[0]['calls'] for q in a+b)
 x,y=[q['copied_bytes'] for q in a],[q['copied_bytes'] for q in b]
 assert len(set(x))==len(set(y))==1 and y[0]<=x[0]
 table.append(dict(case=index,control_bytes=x[0],candidate_bytes=y[0],reduction_percent=None if not x[0] else 100*(x[0]-y[0])/x[0],matched_changed_pixels=a[0]['changed_pixels'],calls=a[0]['calls']))
assert table[0]['calls']==1
improvement=any(v['candidate_bytes']<v['control_bytes'] for v in table)
save(dest,dict(passed=True,optimization_demonstrated=improvement,physical_testing_ready=improvement,physical_access=False,rows=table,cases={c:dict(audit_sha256=sha(k/('emu-'+c)/'audit.json'),closure_sha256=sha(k/('emu-'+c)/'closure.json')) for c in cases},
 strict_events_passed=False,limits='Actual input-clip matched text-copy comparison with same visible pixels across both five-sample ordinary boots. Not emulator or hardware FPS, physical qualification or release. Sole inheritedFt49 remains strict failure.'))
print(json.dumps(table,indent=2))
