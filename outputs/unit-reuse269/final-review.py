"""Close this unique observation; do not turn missing reuse into a PASS."""
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
assert not audit['strict_qualification_passed'] and [(e['source'],e['event_id']) for e in audit['warnings_errors']]==[('Ftdisk',49)]
assert not audit['new_events']['application']
analysis=read(out/'ledger-analysis.json');assert analysis['unknown_actor_work']==0
assert read(out/'actual-controls.json')['passed']
watch=read(out/'watch-analysis.json');assert watch['observation_parse_pass']
assert read(out/'watch-seal.json')['acknowledged']
frozen=read(k/'emulator-frozen.json')
for n,h in frozen.items():assert sha(ws/n)==h,n
sp=importlib.util.spec_from_file_location('deps',k/'runtime-dependencies.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
assert m.inventory()==read(k/'host-dependencies.json')['files']
alloc=read(out/'allocation.json');assert alloc['allocation_consistent'] and not alloc['orphan_cluster_count'] and not alloc['errors']
folder=Path(read(out/'watch-location.json')['path'])
private={p.name:{'bytes':p.stat().st_size,'sha256':sha(p)} for p in folder.iterdir() if p.is_file()}
r=dict(closed=True,never_relaunch_or_recollect=True,scoped_observation_passed=True,
    all_four_actual_reuse=watch['all_four_actual_reuse'],all_four_unchanged=watch['all_four_unchanged'],
    strict_qualification_passed=False,strict_failure='Inherited Ftdisk49',physical_access=False,ordinary_qualified=False,
    renderer_sha256=read(k/'renderer-build005.json')['executable_sha256'],actual_native_attestations=len(trace['checkpoints']),
    exact_cpu_bytes=32768,cpu_reads=2,cpu_writes=0,ledger_pages=len(trace['ledger_pages']),ui_pages=len(trace['ui_pages']),
    directories=alloc['directories'],files=alloc['files'],directory_clusters=alloc['directory_clusters'],orphan_clusters=0,allocation_errors=0,
    hives=len(audit['hives']),protected_hashes=len(audit['files']),frozen_inputs=len(frozen),host_dependencies=len(m.inventory()),
    actual_graph_negatives=len(read(out/'actual-controls.json')['rejected_mutations']),synthetic_watch_negatives=read(k/'parser-tests001.json')['synthetic_rejected'],
    exact_observer_gate_races=4096,failed_gate_preserved=True,release_installed=False,native_gpu_grant=False,speedup_proved=False,
    no_full_cpu_concurrency_guarantee=True,private_readback_files=private,
    evidence_sha256={str(p.relative_to(k)):sha(p) for p in [out/'trace.json',out/'audit.json',out/'ledger-analysis.json',out/'actual-controls.json',out/'watch-analysis.json',out/'watch-seal.json',out/'watch-terminal.txt',k/'runtime-review.json']})
dest=k/'final-review.json';assert not dest.exists();dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
