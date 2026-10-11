"""Review CLOSED234 exact source/publication/runtime scopes and staged bytes."""
import ast,datetime,hashlib,json,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'review002.json';assert not dest.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
for n,h in read(k/'emulator-frozen.json').items():assert sha(ws/n)==h,n
h=read(k/'trace002/host-state.json');a=read(k/'trace002/audit.json');t=read(k/'trace002/trace.json');q=read(k/'snapshot-review001.json');d=read(k/'consume-review001.json');c=read(k/'trace002/closure.json')
assert h['closed'] and h['cleanup_record_exists'] and c['closed'] and c['never_relaunch_or_recollect']
assert all(h[n]==0 for n in ['runner_exit_code','tracer_exit_code','observer_exit_code','audit_exit_code'])
assert t['closed'] and t['snapshot_protocol_passed'] and t['guest_resumed'] and t['physical_mode_restored'] and not t['remaining_breakpoints']
assert q['passed'] and q['complete_snapshot_protocol'] and q['waited_at_stop'] is None
assert q['source_sha256']==sha(k/'decode-snapshot.py') and q['trace_sha256']==sha(k/'trace002/trace.json')
assert d['passed'] and d['source_sha256']==sha(k/'decode-result.py') and d['trace_sha256']==sha(k/'trace002/trace.json')
assert len(q['views'])==3 and q['unique_events']==256
assert len(q['producer_pairs'])==len(q['ack_pairs'])==51 and len(q['complete_captured_lifecycles'])==50
assert all(v['cleared_nop'] for v in q['ack_pairs']) and not q['missing_pair_boundaries'] and not q['reset_pairs']
v=q['views']['wait_live_snapshot'];assert v['header']['total']==16765 and v['header']['overwritten']==16509
assert [r['kind'] for r in v['rows'][:3]]==[3,4,5] and [r['kind'] for r in v['rows'][-3:]]==[1,2,3],'Leading producer-set outside captured ring and trailing unmatched producer retained'
assert all(r['parameter']==0x7a080101 and r['trapped']==0x100 and r['nsource']==1 for r in q['producer_pairs'])
assert q['error_mask']==0x100000 and not v['current']['fifo_valid'] and all(not v['current'][f'fifo{i}'] for i in range(10))
assert v['current']['pending']==0x100000 and v['current']['waits']==2
requests=[x for x in t['monitor'] if x['command'].endswith('xwn-snapshot234 true')];assert len(requests)==1
assert len([x for x in t['monitor'] if x['command'].endswith('xwn-preserve227 true')])==1
assert all('busy=1' not in x['reply'] for x in t['monitor'])
assert not t['passed'] and not t['dirty_surface_coverage'] and t['reserved_bytes_unchanged']
p=t['preserve_result'];assert p['state']==4 and p['reason']==20 and p['consume_stop']==4
assert p['wait_before']==p['wait_after']==2 and p['consume_steps']==p['consume_words']==0
assert p['native_grant']==p['references_retired']==p['dirty']==p['downloaded']==p['bytes']==0
assert p['request0']==p['gate0']==0x03f7c5e8 and p['request1']==p['gate1']==0x03f8c858
assert p['request1']-p['request0']==66160 and d['raw_read_bytes']==212992
assert a['windows_launch_record_exists'] and a['normal_shutdown_count']==1 and a['dashboard_return']
assert a['cpu_scope_passed'] and a['observation_scope_passed'] and a['integrity_passed']
assert a['workload']['allocations']==a['workload']['releases']==a['workload']['exposure_refusals']==65
assert a['workload']['verified_bytes']==3194880 and a['workload']['joined_workers']==4
assert a['retirement']['rounds']==8 and a['retirement']['reads']==128
assert len(a['warnings_errors'])==1 and a['warnings_errors'][0]['source']=='Ftdisk' and a['warnings_errors'][0]['event_id']==49
assert not a['new_events']['application'] and not a['strict_events_passed']
for n in ['preservation_trace_scope_passed','strict_qualification_passed','backend_preservation_qualified','ordinary_qualified','physical_qualified']:assert not a[n]
for n,files in [('before/allocation.json',6719),('allocation.json',6724)]:
 al=read(k/'trace002'/n);assert al['directories']==320 and al['files']==files and al['directory_clusters']==321 and not al['errors'] and not al['orphan_cluster_count'] and al['allocation_consistent']
