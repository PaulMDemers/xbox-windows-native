"""Physical driver/log/cold-integrity verdict; never infer audibility from completion."""
import hashlib,json,pathlib,struct,subprocess,sys
sys.dont_write_bytecode=True
sys.path.insert(0,'/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/python3/dist-packages')
import hivex
k=pathlib.Path(__file__).resolve().parent;repo=k.parents[1];case=sys.argv[1];assert case in ['combined001']
out=k/case;art=k/'artifacts'/case;dest=out/'audit.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
collection=read(out/'collection.json');assert collection['completed']
prior=k/'artifacts'/'before002'
remote='xwnd253'
r=dict(case=case,physical_result=True,audibility_observed=False,physical_audio_qualified=False,hives=[],logs={},new_events={},offline_registry_edits='exact two video tokens, audio unchanged')
for path,row in collection['files'].items():
    if row is not None:assert sha(art/path.lstrip('/'))==row['sha256'],'Collected bytes changed: '+path
for name in ['system','software','sam','security','default']:
    p=art/'F/winnt/system32/config'/name;data=p.read_bytes();h=hivex.Hivex(str(p));todo=[h.root()];seen=set();count=0
    while todo:
        n=todo.pop();assert n not in seen;seen.add(n);h.node_name(n)
        for v in h.node_values(n):h.value_key(v);h.value_value(v);count+=1
        todo.extend(h.node_children(n))
    a,b=struct.unpack_from('<II',data,4);c=0
    for at in range(0,508,4):c ^= struct.unpack_from('<I',data,at)[0]
    c=0xfffffffe if c==0xffffffff else 1 if c==0 else c
    r['hives'].append(dict(name=name,sha256=sha(p),keys=len(seen),values=count,sequences_equal=a==b,checksum_valid=c==struct.unpack_from('<I',data,508)[0]))
r['event_history_preserved']=True
for name,label in [('sysevent.evt','system'),('appevent.evt','application')]:
    pair=[]
    for phase,root in [('before',prior),('after',art)]:
        output=art/(phase+'-'+label+'-events.json');assert not output.exists()
        subprocess.run([sys.executable,str(repo/'outputs/native-windows-physical-f/decode-legacy-events.py'),str(root/'F/winnt/system32/config'/name),'--output',str(output)],check=True,stdout=subprocess.DEVNULL)
        pair.append(read(output)['records'])
    a,b=pair;by={v['record']:v for v in b};r['event_history_preserved'] &= all(by.get(v['record'])==v for v in a)
    boundary=max((v['record'] for v in a),default=0);r['new_events'][label]=[v for v in b if v['record']>boundary]
r['setupapi_history_preserved']=(art/'F/winnt/setupapi.log').read_bytes().startswith((prior/'F/winnt/setupapi.log').read_bytes())
for script in ['typed-state001.py','installed-binding001.py']:subprocess.run([sys.executable,str(k/script),case],check=True)
r['typed_state']=read(out/'device-state.json');r['installed_binding']=read(out/'installed-binding.json')
r['installed_binary_matches']=(art/'F/winnt/system32/drivers/xwnaci207.sys').exists() and sha(art/'F/winnt/system32/drivers/xwnaci207.sys')=='c5736457d9f4b7c6dafc730eb19bc0eda6c6820cee8e21580d357708df36cd75'
r['installed_inf_matches']=False
if r['installed_binding']['passed']:
    name=r['installed_binding']['driver_class']['infpath'][0];assert '/' not in name and '\\' not in name and '..' not in name
    r['installed_inf_matches']=sha(art/'F/winnt/inf'/name)==sha(repo/'outputs/audio207/xwnaci207.inf')
def lines(name):
    p=art/'F'/remote/name
    if not p.exists():return []
    r['logs'][name]=dict(sha256=sha(p),bytes=p.stat().st_size);return p.read_text().splitlines()
