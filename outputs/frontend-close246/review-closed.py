"""Independent closed246 raw reparse, resident pins, exact cold and source review."""
import hashlib,json
from pathlib import Path
from closed import qualify
from lifecycle246 import parse
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'review001.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for p,h in read(k/'emulator-frozen.json').items():assert sha(ws/p)==h,p
m=read(k/'matrix001.json');s=read(k/'preserve001/host-state.json');t=read(k/'preserve001/trace.json');a=read(k/'preserve001/audit.json');v=read(k/'preserve001/frontend.json')
assert m['closed'] and m['completed'] and s['closed'] and s['runner_exit_code']==s['tracer_exit_code']==s['observer_exit_code']==s['audit_exit_code']==0
assert t['passed'] and t['closed'] and t['physical_mode_restored'] and t['guest_resumed'] and not t['remaining_breakpoints'] and len(t['events'])==2
for row in t['events']:assert row['resident_bytes_match'] and sha(ws/row['pin']['path'])==row['pin']['sha256']==row['expected_sha256']
raw=Path(v['raw_path']);data=raw.read_bytes();assert sha(raw)==v['raw_sha256'] and len(data)==v['raw_bytes']
actual=qualify(data,t['frontend_closed_report'],t['frontend_closed_reread'],t['frontend_reopened_report']);assert actual==v['frontend'] and v['passed']
full=parse(data,[(r[0],r[1]) for r in t['phase_snapshot']['tuple']['surfaces']]);assert full==read(Path(v['full_analysis']['path'])) and sha(Path(v['full_analysis']['path']))==v['full_analysis']['sha256']
assert full['target_callback_retirement_observed'] and len(full['targets'])==3
assert a['cpu_scope_passed'] and a['integrity_passed'] and a['normal_shutdown_count']==1 and a['orderly_host_exit_passed'] and a['dashboard_return']
assert len(a['warnings_errors'])==1 and a['warnings_errors'][0]['source']=='Ftdisk' and a['warnings_errors'][0]['event_id']==49 and not a['strict_events_passed'] and not a['strict_qualification_passed'] and not a['ordinary_qualified'] and not a['physical_qualified']
allocation=read(k/'preserve001/allocation.json');assert allocation['allocation_consistent'] and not allocation['errors'] and not allocation['orphan_cluster_count']
assert len(a['hives'])==5 and all(r['parsed'] for r in a['hives']) and all(r['matched'] for r in a['files'])
assert read(k/'build001.json')['borrowed_sources_restored'] and not read(k/'frontend-test001.json')['passed']
assert read(k/'frontend-test002.json')['passed'] and read(k/'closed-test001.json')['passed']
assert read(k.parent/'gpu-lifecycle245/review001.json')['passed'] and not read(k.parent/'gpu-lifecycle244/preserve001/trace.json')['passed']
dest.write_text(json.dumps(dict(passed=True,source_sha256=sha(Path(__file__)),frontend=actual,raw_sha256=sha(raw),actual_qualified_scope='One actual UI closure/reopen; CPU/cold integrity scope; strict events fail',native_gpu_ownership=False,ordinary_qualified=False,physical_access=False,all_owned_closed=True,frozen_pins=len(read(k/'emulator-frozen.json')),stage_hashes={n:sha(k/n) for n in ['matrix001.json','build001.json','preserve001/trace.json','preserve001/frontend.json','preserve001/audit.json','preserve001/allocation.json']}),indent=2)+'\n')
print('246 independent raw/runtime/cold calibration review PASS')
