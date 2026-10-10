"""Independent frozen-byte, raw pin, closure and qualification-scope review."""
import ast,datetime,hashlib,json,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'review001.json';assert not dest.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
results=[]
for name,build in [('xemu-backend-preserve227','build005'),('xemu-backend-reason228','build002')]:
 kit=k.parent/name;case=kit/'trace001';a=read(case/'audit.json');t=read(case/'trace.json');h=read(case/'host-state.json');c=read(case/'closure.json');b=read(kit/(build+'.json'))
 assert h['closed'] and c['closed']
 if name.endswith('227'):
  assert h['status']=='cold_audited_closed'
  assert all(h[n]==0 for n in ['runner_exit_code','tracer_exit_code','observer_exit_code','audit_exit_code'])
 else:
  assert h['status']=='preserved_failure' and 'TimeoutExpired' in h['error']
  recovery=read(case/'observer-recovery.json');collection=read(case/'recovered-closure.json')
  assert recovery['closed'] and recovery['exit_code']==0 and recovery['no_previous_windows_request']
  assert collection['closed'] and collection['audit_exit_code']==0
  assert 'KeyError' in (case/'observer-console.txt').read_text()
 assert c['audit_sha256']==sha(case/'audit.json')
 frozen=read(kit/'emulator-frozen.json')
 for p,digest in frozen.items():assert sha(ws/p)==digest,p
 assert b['passed'] and b['borrowed_sources_restored']
 assert sha(kit/'artifacts'/build/'xemu-preserve227.exe')==b['executable_sha256']
 assert t['closed'] and t['guest_resumed'] and not t['remaining_breakpoints']
 assert not t['debugger_memory_writes'] and not t['gpu_ownership_qualified']
 iv=read(k.parent/'video-loader-handoff225/inventory002.json');site=iv['sites']['producer_exit_entry']
 row=t['executing_code_pin'];raw=ws/iv['binaries']['image-crom.bin']['path'];assert sha(raw)==iv['binaries']['image-crom.bin']['sha256']
 data=raw.read_bytes()[site-0x3a00000:site-0x3a00000+64]
 assert row['address']==site and bytes.fromhex(row['hex'])==data and row['sha256']==hashlib.sha256(data).hexdigest()
 for before,after in zip(t['before'],t['after']):
  assert sha(ws/before['path'])==before['sha256']==after['sha256']==sha(ws/after['path'])
 assert t['reserved_bytes_unchanged']
 assert a['integrity_passed']
 assert not a['ordinary_qualified'] and not a['physical_qualified'] and not a['strict_qualification_passed']
 if name.endswith('227'):
  assert a['cpu_scope_passed'] and a['observation_scope_passed']
  assert a['normal_shutdown_count']==1 and a['dashboard_return']
 else:
  assert not a['cpu_scope_passed'] and not a['observation_scope_passed']
  assert a['normal_shutdown_count']==0 and not a['dashboard_return']
  assert not (case/'artifacts/result.log').exists()
  assert 'TIMEOUT201 1 0 120090' in (case/'artifacts/wizard201.log').read_text()
 assert len(a['hives'])==5 and all(v['parsed'] for v in a['hives']) and all(v['matched'] for v in a['files'])
 alloc=read(case/'allocation.json');assert (alloc['directories'],alloc['files'],alloc['directory_clusters'])==(320,6724 if name.endswith('227') else 6722,321)
 assert alloc['allocation_consistent'] and not alloc['errors'] and not alloc['orphan_cluster_count']
 assert len(a['warnings_errors'])==1 and a['warnings_errors'][0]['source']=='Ftdisk' and a['warnings_errors'][0]['event_id']==49
 assert not a['new_events']['application']
 result=t['preserve_result'];assert result['native_grant']==result['references_retired']==0
 assert result['state']==(4 if name.endswith('227') else 3) and result['downloaded']==result['bytes']==0
 assert not a['backend_preservation_qualified'] and not t['dirty_surface_coverage']
 if name.endswith('228'):assert result['reason']==0 and result['surfaces']==0
 results.append(dict(kit=name,closed=True,frozen_pins=len(frozen),trace_sha256=sha(case/'trace.json'),audit_sha256=sha(case/'audit.json'),result=result,backend_qualified=False,cpu_scope_passed=a['cpu_scope_passed'],physical_access=False))
t=read(k/'terminal-test001.json');assert t['passed'] and t['source_sha256']==sha(k/'test-terminal.py') and t['test_sha256']==sha(k/'test-terminal.c')
assert t['compiled_source_sha256']==sha(k/'artifacts/build002/source/hw/xbox/nv2a/nv2a.c')
for row in t['runs']:assert row['compile_exit']==row['exit_code']==0 and not row['stderr'] and 'checks=100390 concurrent_pairs=100000' in row['stdout']
compiled=(k/'artifacts/build002/source/hw/xbox/nv2a/nv2a.c').read_text();start=compiled.index('void nv2a_preserve227_finish(');end=compiled.index('\nstatic void nv2a_realize',start)
assert hashlib.sha256(compiled[start:end].encode()).hexdigest()==t['actual_helper_sha256']
for kit in [k,k.parent/'xemu-backend-preserve227']:
 for p in kit.rglob('*.py'):
  if 'artifacts' not in p.parts:ast.parse(p.read_text(encoding='utf-8-sig'),filename=str(p))
staged={}
for name in subprocess.check_output(['git','diff','--cached','--name-only','-z'],cwd=ws).decode().strip('\0').split('\0'):
 if name.startswith(('outputs/xemu-backend-preserve227/','outputs/xemu-backend-reason228/')):
  data=subprocess.check_output(['git','show',':'+name],cwd=ws);assert data==(ws/name).read_bytes()
  assert '/artifacts/' not in name and '/build-logs/' not in name;staged[name]=hashlib.sha256(data).hexdigest()
subprocess.run(['git','diff','--cached','--check'],cwd=ws,check=True)
subprocess.run(['C:/Python314/python.exe','-B',str(ws/'tools/check-repository.py')],cwd=ws,check=True)
dest.write_text(json.dumps(dict(passed=True,checked_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),source_sha256=sha(Path(__file__)),cases=results,terminal_host_checks_passed=True,staged_byte_pins=staged,limits='Evidence/source review only.227 refused;228 had zero cached surfaces and failed startup/workload. No preserving download, reference retirement, native ownership, acceleration or physical qualification.'),indent=2)+'\n')
print('227/228 independent source/evidence/qualification-scope review PASS')
