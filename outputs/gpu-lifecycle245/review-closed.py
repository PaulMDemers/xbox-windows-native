"""Review corrected245 actual closed trace plus preserved244 failure, no recollection."""
import ast,hashlib,json
from pathlib import Path
from lifecycle import parse
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'review001.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=k.parent/'gpu-lifecycle244'
for kit in [old,k]:
 for p,h in read(kit/'emulator-frozen.json').items():assert sha(ws/p)==h,p
 for p in kit.glob('*.py'):ast.parse(p.read_text())
failed=read(old/'preserve001/trace.json');oldstate=read(old/'preserve001/host-state.json');remainder=read(old/'preserve001/audit-remainder001.json')
assert oldstate['closed'] and oldstate['audit_exit_code']==1 and not failed['passed']
assert failed['closed'] and failed['guest_resumed'] and not failed['remaining_breakpoints'] and failed['physical_mode_restored']
assert 'preservation' not in failed and len(failed['events'])==1
assert not (old/'preserve001/audit.json').exists() and remainder['completed_unperformed_metadata_stages'] and remainder['protected_hash_results_unrecorded']
m=read(k/'matrix001.json');state=read(k/'preserve001/host-state.json');t=read(k/'preserve001/trace.json');a=read(k/'preserve001/audit.json')
assert m['closed'] and m['completed'] and state['closed'] and state['audit_exit_code']==0
assert t['closed'] and t['passed'] and t['guest_resumed'] and t['physical_mode_restored'] and not t['remaining_breakpoints']
assert not t['debugger_memory_writes'] and not t['debugger_register_writes']
assert [e['name'] for e in t['events']]==['actual_xromwell_xbe_entry','actual_freeldr_multiboot_entry']
for e in t['events']:assert e['resident_bytes_match'] and sha(ws/e['pin']['path'])==e['pin']['sha256']
assert t['events'][0]['registers'][8]==0x11100 and t['events'][1]['registers'][8]==0x200a20
p=t['preservation'];assert p['closed'] and p['preservation_scope_passed'] and p['worker_full_byte_comparison_passed'] and not p['ram']
result=p['result'];assert result['state']==3 and result['surfaces']==result['dirty']==result['downloaded']==3 and result['bytes']==3072000
assert not any(result[n] for n in ['reason','error','old_halt','consume_stop','consume_words','consume_steps','wait_before','wait_after'])
assert p['paired_inventory_result']['passed']
run=Path('E:/Codex-private-artifacts/xbox-windows-feasibility/phase245-runs/nt5-phase245-preserve001')
q=read(k/'preserve001/lifecycle.json');assert q['passed'] and q['closed']
assert q['raw_sha256']==sha(run/'cpu-trace.log') and q['parser_sha256']==sha(k/'lifecycle.py')
full=parse((run/'cpu-trace.log').read_bytes(),[(v[0],v[1]) for v in t['phase_snapshot']['tuple']['surfaces']])
assert full==read(Path(q['full_analysis']['path'])) and q['full_analysis']['sha256']==sha(Path(q['full_analysis']['path']))
assert full['target_callback_retirement_observed'] and len(full['targets'])==3
assert full['observed']['callbacks']==full['observed']['inserted']==full['observed']['remove_requests']==full['observed']['unlinked']==full['observed']['freed']==23
assert full['observed']['cpu_stopped_frees']==0 and not full['display_quiescence'] and not full['full_reference_retirement'] and not full['native_gpu_ownership']
assert [len(v['frontend_inflight']) for v in full['marks']]==[0,1]
assert full['observed']['complete_frontend_loans']==1744 and full['observed']['sync_null_returns']==0
assert full['observed']['flushes']==full['observed']['complete_flushes']==1
assert a['cpu_scope_passed'] and a['observation_scope_passed'] and a['guest_trace_scope_passed'] and a['backend_preservation_scope_passed'] and a['integrity_passed']
assert a['normal_shutdown_count']==1 and a['dashboard_return'] and a['orderly_host_exit_passed']
assert [(v['source'],v['event_id'],v['type']) for v in a['warnings_errors']]==[('Ftdisk',49,1)] and not a['new_events']['application']
assert not any(a[n] for n in ['strict_qualification_passed','ordinary_qualified','physical_qualified','backend_preservation_qualified','publication_contract_qualified'])
assert read(k/'callback-test002.json')['passed'] and read(k/'layout-test001.json')['passed']
assert read(k/'baseline-inputs001.json')['passed']
for kit in [old,k]:
 d=read(kit/'portable-offload001.json');assert d['closed']
 for e in d['entries']:
  assert e['original_path_preserved'] and not e['disk_backing_chains_moved']
  for row in e['files']:assert sha(Path(e['source'])/row['path'])==row['sha256']
al=read(k/'preserve001/allocation.json');assert al['allocation_consistent'] and not al['errors'] and not al['orphan_cluster_count']
delay=[dict(surface=v['link']['a'],bytes=v['link']['b'],generation=v['generation'],request_to_unlink_ns=v['unlink']['when']-v['remove_request']['when'],request_to_free_ns=v['free']['when']-v['remove_request']['when'],cpu_stopped=v['free']['stopped']) for v in full['targets']]
dest.write_text(json.dumps(dict(passed=True,scope='Actual245 callback retirement and causal display-loan evidence; not quiescence/native ownership',preserved_failed244=True,old_protected_hash_scope_unknown=True,observed=full['observed'],targets=delay,final_marker_inflight_loans=len(full['marks'][1]['frontend_inflight']),cpu_stopped_callback_execution_proved=False,backend_preserved_bytes=result['bytes'],workload=a['workload'],allocation={n:al[n] for n in ['directories','files','directory_clusters','orphan_cluster_count']},frozen_pins={kit.name:len(read(kit/'emulator-frozen.json')) for kit in [old,k]},trace_sha256=sha(k/'preserve001/trace.json'),audit_sha256=sha(k/'preserve001/audit.json'),lifecycle_sha256=sha(k/'preserve001/lifecycle.json'),ordinary_qualified=False,strict_qualified=False,physical_access=False,native_gpu_ownership=False),indent=2)+'\n')
print('245 actual lifecycle/preservation/cold scopes PASS;244 failure retained; strict/display/native ownership FALSE')
