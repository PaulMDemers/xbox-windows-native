"""Independent raw-tail and actual call-pair review of closed forced-TRUE003."""
import hashlib,json,pathlib
k=pathlib.Path(__file__).resolve().parent;ws=k.parents[1]
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
dest=k/'pair-verification003.json';assert not dest.exists()
for fn in ['emulator-frozen.json','frozen002.json','frozen003.json']:
    for name,digest in read(k/fn).items():assert sha(ws/name)==digest,(fn,name)
expected=bytes((73*(i%256)+19*((i//256)%256)+91)%256 for i in range(86016))
stages=['seeded_TRUE_entry','before-HAL-callback','after-HAL-callback','ResetDisplay-return','VidResetDisplay-return']
results=[];callback_bodies=[];raw_bytes=0
for case in ['control003','candidate003']:
    out=k/case;trace=read(out/'trace.json');a=read(out/'audit.json');host=read(out/'host-state.json');closure=read(out/'closure.json')
    run=pathlib.Path('E:/Codex-private-artifacts/xbox-windows-feasibility/bootguard223-runs')/('nt5-bootguard223-'+case)
    assert trace['passed'] and trace['closed'] and trace['guest_resumed'] and not trace['remaining_breakpoints']
    assert trace['host_forced_setmode'] and trace['natural_boot_argument']==0 and trace['execution_argument']==1
    assert len(trace['argument_mutations'])==2
    for m in trace['argument_mutations']:
        before=bytes.fromhex(m['before_hex']);after=bytes.fromhex(m['after_hex'])
        assert len(before)==len(after)==4 and before[0]==0 and after[0]==1 and before[1:]==after[1:]
    assert [g['stage'] for g in trace['guards']]==stages
    for row in trace['guards']:
        p=out/'artifacts'/(row['stage']+'-tail.bin');data=p.read_bytes();assert len(data)==86016 and sha(p)==row['sha256'];raw_bytes+=len(data)
        target=bytes(86016) if case=='control003' and row['stage'].endswith('-return') else expected
        assert data==target,(case,row['stage'])
        p=out/'artifacts'/(row['stage']+'-saved-rows.bin');assert sha(p)==row['saved_rows_sha256'] and p.stat().st_size==8960
        if row['stage'].endswith('-return'):assert p.read_bytes()==bytes(8960)
        assert row['state']==trace['before_seed']
    events=trace['events'];assert len(events)==5
    assert [e['kind'] for e in events]==['natural_FALSE_entry_forced_TRUE_diagnostic','HAL_callback_call_site','HAL_callback_return_site','actual_paired_return','actual_paired_return']
    assert events[1]['registers']['ESP']==events[2]['registers']['ESP']
    callback_bodies.append(events[1]['target_body_sha256'])
    assert hashlib.sha256(bytes.fromhex(events[1]['target_body_hex'])).hexdigest()==callback_bodies[-1]
    for event in events[3:]:assert event['registers']['ESP']==event['pair']['stack']+event['pair']['delta']
    for i,pte in enumerate(trace['tail_mapping']['ptes']):assert pte&1 and pte&16 and pte&0xfffff000==0x3feb000+i*4096
    assert host['closed'] and all(host[n]==0 for n in ['runner_exit','tracer_exit','supervisor_exit','audit_exit'])
    assert sha(run/'monitor-ready.json')==host['monitor_ready_sha256'] and sha(run/'instance.json')==host['instance_sha256']
    assert sha(out/'audit.json')==closure['audit_sha256'] and sha(run/'cleanup.json')==closure['cleanup_sha256']
    launch=read(out/'launch.json');assert len(launch['cycles'])==1 and launch['cycles'][0]['status']=='accepted' and launch['cycles'][0]['dashboard_return']
    assert a['boot_guard_passed'] and a['cpu_scope_passed'] and a['integrity_passed'] and a['normal_shutdown_count']==1
    assert not a['ordinary_qualified'] and not a['physical_qualified'] and not a['strict_qualification_passed']
    assert len(a['warnings_errors'])==1 and a['warnings_errors'][0]['source']=='Ftdisk' and a['warnings_errors'][0]['event_id']==49
    assert not a['new_events']['application'] and not any(e['source']=='Application Popup' for e in a['new_events']['system'])
    assert len(a['hives'])==5 and all(h['parsed'] for h in a['hives']) and len(a['files'])==28 and all(f['matched'] for f in a['files'])
    alloc=read(out/'allocation.json');assert alloc['allocation_consistent'] and not alloc['errors'] and not alloc['orphan_cluster_count']
    results.append(dict(case=case,forced_TRUE_guard_passed=True,cpu_scope_passed=True,strict_qualification_passed=False,
        ordinary_qualified=False,physical_qualified=False,actual_events=5,tail_snapshots=5,
        closed_utc=host['closed_utc'],audit_sha256=sha(out/'audit.json'),trace_sha256=sha(out/'trace.json')))
assert callback_bodies[0]==callback_bodies[1]
result=dict(passed=True,physical_access=False,host_forced_setmode=True,natural_TRUE_qualified=False,
    gpu_ownership_qualified=False,raw_tail_bytes_checked=raw_bytes,HAL_callback_bodies_equal=True,cases=results,
    limits='Actual compiled TRUE branch exercised by two debugger BOOLEAN byte changes plus tail seed; not a naturally requested TRUE boot, ordinary qualification, physical UMA/coherence proof or GPU grant.')
dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps({n:result[n] for n in ['passed','raw_tail_bytes_checked','natural_TRUE_qualified','gpu_ownership_qualified']}))
