"""Once-only cold audit of actual222 workload, return and unchanged event gates."""
import contextlib,subprocess,importlib.util
from common import *
case=sys.argv[1];assert case in ['control001','preserve001'];out=k/case;art=out/'artifacts';dest=out/'audit.json';assert not dest.exists()
run=Path('/mnt/e/Codex-private-artifacts/xbox-windows-feasibility/phase240-runs/nt5-phase240-'+case);assert (run/'cleanup.json').exists()
f=read(k/('fixture-'+case+'.json'));base=Path(f['fixture_path_linux']);disk=run/'hdd.qcow2'
assert sha(base)==f['fixture_sha256'] and sha(Path(f['parent']))==f['parent_sha256']
for name,digest in read(k/'emulator-frozen.json').items():assert sha(ws/name)==digest,name
spec=importlib.util.spec_from_file_location('log222',k.parent/'video-resident-context222/analyze-log.py');parser=importlib.util.module_from_spec(spec);spec.loader.exec_module(parser)
spec=importlib.util.spec_from_file_location('ret224',k.parent/'video-fifo-retirement224/analyze-retirement.py');ret=importlib.util.module_from_spec(spec);spec.loader.exec_module(ret)
sys.path.insert(0,str(k.parent/'video-boot-layout219'));from runner_analysis import helper
r=dict(physical_access=False,debugger=True,gpu_reads=True,gpu_writes=False,gpu_ownership_qualified=False,files=[],hives=[],new_events={})
with contextlib.ExitStack() as stack:
    before,after=[readers(stack.enter_context(ColdIO(p)),p) for p in [base,disk]]
    logs={}
    for name in ['result.log','wizard201.log','retirement.log']:
        try:data=after['F'].read('xwnret224/'+name);(art/name).write_bytes(data)
        except KeyError:data=None
        logs[name]=data
    r['workload']=parser.analyze(logs['result.log']);r['retirement']=ret.analyze(logs['retirement.log'],True)
    try:r['wizard']=helper(logs['wizard201.log'],1)
    except (AssertionError,ValueError,UnicodeError,TypeError) as e:r['wizard']=dict(passed=False,error=repr(e))
    for name,digest in f['protected'].items():
        v,path=name.split('/',1)
        if path.startswith('winnt/system32/config/') or path in ['winnt/setupapi.log','winnt/system32/xwn-video-trace.bin']:continue
        actual=m.sha(after[v].read(path));r['files'].append(dict(path=name,expected_sha256=digest,actual_sha256=actual,matched=digest==actual))
    r['startup_unchanged']=m.sha(after['F'].read(STARTUP))==f['files']['F/'+STARTUP]
    for name in HIVES:
        p=art/('after-'+name);p.write_bytes(after['F'].read('winnt/system32/config/'+name))
        try:row=hive(p)
        except Exception as e:row=dict(parsed=False,error=repr(e))
        r['hives'].append(dict(name=name,**row))
    for phase,rr in [('before',before),('after',after)]:
        (art/(phase+'-setupapi.log')).write_bytes(rr['F'].read('winnt/setupapi.log'))
    r['setupapi_history_preserved']=(art/'after-setupapi.log').read_bytes().startswith((art/'before-setupapi.log').read_bytes())
    r['event_history_preserved']=True
    for name,label in [('sysevent.evt','system'),('appevent.evt','application')]:
        pair=[]
        for phase,rr in [('before',before),('after',after)]:
            p=art/(phase+'-'+name);p.write_bytes(rr['F'].read('winnt/system32/config/'+name));d=out/(phase+'-'+label+'-events.json')
            subprocess.run([sys.executable,str(k.parent/'native-windows-physical-f/decode-legacy-events.py'),str(p),'--output',str(d)],check=True,stdout=subprocess.DEVNULL);pair.append(read(d)['records'])
        by={v['record']:v for v in pair[1]};r['event_history_preserved'] &= all(by.get(v['record'])==v for v in pair[0])
        boundary=max((v['record'] for v in pair[0]),default=0);r['new_events'][label]=[v for v in pair[1] if v['record']>boundary]
