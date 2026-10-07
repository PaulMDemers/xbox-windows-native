"""Qualify targeted first-install observations, never ordinary or physical stability."""
import hashlib,json,re
from pathlib import Path
k=Path(__file__).resolve().parent;out=k/'001';read=lambda p:json.loads(p.read_text())
a=read(out/'audit.json');p=read(out/'package-audit.json');v=read(out/'allocation.json');c=read(out/'collection.json')
for stage in c['stages'].values():assert hashlib.sha256((out/stage['output']).read_bytes()).hexdigest()==stage['sha256']
w=a['window_observer_log']
run=k.parents[1]/'work/runs/nt5-fatx-first-install-0101-001'
assert (run/'cleanup.json').exists()
completion=read(run/'completion.json')
gates=dict(owned_return_cleanup=completion.get('reason')=='external_capture_complete',cold_audit=a['diagnostic_checks_passed'],installed_gpu=p['installation_checks_passed'],
    setup_log_grew=p['new_setupapi_bytes']>0,no_new_non_ascii_bytes=not p['new_non_ascii_offsets'],
    one_gpu_finish=len(re.findall(r'GPU_FINISH_ONCE .*posted=1',w))==1,
    one_reboot_defer=len(re.findall(r'GPU_RESTART_DEFER_ONCE .*posted=1',w))==1,
    one_identified_placeholder_cancel=len(re.findall(r'PLACEHOLDER_CANCEL_ONCE .*posted=1',w))==1,
    queue_idle='INSTALL_QUEUE_IDLE_BEFORE_RESTART 0' in a['log'],
    allocation=v['allocation_consistent'] and not v['errors'] and not v['orphan_cluster_count'],
    five_structural_hives=len(a['hives'])==5 and all(h['parsed'] for h in a['hives']))
r=dict(passed=all(gates.values()),gates=gates,physical_qualified=False,ordinary_stability_qualified=False,
    ui_assisted_diagnostic=True,evidence_sha256={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in [out/n for n in ['audit.json','allocation.json','package-audit.json','collection.json','launch.json']]},
    limits='Exact prior004 targeted UI helper changes installation timing. No physical result or explanation of original malformed log. Placeholder cancellation does not persistently resolve that device.')
p=out/'qualification.json';assert not p.exists();p.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
