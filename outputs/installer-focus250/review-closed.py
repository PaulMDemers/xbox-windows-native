"""Independent raw/frozen proof; scoped PASS never promotes strict/native qualification."""
import hashlib,json
from pathlib import Path
from worker import qualify
from closed import qualify as uiqualify
from lifecycle247 import parse
from diagnostic import decode
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'closed-review001.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
for path,h in read(k/'emulator-frozen.json').items():assert sha(ws/path)==h,path
o=k/'preserve001';r=read(o/'worker.json');t=read(o/'trace.json');a=read(o/'audit.json');s=read(o/'host-state.json')
run=Path('E:/Codex-private-artifacts/xbox-windows-feasibility/phase250-runs/nt5-phase250-preserve001');raw=run/'cpu-trace.log';data=raw.read_bytes()
assert s['closed'] and s['cleanup_record_exists'] and read(run/'host-exit.json')['passed']
assert t['passed'] and t['closed'] and t['guest_resumed'] and not t['remaining_breakpoints'] and t['physical_mode_restored']
assert r['passed'] and r['raw_sha256']==sha(raw)
assert qualify(data,t['worker_closed_report'],t['worker_closed_reread'],t['worker_released_report'])==r['worker']
assert uiqualify(data,t['frontend_closed_report'],t['frontend_closed_reread'],t['frontend_reopened_report'])==r['frontend']
full=parse(data,[(v[0],v[1]) for v in t['phase_snapshot']['tuple']['surfaces']]);assert full==read(Path(r['full_analysis']['path']))
assert full['target_callback_retirement_observed'] and full['observed']['cpu_stopped_frees']==0 and not full['observed']['sync_null_returns']
assert a['cpu_scope_passed'] and a['guest_trace_scope_passed'] and a['integrity_passed'] and a['normal_shutdown_count']==1 and a['dashboard_return']
assert a['workload']['passed'] and a['wizard']['passed'] and a['retirement']['passed']
assert len(a['warnings_errors'])==1 and a['warnings_errors'][0]['source']=='Ftdisk' and a['warnings_errors'][0]['event_id']==49 and not a['new_events']['application']
assert not a['strict_events_passed'] and not a['strict_qualification_passed'] and not a['ordinary_qualified'] and not a['physical_qualified']
wizard=o/'artifacts/wizard201.log';d,projection=decode(wizard.read_bytes());assert d==read(o/'installer-focus.json') and d['sample_count']==0 and projection==wizard.read_bytes()
assert not d['foreground_refusal_observed'] and not r['worker']['latest_dirty_bytes_at_disposal_preserved']
assert a['wizard']['targets']==[1,2,5] and a['wizard']['actions']==3 and a['wizard']['actual_idle']==[5100,3,23430]
f=read(k/'fixture-preserve001.json');build=read(k/'wizard-build001.json');assert f['protected']['F/xwnret224/wizard.exe']==build['binary_sha256']==sha(k/'artifacts/wizard-build001/wizard.exe')
assert sha(k/'policy.h')==sha(k.parent/'setup-wizard-automation201/policy.h')
prior=k.parent/'installer-focus249/preserve001';pt=read(prior/'trace.json');assert not pt['passed'] and 'loader_launch' not in pt and pt['guest_resumed'] and not pt['remaining_breakpoints']
assert read(prior/'host-state.json')['closed'] and read(prior/'audit.json')['integrity_passed']
dest.write_text(json.dumps(dict(review_passed=True,scoped_workload_barrier_passed=True,strict_qualification_passed=False,ordinary_qualified=False,physical_qualified=False,native_gpu_ownership=False,source_sha256=sha(Path(__file__)),frozen_checks=len(read(k/'emulator-frozen.json')),raw_sha256=sha(raw),wizard_sha256=sha(wizard),refused_wait_snapshots=0,original248_cause_resolved=False,diagnostic_branch_runtime_exercised=False,workload=a['workload'],worker=r['worker'],frontend=r['frontend'],observed=full['observed'],normal_shutdown_count=1,dashboard_return=True,integrity_passed=True,strict_warning_error_events=[dict(source='Ftdisk',event_id=49,type=1)],prior249_remains_failed=True,physical_access=False),indent=2)+'\n');print('250 raw scoped workload/barriers PASS; strict FALSE, no reproduced foreground refusal')
