import hashlib,importlib.util,json
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];out=k/'emu001'
read=lambda p:json.loads(p.read_text())
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
host=read(out/'host-state.json');audit=read(out/'audit.json');trace=read(out/'trace.json')
assert host['closed'] and host['status']=='cold_audited'
assert all(host[n]==0 for n in ['runner_exit_code','tracer_exit_code','audit_exit_code'])
assert trace['passed'] and trace['closed'] and trace['guest_resumed'] and not trace['remaining_breakpoints'] and trace['physical_mode_restored']
assert audit['ledger_diagnostic_passed'] and audit['integrity_passed'] and audit['orderly_host_exit_passed']
assert audit['normal_shutdown_count']==1 and audit['dashboard_return']
assert not audit['strict_qualification_passed']
assert [(e['source'],e['event_id']) for e in audit['warnings_errors']]==[('Ftdisk',49)]
assert not audit['new_events']['application']
analysis=read(out/'ledger-analysis.json');assert analysis['unknown_actor_work']==0 and analysis['original_work_returned']==54
assert not analysis['thread_join_proved'] and not analysis['retirement_ready']
assert read(out/'actual-controls.json')['passed'] and read(k/'source-review.json')['passed']
frozen=read(k/'emulator-frozen.json')
for n,h in frozen.items():assert sha(ws/n)==h,n
sp=importlib.util.spec_from_file_location('deps',k/'runtime-dependencies.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
assert m.inventory()==read(k/'host-dependencies.json')['files']
alloc=read(out/'allocation.json');assert alloc['allocation_consistent'] and not alloc['orphan_cluster_count'] and not alloc['errors']
r=dict(scoped_observation_passed=True,strict_qualification_passed=False,strict_failure='Inherited Ftdisk49',
    closed=True,never_relaunch_or_recollect=True,physical_access=False,ordinary_qualified=False,
    renderer_sha256=read(k/'renderer-build001.json')['executable_sha256'],
    original_shader_work_returned=54,os_thread_join_proved=False,
    actual_native_attestations=len(trace['checkpoints']),exact_cpu_bytes=32768,cpu_reads=2,cpu_writes=0,
    ledger_rows=55678,ledger_pages=len(trace['ledger_pages']),ui_rows=1939,ui_pages=len(trace['ui_pages']),
    native_contexts=analysis['native_contexts'],ui_native_context=analysis['ui_context'],
    directories=alloc['directories'],files=alloc['files'],directory_clusters=alloc['directory_clusters'],
    orphan_clusters=0,allocation_errors=0,hives=len(audit['hives']),protected_hashes=len(audit['files']),
    frozen_inputs=len(frozen),host_dependencies=len(m.inventory()),
    indexed_binding_rows=analysis['scoped_indexed_binding_rows'],container_attachment_rows=analysis['container_attachment_rows'],
    synthetic_negatives=read(k/'extra-tests001.json')['negative_controls'],
    actual_negatives=len(read(out/'actual-controls.json')['rejected_mutations']),
    retirement_ready=False,native_gpu_grant=False,speedup_proved=False,
    source_limitation=read(k/'source-review.json')['limitation'],
    evidence_sha256={str(p.relative_to(k)):sha(p) for p in [out/'trace.json',out/'audit.json',out/'ledger-analysis.json',out/'actual-controls.json',out/'release-evidence.json',k/'source-review.json']})
dest=k/'final-review.json';assert not dest.exists();dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
