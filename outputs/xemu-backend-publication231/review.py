"""Review closed231 raw telemetry, actual atomic tests and staged source bytes."""
import ast,datetime,hashlib,json,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'review001.json';assert not dest.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
for n,h in read(k/'emulator-frozen.json').items():assert sha(ws/n)==h,n
h=read(k/'trace001/host-state.json');a=read(k/'trace001/audit.json');t=read(k/'trace001/trace.json');c=read(k/'trace001/closure.json');q=read(k/'queue-review001.json')
assert h['closed'] and h['cleanup_record_exists'] and c['closed'] and c['never_relaunch_or_recollect']
assert all(h[n]==0 for n in ['runner_exit_code','observer_exit_code','tracer_exit_code','audit_exit_code'])
assert a['cpu_scope_passed'] and a['observation_scope_passed'] and a['integrity_passed']
assert a['normal_shutdown_count']==1 and a['dashboard_return']
assert len(a['warnings_errors'])==1 and a['warnings_errors'][0]['source']=='Ftdisk' and a['warnings_errors'][0]['event_id']==49
assert not a['new_events']['application']
for n in ['strict_qualification_passed','backend_preservation_qualified','ordinary_qualified','physical_qualified','publication_contract_qualified']:assert not a[n]
assert t['closed'] and t['physical_mode_restored'] and t['guest_resumed'] and not t['remaining_breakpoints']
assert t['reserved_bytes_unchanged'] and not t['passed'] and not t['dirty_surface_coverage']
p=t['preserve_result'];assert p['state']==4 and p['reason']==1 and p['tuple_published']==1 and p['publication_version']==231
assert p['surfaces']==p['dirty']==p['downloaded']==p['bytes']==p['native_grant']==p['references_retired']==0
assert q['passed'] and q['raw_read_bytes']==212992 and q['trace_sha256']==sha(k/'trace001/trace.json')
g=q['phases']['gate'];assert not g['get_equals_put'] and g['parser_method_count']==g['parser_error']==0
assert q['phases']['request']==g and p['gate1']-p['gate0']==66240
assert read(k/'publication-test003.json')['passed'] and not read(k/'publication-test001.json')['passed'] and not read(k/'publication-test002.json')['passed']
assert read(k/'decode-failure001.json')['source_sha256']==sha(k/'decode-queue.py')
for f in k.glob('*.py'):ast.parse(f.read_text(),filename=str(f))
for pid in [h[n] for n in ['controller_pid','runner_pid','tracer_pid','observer_pid']]:
    result=subprocess.run(['pwsh','-NoProfile','-Command',f'if(Get-Process -Id {pid} -ErrorAction SilentlyContinue){{exit 1}}'],capture_output=True)
    assert result.returncode==0,('Owned PID still exists',pid)
staged={}
for n in subprocess.check_output(['git','diff','--cached','--name-only','-z'],cwd=ws).decode().strip('\0').split('\0'):
    if n.startswith('outputs/xemu-backend-publication231/'):
        blob=subprocess.check_output(['git','show',':'+n],cwd=ws);assert blob==(ws/n).read_bytes(),n
        staged[n]=hashlib.sha256(blob).hexdigest()
assert staged
subprocess.run(['git','diff','--cached','--check'],cwd=ws,check=True)
subprocess.run(['C:/Python314/python.exe','-B',str(ws/'tools/check-repository.py')],cwd=ws,check=True)
dest.write_text(json.dumps(dict(passed=True,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),source_sha256=sha(Path(__file__)),staged_byte_pins=staged,frozen_inputs_unchanged=True,owned_root_sessions_closed=True,physical_access=False,scope='Actual ordered terminal telemetry and refusal; CPU/cold scope passed. Consuming drain, dirty readback, GPU visibility, reference retirement and native ownership remain unqualified.'),indent=2)+'\n')
print('231 closed queue evidence/atomic tests/frozen/staged exact bytes PASS')