subprocess.run([sys.executable,str(k/'typed-state.py'),case],check=True);r['typed_state']=read(out/'device-state.json')
scan(disk,art);a=read(out/'allocation.json');r['allocation_passed']=a['allocation_consistent'] and not a['errors'] and not a['orphan_cluster_count']
r['integrity_passed']=r['allocation_passed'] and r['startup_unchanged'] and all(v['matched'] for v in r['files']) and all(v['parsed'] for v in r['hives']) and r['setupapi_history_preserved'] and r['event_history_preserved'] and all(r['typed_state'][v] for v in ['hive_headers_valid','selected_policy_unchanged','no_new_device_disabling'])
r['warnings_errors']=[v for group in r['new_events'].values() for v in group if v['type'] in [1,2]]
r['strict_events_passed']=not r['warnings_errors'] and not r['new_events']['application']
r['normal_shutdown_count']=sum(v['source']=='EventLog' and v['event_id']==6006 for v in r['new_events']['system'])
r['dashboard_return']=(read(out/'launch.json')['cycles'][0].get('dashboard_return') is True) if (out/'launch.json').exists() else False
r['windows_launch_record_exists']=(out/'launch.json').exists()
r['host_exit']=read(run/'host-exit.json')
r['orderly_host_exit_passed']=r['host_exit']['passed']
r['cpu_scope_passed']=r['orderly_host_exit_passed'] and r['workload']['passed'] and r['wizard']['passed'] and r['integrity_passed'] and r['normal_shutdown_count']==1 and r['dashboard_return'] and not r['new_events']['application'] and not any(v['source']=='Application Popup' for v in r['new_events']['system'])
r['observation_scope_passed']=r['cpu_scope_passed'] and r['retirement']['passed']
r['strict_qualification_passed']=r['observation_scope_passed'] and r['strict_events_passed']
r['handoff_trace']=read(out/'trace.json')
r['guest_gpu_command_writes']=False
r['backend_vram_compared_bytes']=r['handoff_trace'].get('preserve_result',{}).get('bytes',0)
r['backend_refusal_reason']=r['handoff_trace'].get('preserve_result',{}).get('reason')
r['guest_trace_scope_passed']=r['observation_scope_passed'] and r['handoff_trace']['passed'] and r['handoff_trace']['closed'] and r['handoff_trace'].get('guest_resumed') and not r['handoff_trace']['remaining_breakpoints']
r['strict_qualification_passed'] &= r['guest_trace_scope_passed']
r['dirty_surface_coverage']=r['handoff_trace'].get('dirty_surface_coverage',False)
r['publication_contract_qualified']=False
r['backend_preservation_scope_passed']=r['guest_trace_scope_passed'] and r['handoff_trace'].get('preservation',{}).get('preservation_scope_passed',False)
r['backend_preservation_qualified']=False
r['publication_limit']='239 pre-snapshot, optional bounded existing232 preservation and RAM captures at pinned Xromwell entry. Internal complete byte comparison is not reference retirement, native ownership or hardware qualification.'
r['strict_qualification_passed'] &= r['backend_preservation_qualified']
r.update(ordinary_qualified=False,physical_qualified=False,native_deferred_cleanup_qualified=False,
         limits='Guest239 debugger preservation experiment using unchanged238 emulator and224 CPU manager. Phase tuple and loader entry pins are separate from renderer-reference retirement, producer close, native permit, physical acceleration, device merge or all-file-content qualification. All warning/error events retained as strict failures.')
save(dest,r);save(out/'closure.json',dict(closed=True,never_relaunch_or_recollect=True,audit_sha256=sha(dest),cleanup_sha256=sha(run/'cleanup.json'),cpu_scope_passed=r['cpu_scope_passed'],guest_trace_scope_passed=r['guest_trace_scope_passed'],observation_scope_passed=r['observation_scope_passed'],strict_qualification_passed=r['strict_qualification_passed'],physical_access=False))
print(json.dumps({n:r[n] for n in ['observation_scope_passed','cpu_scope_passed','retirement','integrity_passed','normal_shutdown_count','warnings_errors']},indent=2))
