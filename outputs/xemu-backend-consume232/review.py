"""Verify closed232 refusal, host adapters, source pins and staged exact bytes."""
import ast,datetime,hashlib,json,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'review001.json';assert not dest.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
for n,digest in read(k/'emulator-frozen.json').items():assert sha(ws/n)==digest,n
h=read(k/'trace001/host-state.json');a=read(k/'trace001/audit.json');t=read(k/'trace001/trace.json');c=read(k/'trace001/closure.json');q=read(k/'consume-review001.json')
assert h['closed'] and h['cleanup_record_exists'] and c['closed'] and c['never_relaunch_or_recollect']
assert all(h[n]==0 for n in ['runner_exit_code','observer_exit_code','tracer_exit_code','audit_exit_code'])
assert a['cpu_scope_passed'] and a['observation_scope_passed'] and a['integrity_passed']
assert a['normal_shutdown_count']==1 and a['dashboard_return']
assert len(read(k/'trace001/launch.json')['cycles'])==1
assert len(a['warnings_errors'])==1 and a['warnings_errors'][0]['source']=='Ftdisk' and a['warnings_errors'][0]['event_id']==49
assert not a['new_events']['application']
for n in ['strict_qualification_passed','backend_preservation_qualified','ordinary_qualified','physical_qualified','publication_contract_qualified']:assert not a[n]
assert t['closed'] and t['physical_mode_restored'] and t['guest_resumed'] and not t['remaining_breakpoints']
assert t['reserved_bytes_unchanged'] and not t['passed'] and not t['dirty_surface_coverage']
p=t['preserve_result'];assert p['state']==4 and p['reason']==20 and p['tuple_published']==1 and p['publication_version']==232
assert p['consume_stop']==4 and p['consume_words']==p['consume_steps']==0
assert p['wait_before']==p['wait_after']==2
assert p['surfaces']==p['dirty']==p['downloaded']==p['bytes']==p['native_grant']==p['references_retired']==0
assert q['passed'] and q['raw_read_bytes']==212992 and q['trace_sha256']==sha(k/'trace001/trace.json')
assert q['waits']=={'before':['nop'],'after':['nop']} and not q['actual_words_consumed']
g=q['phases']['gate'];assert not g['get_equals_put'] and g['parser_method_count']==g['parser_error']==0
assert q['phases']['request']==g and p['gate1']-p['gate0']==66240
alloc=read(k/'trace001/allocation.json')
assert alloc['capture_complete'] and alloc['directories']==320 and alloc['live_entries']-alloc['directories']==6723
assert alloc['directory_clusters']==321 and alloc['orphan_cluster_count']==0 and not alloc['errors']
assert len(a['hives'])==5 and all(v['parsed'] for v in a['hives'])
for record,script,test,include in [('consume-test001.json','test-consume.py','test-consume.c','pusher-actual.inc'),('publication-test001.json','test-publication.py','test-publication.c','publication-actual.inc')]:
    v=read(k/record);assert v['passed'] and len(v['runs'])==2
    assert v['source_sha256']==sha(k/script) and v['test_sha256']==sha(k/test)
    folder=k/'artifacts'/record.removesuffix('.json')
    key='actual_parser_sha256' if script=='test-consume.py' else 'actual_helper_sha256'
    assert v[key]==sha(folder/include)
    assert all(row['exit_code']==0 and not row['stderr'] for row in v['runs'])
assert read(k/'guard-test001.json')['passed'] and read(k/'guard-test001.json')['checks']==72
b=read(k/'build001.json');assert b['passed'] and b['borrowed_sources_restored'] and len(b['original_sources'])==6
pins=read(k/'candidate001-source-pins.json')
assert b['source_manifest_sha256']==sha(k/'candidate001-source-pins.json')
assert b['patch_sha256']==sha(k/'consume232-build001.patch')
assert b['executable_sha256']==sha(k/'artifacts/build001/xemu-preserve227.exe')
for f in (k/'artifacts/build001/source').rglob('*'):
    if f.is_file():assert sha(f)==pins[f.relative_to(k/'artifacts/build001/source').as_posix()]
wait=read(k/'wait-source001.json');assert wait['passed'] and wait['compiled_source_sha256']==pins[wait['compiled_source']]
assert wait['compiled_source_sha256']==sha(k/wait['artifact']) and not wait['qualification']
for f in k.glob('*.py'):ast.parse(f.read_text(),filename=str(f))
for pid in [h[n] for n in ['controller_pid','runner_pid','tracer_pid','observer_pid']]:
    result=subprocess.run(['pwsh','-NoProfile','-Command',f'if(Get-Process -Id {pid} -ErrorAction SilentlyContinue){{exit 1}}'],capture_output=True)
    assert result.returncode==0,('Owned PID still exists',pid)
staged={}
for n in subprocess.check_output(['git','diff','--cached','--name-only','-z'],cwd=ws).decode().strip('\0').split('\0'):
    if n.startswith('outputs/xemu-backend-consume232/'):
        blob=subprocess.check_output(['git','show',':'+n],cwd=ws);assert blob==(ws/n).read_bytes(),n
        staged[n]=hashlib.sha256(blob).hexdigest()
assert staged
subprocess.run(['git','diff','--cached','--check'],cwd=ws,check=True)
subprocess.run(['C:/Python314/python.exe','-B',str(ws/'tools/check-repository.py')],cwd=ws,check=True)
dest.write_text(json.dumps(dict(passed=True,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),source_sha256=sha(Path(__file__)),staged_byte_pins=staged,frozen_inputs_unchanged=True,owned_root_sessions_closed=True,physical_access=False,
    scope='Bounded actual-parser host tests and actual wait refusal; CPU/cold scope passed. Guest consumption, dirty readback, reference retirement and native ownership unqualified. Peer repeated-boot storage failure remains separate.'),indent=2)+'\n')
print('232 closed refusal/source pins/host tests/staged bytes and repository checks PASS')
