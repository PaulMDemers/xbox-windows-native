"""Review CLOSED independent traces, raw immutable tuples and recovered cold scope."""
import hashlib,json,re
from pathlib import Path
from parsing import snapshot_tuple,span
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'review001.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pins=read(k/'emulator-frozen.json')
for name,digest in pins.items():assert sha(ws/name)==digest,name
matrix=read(k/'matrix001.json');assert matrix['completed'] and matrix['closed']
inv=read(k/'inventory001.json');rows=[];private_pids=[]
for case,phase in [('dashboard001','dashboard'),('xbe001','xbe'),('freeldr001','freeldr')]:
 out=k/case;t=read(out/'trace.json');a=read(out/'audit.json');h=read(out/'host-state.json');f=read(k/('fixture-'+case+'.json'))
 assert h['closed'] and h['cleanup_record_exists'] and h['audit_exit_code']==0 and read(out/'closure.json')['closed']
 assert t['case']==case and t['phase']==phase and t['closed'] and t.get('guest_resumed') and t['remaining_breakpoints']==[] and t['physical_mode_restored'] and t['prior_physical_mode']=='0'
 assert not t['debugger_memory_writes'] and not t['debugger_register_writes'] and not t['gpu_ownership_qualified'] and not t['dirty_surface_coverage']
 commands=[v['command'] for v in t['monitor']];assert sum('qom-set' in v and 'xwn-snapshot238' in v for v in commands)<=1
 assert not any('xwn-preserve' in v for v in commands)
 requests=[v['command'] for v in t['gdb_requests']];assert not any(v.startswith(('M','X','P','G','Qqemu.PhyMemMode:1')) for v in requests)
 arms=[v for v in requests if v.startswith('Z')];removes=[v for v in requests if v.startswith('z')];assert [v[1:] for v in arms]==[v[1:] for v in removes]
 events=t['events'];resident=[]
 for event in events:
  pin=event['pin'];p=ws/pin['path'];assert sha(p)==pin['sha256'] and p.stat().st_size==pin['bytes']==32 and event['resident_bytes_match']
  if event['name']=='actual_xromwell_xbe_entry':expected=span((k/'artifacts/inputs/xromwell.xbe').read_bytes(),inv['launcher'],inv['launcher']['entry'],32);entry=inv['launcher']['entry']
  else:
   assert event['name']=='actual_freeldr_multiboot_entry';entry=int(inv['freeldr']['entry_address'],16);offset=entry-int(inv['freeldr']['staging_address'],16);expected=(k/'artifacts/inputs/freeldr.sys').read_bytes()[offset:offset+32]
   assert event['registers'][0]==0x2badb002 and not event['registers'][9]&0x200
  assert p.read_bytes()==expected and pin['address']==entry and event['registers'][8]==entry
  resident.append(pin)
 s=t.get('phase_snapshot',{});summary=dict(terminal_state=s.get('terminal_state'),passed=s.get('passed',False),error=t.get('error'))
 if s.get('terminal_state')==3:
  parsed=snapshot_tuple(s['terminal_reply']);assert parsed==s['tuple'] and s['immutable_reread_matched'] and s['terminal_reply']==s['immutable_reread_reply']
  assert s['phase']==phase and parsed['current_fifo_valid']
  if phase=='xbe':assert s['registers']==events[0]['registers'] and s['cpu_phase']=='actual_xromwell_xbe_entry'
  if phase=='freeldr':assert s['registers']==events[1]['registers'] and s['cpu_phase']=='actual_freeldr_multiboot_entry'
  if phase=='dashboard':assert s['cpu_phase']=='dashboard_cpu_stop'
  c=parsed['current_pg_only'];summary.update(header=parsed['header'],wait_mask=c[9],wait_labels=parsed['wait_labels'],pending=c[4],enabled=c[5],nsource=c[6],trapped=c[7],data=c[8],current_fifo_valid=True,fifo=parsed['current_fifo'],fifo_when=parsed['fifo_when'],context=parsed['context'],renderer_valid=parsed['renderer_valid'],surface_count=parsed['surface_count'],surface_truncated=parsed['surface_truncated'],surfaces=parsed['surfaces'],cpu_eip=s['registers'][8])
 elif s.get('terminal_state')==5:assert not s.get('passed') and not t['passed'] and 'tuple' not in s
 else:assert not t['passed'],'Missing terminal phase cannot pass'
 if t['passed']:assert len(events)==2 and summary['passed'] and len(arms)==2
 assert not a['ordinary_qualified'] and not a['physical_qualified'] and not a['backend_preservation_qualified'] and not a['strict_qualification_passed']
 allocation=read(out/'allocation.json');assert a['allocation_passed']==bool(allocation['allocation_consistent'] and not allocation['errors'] and not allocation['orphan_cluster_count'])
 assert len(a['hives'])==5 and a['strict_events_passed']==(not a['warnings_errors'] and not a['new_events']['application'])
 assert a['guest_trace_scope_passed']==bool(a['observation_scope_passed'] and t['passed'] and t['closed'] and t.get('guest_resumed') and not t['remaining_breakpoints'])
 seed=Path(f['fixture_path_windows']);assert sha(seed)==f['fixture_sha256']
 run=Path('E:/Codex-private-artifacts/xbox-windows-feasibility/phase238-runs/nt5-phase238-'+case)
 assert read(run/'cleanup.json') is not None
 row=dict(case=case,phase=phase,trace_passed=t['passed'],snapshot=summary,resident_pins=resident,integrity_passed=a['integrity_passed'],cpu_scope_passed=a['cpu_scope_passed'],observation_scope_passed=a['observation_scope_passed'],normal_shutdown_count=a['normal_shutdown_count'],dashboard_return=a['dashboard_return'],warnings_errors=[{'source':v['source'],'event_id':v['event_id'],'type':v['type']} for v in a['warnings_errors']],strict_qualified=False,ordinary_qualified=False,physical_qualified=False,allocation={v:allocation[v] for v in ['directories','files','directory_clusters','orphan_cluster_count','errors'] if v in allocation},hives=5,host_closure=a['host_exit'],cold_scope='Orderly host exit and recovered selected-content/full-allocation checks; not all-file durability')
 rows.append(row)
 for name in ['controller_pid','runner_pid','tracer_pid','observer_pid']:
  if h.get(name):private_pids.append(h[name])
record=dict(passed=True,evidence_review=True,frozen_pins_unchanged=len(pins),independent_runs=True,cases=rows,owned_process_ids=private_pids,physical_access=False,gpu_ownership_qualified=False,limits='Review correctness, not strict GPU qualification; phase PG-only worker state is not renderer retirement/dirty readback/current FIFO/producer close.')
dest.write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record,indent=2))