assert len(a['hives'])==5 and all(v['parsed'] for v in a['hives']) and all(v['matched'] for v in a['files'])
assert a['startup_unchanged'] and a['setupapi_history_preserved'] and a['event_history_preserved']
f=read(k/'preparation-failure001.json');assert f['closed'] and not f['guest_launch'] and not f['source_fixture_created'] and f['never_reuse_attempt']
assert sha(Path(f['partial_fixture']))==f['partial_sha256'] and sha(k/'prepare.py')==f['script_sha256']
assert not (k/'trace001/runner-start.json').exists() and not (k/'fixture-trace001.json').exists()
b=read(k/'build001.json');pins=read(k/'candidate001-source-pins.json')
assert b['passed'] and b['borrowed_sources_restored'] and len(b['original_sources'])==7
assert b['source_sha256']==sha(k/'build.py') and b['patch_generator_sha256']==sha(k/'patch.py')
assert b['source_manifest_sha256']==sha(k/'candidate001-source-pins.json') and b['patch_sha256']==sha(k/'snapshot234-build001.patch')
assert b['executable_sha256']==sha(k/'artifacts/build001/xemu-preserve227.exe')
for p in (k/'artifacts/build001/source').rglob('*'):
 if p.is_file():assert sha(p)==pins[p.relative_to(k/'artifacts/build001/source').as_posix()]
for n in ['test001.json','prelaunch-review001.json','guard-test001.json','powershell-syntax001.json']:assert read(k/n)['passed']
ct=read(k/'continuation-record001.json');continuation=(ws/'outputs/engineering-notes/CONTINUATION.md').read_bytes();assert sha(ws/'outputs/engineering-notes/CONTINUATION.md')==ct['new_sha256']
separator=b'--- Previous continuation retained byte-exact below ---\n\n';end=continuation.index(separator)+len(separator);assert hashlib.sha256(continuation[end:]).hexdigest()==ct['old_tail_sha256']
for p in k.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
for pid in [h[n] for n in ['controller_pid','runner_pid','tracer_pid','observer_pid']]:
 r=subprocess.run(['pwsh','-NoProfile','-Command',f'if(Get-Process -Id {pid} -ErrorAction SilentlyContinue){{exit 1}}'],capture_output=True);assert r.returncode==0,('Owned PID exists',pid)
staged={}
for n in subprocess.check_output(['git','diff','--cached','--name-only','-z'],cwd=ws).decode().strip('\0').split('\0'):
 if n.startswith('outputs/xemu-wait-snapshot234/'):
  blob=subprocess.check_output(['git','show',':'+n],cwd=ws);assert blob==(ws/n).read_bytes(),n;staged[n]=hashlib.sha256(blob).hexdigest()
assert staged
rf=read(k/'review-failure001.json');assert not rf['passed'] and rf['source_sha256']==sha(k/'review.py') and not rf['guest_failure']
subprocess.run(['git','diff','--cached','--check'],cwd=ws,check=True)
subprocess.run(['C:/Python314/python.exe','-B',str(ws/'tools/check-repository.py')],cwd=ws,check=True)
dest.write_text(json.dumps(dict(passed=True,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),source_sha256=sha(Path(__file__)),staged_byte_pins=staged,frozen_inputs_unchanged=True,owned_root_processes_closed=True,complete_worker_snapshot_protocol=True,actual_complete_lifecycles=50,windows_cpu_cold_scope_passed=True,preservation_refused=True,strict_ftdisk49_failure_retained=True,native_ownership=False,physical_access=False,scope='Worker publication and actual guest acknowledgements plus one debugger-observed CPU boot/cold integrity. No GPU handoff, acceleration, repeat-boot or all-file-content qualification.'),indent=2)+'\n')
print('234 actual publication/refusal/CPU/cold/frozen/staged/repository review PASS')