def required(rows,expected):return all(rows.count(s)==1 for s in expected) and not any('FAIL' in s or 'BLOCKED' in s for s in rows)
audio=lines('audio207.log');rows=[s.split() for s in audio];state=lines('state207.log');attempt=lines('attempt.log')
r['audio_probe_passed']=bool(rows) and rows[-1]==['CHANNEL001_END','6','0'] and rows.count(['CHANNEL001_BEGIN','1','1'])==1
for i in range(6):
    for tag in ['OPEN','PREPARE','WRITE','RESET','UNPREPARE','CLOSE']:r['audio_probe_passed'] &= rows.count([tag,str(i),'0'])==1
    for tag,value in [('DONE_AFTER_RESET','1'),('DONE_BEFORE_RESET','1'),('POSITION_RESULT','0'),('POSITION_TYPE','2'),('POSITION_SAMPLES','144000'),('PHASE_MASK',str(i%3+1)),('CYCLE','0')]:r['audio_probe_passed'] &= rows.count([tag,str(i),value])==1
r['audio_state_passed']=required(state,['ACTUAL_SERVICE xwnaci207','DEVNODE_STATUS_RESULT 0','DEVNODE_PROBLEM 0','TARGET_MODULE_COUNT 1','LEGACY_MODULE_COUNT 0','STATE207_END 0'])
tags=['AUDIO_STATE_JOIN 0','AUDIO_STATE_EXIT 0','AUDIO_PROBE_JOIN 0','AUDIO_PROBE_EXIT 0']
r['audio_children_joined']=[v for v in attempt if v.startswith('AUDIO_')]==tags
sys.path.insert(0,str(repo/'outputs/video-text-oracle206'))
from runner_analysis import analyze as runner
from sample_analysis import analyze
from dib_analysis import analyze as dib
from timing_analysis import timing
from window_analysis import window
from text_analysis import analyze as text_analysis
def blob(name):
    p=art/'F'/remote/name
    return p.read_bytes() if p.exists() else None
snapshots=[blob(n) for n in ['setup-before.log','setup-after.log']]
r['boundary_analysis']=runner('\n'.join(v for v in attempt if not v.startswith('AUDIO_')),snapshots,blob('wizard201.log'),0)
r['setup_gate_passed']=r['boundary_analysis']['idle_branch_passed']
texts=[None if blob('sample%d/gdi-baseline.txt'%i) is None else blob('sample%d/gdi-baseline.txt'%i).decode('ascii') for i in range(5)]
r['samples']=[analyze(v) for v in texts];r['dib_samples']=[dib(v,0) for v in texts]
r['phase_samples']=[timing(v,0) for v in texts];r['window_samples']=[window(v,0) for v in texts];r['text_samples']=[text_analysis(v,1) for v in texts]
r['actual_caps']=r['samples'][0]['actual_caps'];r['actual_modes']=r['samples'][0]['actual_modes']
r['caps_consistent']=all(v['actual_caps']==r['actual_caps'] and v['actual_modes']==r['actual_modes'] for v in r['samples'])
r['display_workload_passed']=r['caps_consistent'] and all(v['probe_passed'] and v['copy_checks_passed'] and v['loop_coverage'] and v['counters_passed'] for v in r['samples']) and all(v['passed'] for group in ['dib_samples','phase_samples','window_samples','text_samples'] for v in r[group])
r['checkpoint_history_preserved']=all(v is not None and v.startswith((prior/'F/winnt/setupapi.log').read_bytes()) and (art/'F/winnt/setupapi.log').read_bytes().startswith(v) for v in snapshots)
r['warnings_errors']=[v for group in r['new_events'].values() for v in group if v['type'] in [1,2]]
r['strict_events_passed']=not r['warnings_errors'] and not r['new_events']['application']
r['combined_interval_passed']=False
def ft(line,label):
    parts=line.split();assert len(parts)==3 and parts[0]==label
    lo,hi=map(int,parts[1:]);assert 0<=lo<=0xffffffff and 0<=hi<=0xffffffff
    return (hi<<32)|lo
