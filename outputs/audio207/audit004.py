"""Cold audio lifecycle audit; never equate forced host closure with guest reboot."""
import contextlib,json,pathlib,subprocess,sys
k=pathlib.Path(__file__).resolve().parent;repo=k.parents[1]
sys.path.insert(0,str(repo/'outputs/video-text-oracle206'))
from common import ColdIO,readers,sha,save,hive,scan,m,STARTUP,HIVES
case=sys.argv[1];assert case in ['candidate003'];out=k/case;art=out/'artifacts'
dest=out/'audit.json';assert not dest.exists()
for name,digest in json.loads((k/'frozen004.json').read_text()).items():
    assert sha(repo/name)==digest,('Frozen input changed',name)
run=repo/('work/runs/nt5-audio207-'+case);assert (run/'cleanup.json').exists()
f=json.loads((out/'fixture.json').read_text());base=pathlib.Path(f['fixture_path_linux']);disk=run/'hdd.qcow2'
assert sha(base)==f['fixture_sha256'] and sha(pathlib.Path(f['parent']))==f['parent_sha256']
r=dict(case=case,physical_access=False,debugger=False,files=[],hives=[],new_events={},logs={})
with contextlib.ExitStack() as stack:
    before,after=[readers(stack.enter_context(ColdIO(p)),p) for p in [base,disk]]
    for name in ['audio207.log','runner207.log','wizard201.log']:
        try:blob=after['F'].read(f['namespace']+'/'+name)
        except KeyError:blob=None
        if blob is not None:(art/name).write_bytes(blob)
        r['logs'][name]=None if blob is None else dict(sha256=m.sha(blob),bytes=len(blob))
    for name,digest in f['protected'].items():
        v,path=name.split('/',1)
        if path.startswith('winnt/system32/config/') or path in ['winnt/setupapi.log','winnt/system32/xwn-video-trace.bin']:continue
        actual=m.sha(after[v].read(path));r['files'].append(dict(path=name,before_sha256=digest,after_sha256=actual,matched=digest==actual))
    r['startup_unchanged']=m.sha(after['F'].read(STARTUP))==f['files']['F/'+STARTUP]
    for name in HIVES:
        p=art/('after-'+name);p.write_bytes(after['F'].read('winnt/system32/config/'+name))
        try:row=hive(p)
        except Exception as exc:row=dict(parsed=False,error=type(exc).__name__)
        r['hives'].append(dict(name=name,**row))
    setup=[]
    for phase,rr in [('before',before),('after',after)]:
        blob=rr['F'].read('winnt/setupapi.log');setup.append(blob);(art/(phase+'-setupapi.log')).write_bytes(blob)
    r['setupapi_history_preserved']=setup[1].startswith(setup[0])
    r['event_history_preserved']=True
    for name,label in [('sysevent.evt','system'),('appevent.evt','application')]:
        pair=[]
        for phase,rr in [('before',before),('after',after)]:
            p=art/(phase+'-'+name);p.write_bytes(rr['F'].read('winnt/system32/config/'+name));d=out/(phase+'-'+label+'-events.json')
            subprocess.run([sys.executable,str(repo/'outputs/native-windows-physical-f/decode-legacy-events.py'),str(p),'--output',str(d)],check=True,stdout=subprocess.DEVNULL)
            pair.append(json.loads(d.read_text())['records'])
        a,b=pair;by={v['record']:v for v in b};r['event_history_preserved'] &= all(by.get(v['record'])==v for v in a)
        boundary=max((v['record'] for v in a),default=0);r['new_events'][label]=[v for v in b if v['record']>boundary]
def text(name):return (art/name).read_text() if (art/name).exists() else ''
log=text('audio207.log');rows=[v.split() for v in log.splitlines()]
r['probe_passed']=bool(rows) and rows[-1]==['AUDIO207_END','12','0']
for i in range(12):
    for tag in ['OPEN','PREPARE','WRITE','RESET','UNPREPARE','CLOSE']:
        r['probe_passed'] &= rows.count([tag,str(i),'0'])==1
    r['probe_passed'] &= rows.count(['DONE_AFTER_RESET',str(i),'1'])==1
    if i%3!=1:
        for tag,value in [('DONE_BEFORE_RESET','1'),('POSITION_RESULT','0'),('POSITION_TYPE','2'),('POSITION_SAMPLES','96000')]:
            r['probe_passed'] &= rows.count([tag,str(i),value])==1
runner=text('runner207.log').splitlines()
r['joined_helper_and_probe']=all(runner.count(s)==1 for s in ['HELPER_JOIN_RESULT 0','HELPER_EXIT 0','PROBE_JOIN_RESULT 0','PROBE_EXIT 0','NORMAL_RESTART_REQUEST 0','INSTALL_WAIT_RESULT 0','INSTALL_FINAL_RESULT 0']) and not any('FAIL' in s or 'BLOCKED' in s for s in runner)
r['normal_shutdown_count']=sum(v['source']=='EventLog' and v['event_id']==6006 for v in r['new_events']['system'])
r['dashboard_return']=json.loads((out/'launch.json').read_text())['cycles'][0].get('dashboard_return') is True
subprocess.run([sys.executable,str(k/'typed-state004.py'),case],check=True)
r['typed_state']=json.loads((out/'device-state.json').read_text())
scan(disk,out/'after/artifacts');a=json.loads((out/'after/allocation.json').read_text())
r['allocation_passed']=a['allocation_consistent'] and not a['errors'] and not a['orphan_cluster_count']
r['integrity_passed']=r['allocation_passed'] and all(v['parsed'] for v in r['hives']) and all(v['matched'] for v in r['files']) and r['startup_unchanged'] and r['event_history_preserved'] and r['setupapi_history_preserved'] and all(r['typed_state'][n] for n in ['hive_headers_valid','selected_policy_unchanged','no_new_device_disabling'])
r['warnings_errors']=[v for group in r['new_events'].values() for v in group if v['type'] in [1,2]]
r['strict_events_passed']=not r['warnings_errors'] and not r['new_events']['application']
try:
    subprocess.run([sys.executable,str(k/'analyze-capture.py'),str(run/'ac97-output.wav'),str(out/'capture.json')],check=True)
    r['capture']=json.loads((out/'capture.json').read_text())
except Exception as exc:r['capture']=dict(passed=False,error=repr(exc))
r['scoped_audio_passed']=r['probe_passed'] and r['joined_helper_and_probe'] and r['capture']['passed'] and r['integrity_passed'] and r['normal_shutdown_count']==1 and r['dashboard_return'] and not r['new_events']['application']
r['strict_qualification_passed']=r['scoped_audio_passed'] and r['strict_events_passed']
r['physical_qualified']=False
save(dest,r)
save(out/'closure.json',dict(closed=True,never_relaunch_or_recollect=True,audit_sha256=sha(dest),cleanup_sha256=sha(run/'cleanup.json'),scoped_audio_passed=r['scoped_audio_passed'],strict_qualification_passed=r['strict_qualification_passed'],physical_access=False))
print(json.dumps({n:r[n] for n in ['probe_passed','joined_helper_and_probe','integrity_passed','normal_shutdown_count','scoped_audio_passed','warnings_errors']},indent=2))
