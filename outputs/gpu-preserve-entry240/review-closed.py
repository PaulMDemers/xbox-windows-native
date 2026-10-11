"""Review existing closed239 evidence; never reopen or collect a disk."""
import ast,hashlib,json,re
from pathlib import Path
from parsing import snapshot_tuple
from preservation import preconditions,preserve_tuple
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'review001.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
matrix=read(k/'matrix001.json');assert matrix['closed'] and matrix['completed'] and len(matrix['cases'])==1
pins=read(k/'emulator-frozen.json')
for name,digest in pins.items():assert sha(ws/name)==digest,name
rows=[]
for case in ['control001','preserve001']:
 out=(k.parent/'gpu-preserve-entry239/control001') if case=='control001' else k/case;trace=read(out/'trace.json');audit=read(out/'audit.json');state=read(out/'host-state.json')
 assert state['closed'] and state['cleanup_record_exists'] and state['audit_exit_code']==0
 assert trace['passed'] and trace['closed'] and trace['guest_resumed'] and not trace['remaining_breakpoints'] and trace['physical_mode_restored']
 assert not trace['debugger_memory_writes'] and not trace['debugger_register_writes']
 events=trace['events'];assert [v['name'] for v in events]==['actual_xromwell_xbe_entry','actual_freeldr_multiboot_entry']
 assert all(v['resident_bytes_match'] and sha(ws/v['pin']['path'])==v['pin']['sha256'] for v in events)
 assert events[0]['registers'][8]==0x11100 and events[1]['registers'][8]==0x200a20 and events[1]['registers'][0]==0x2badb002 and not events[1]['registers'][9]&512
 phase=trace['phase_snapshot'];t=snapshot_tuple(phase['terminal_reply']);assert t==phase['tuple'] and phase['immutable_reread_matched']
 p=trace['preservation'];ranges=preconditions(t);assert p['ranges']==ranges and p['closed'] and not p['references_retired'] and not p['ownership_qualified']
 commands=[v['command'] for v in trace['monitor']]
 assert sum(v.startswith('qom-set ') and 'xwn-snapshot238 true' in v for v in commands)==1
 assert not any(v.startswith(('xp ','memsave ','write')) for v in commands)
 assert not any(v.startswith(('M','X','G','P')) for v in [x['command'] for x in trace['gdb_requests']])
 ram=[]
 if case=='control001':
  assert not p['request_accepted'] and p['control_no_request_verified'] and not p['ram'] and not p['preservation_scope_passed']
  assert not any(v.startswith('pmemsave ') or 'xwn-preserve227 true' in v for v in commands)
 else:
  result=preserve_tuple(p['terminal_reply']);assert result==p['result']==trace['preserve_result']
  assert result['state']==3 and result['surfaces']==result['dirty']==result['downloaded']==3 and result['bytes']==3072000
  assert not any(result[key] for key in ['old_halt','error','reason','consume_stop','consume_steps','consume_words','wait_before','wait_after'])
  assert result['request']==result['gate']==t['current_fifo'][4:14]
  assert p['request_accepted'] and p['immutable_reread_matched'] and p['worker_full_byte_comparison_passed'] and p['preservation_scope_passed']
  assert len(p['ram'])==1 and p['ram'][0]['label']=='after-preservation'
  assert sum(v.startswith('pmemsave ') for v in commands)==3
  first_ram=next(i for i,v in enumerate(commands) if v.startswith('pmemsave '))
  last_report=max(i for i,v in enumerate(commands) if v.startswith('qom-get ') and v.endswith('xwn-preserve227-report'))
  assert first_ram>last_report
  for pair,row in zip(ranges,p['ram'][0]['ranges']):
   path=ws/row['path'];assert pair==[row['address'],row['bytes']] and path.stat().st_size==row['bytes'] and sha(path)==row['sha256'];ram.append(row)
 assert audit['cpu_scope_passed'] and audit['observation_scope_passed'] and audit['guest_trace_scope_passed'] and audit['integrity_passed']
 assert audit['normal_shutdown_count']==1 and audit['dashboard_return'] and audit['orderly_host_exit_passed']
 assert not audit['new_events']['application'] and [(v['source'],v['event_id'],v['type']) for v in audit['warnings_errors']]==[('Ftdisk',49,1)]
 assert not audit['strict_qualification_passed'] and not audit['ordinary_qualified'] and not audit['physical_qualified'] and not audit['publication_contract_qualified']
 allocation=read(out/'allocation.json');assert allocation['allocation_consistent'] and not allocation['errors'] and not allocation['orphan_cluster_count']
 rows.append(dict(case=out.relative_to(ws).as_posix(),trace_sha256=sha(out/'trace.json'),audit_sha256=sha(out/'audit.json'),fifo=t['current_fifo'],context=t['context'],surfaces=t['surfaces'],ram=ram,worker_preservation_scope_passed=p['preservation_scope_passed'],cpu_scope_passed=True,cold_integrity_passed=True,normal_shutdown_count=1,allocation={n:allocation[n] for n in ['directories','files','directory_clusters','orphan_cluster_count']},workload=audit['workload'],strict_warning_error_ids=[dict(source=v['source'],id=v['event_id'],type=v['type']) for v in audit['warnings_errors']]))
for p in k.glob('*.py'):ast.parse(p.read_text(encoding='utf-8'),filename=str(p))
record=dict(passed=True,frozen_inputs_unchanged=len(pins),cases=rows,executable_sha256=read(k/'prelaunch-review001.json')['executable_sha256'],source_sha256=sha(Path(__file__)),backend_preservation_scope_passed=True,strict_qualified=False,native_gpu_ownership_qualified=False,physical_access=False,ordinary_qualified=False,scope='Closed debugger preservation: actual compiled worker fences/full byte comparisons and post-success RAM hashes. Complete runtime reference inventory/retirement and native ownership remain unproved; Ftdisk49 unchanged.')
dest.write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8');print('239 closed evidence review PASS; full ownership/strict qualification FALSE')