if r['setup_gate_passed'] and r['audio_children_joined']:
    starts=[(i,ft(v,'CHECKPOINT_TIME')) for i,v in enumerate(attempt) if v.startswith('CHECKPOINT_TIME ')]
    ends=[(i,ft(v,'MEASUREMENT_END_TIME')) for i,v in enumerate(attempt) if v.startswith('MEASUREMENT_END_TIME ')]
    assert len(starts)==2 and len(ends)==1
    indices=[attempt.index(v) for v in tags];assert all(attempt.count(v)==1 for v in tags)
    assert starts[0][0]<indices[0] and indices==list(range(indices[0],indices[0]+4)) and indices[-1]<ends[0][0]
    assert attempt[indices[-1]+1].startswith('MEASUREMENT_START_TIME ') and 0<starts[0][1]<ends[0][1]
    interval=[starts[0][1]//10000000-11644473600,ends[0][1]//10000000-11644473600]
    r['combined_interval_unix']=interval
    r['interval_warning_errors']=[v for v in r['warnings_errors'] if interval[0]-1<=v['generated_unix']<=interval[1]+1]
    r['combined_interval_passed']=not r['interval_warning_errors']
r['normal_shutdown_count']=sum(v['source']=='EventLog' and v['event_id']==6006 for v in r['new_events']['system'])
r['dashboard_return']=read(out/'return.json')['dashboard_return']
a=read(out/'allocation.json');r['allocation_passed']=a['allocation_consistent'] and not a['errors'] and not a['orphan_cluster_count']
r['integrity_passed']=r['allocation_passed'] and collection['protected_files_unchanged'] and collection['startup_restored'] and all(v['sequences_equal'] and v['checksum_valid'] for v in r['hives']) and r['event_history_preserved'] and r['setupapi_history_preserved'] and all(r['typed_state'][n] for n in ['hive_headers_valid','selected_policy_unchanged','no_new_device_disabling','binding_metadata_unchanged'])
trace=(art/'F/winnt/system32/xwn-video-trace.bin').read_bytes();assert len(trace)==4096 and trace[:16]==b'XWN-VID-TRACE01\n'
count,dropped=struct.unpack_from('<II',trace,16);assert count<=254
r['shared_events']=[list(struct.unpack_from('<4I',trace,32+i*16)) for i in range(count) if struct.unpack_from('<I',trace,32+i*16)[0] in [0x30,0x31,0x32]]
acquires=[v for v in r['shared_events'] if v[0]==0x30]
r['shared_acquire_success']=bool(acquires) and dropped==0 and all(v[1]==0 and v[2]>=0x80000000 and v[2]%4096==0 and v[3]>0 for v in acquires) and all(v[1]==0 for v in r['shared_events'])
fields=['audio_probe_passed','audio_state_passed','audio_children_joined','setup_gate_passed','display_workload_passed','checkpoint_history_preserved','combined_interval_passed','integrity_passed','dashboard_return','shared_acquire_success','installed_binary_matches','installed_inf_matches']
r['scoped_combined_passed']=all(r[n] for n in fields) and r['installed_binding']['passed'] and r['normal_shutdown_count']==1 and not r['new_events']['application'] and not any(v['source']=='Application Popup' for v in r['new_events']['system'])
r['strict_qualification_passed']=r['scoped_combined_passed'] and r['strict_events_passed']
r['release_qualified']=False
r['limits']='Physical combined workload and cold integrity scope; no inferred audibility, stereo routing, desktop FPS, GPU acceleration, 1080i or strict release claim. Whole-boot Ftdisk49 remains failure. Actual bound drivers retained only if scoped candidate accepted.'
dest.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({n:r[n] for n in ['scoped_combined_passed','strict_qualification_passed',*fields]},indent=2))
