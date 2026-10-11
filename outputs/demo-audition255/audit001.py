"""Physical driver/log/cold-integrity verdict; never infer audibility from completion."""
import hashlib,json,pathlib,struct,subprocess,sys
sys.dont_write_bytecode=True
sys.path.insert(0,'/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/python3/dist-packages')
import hivex
k=pathlib.Path(__file__).resolve().parent;repo=k.parents[1];case=sys.argv[1];assert case in ['playback001']
out=k/case;art=k/'artifacts'/case;dest=out/'audit.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
collection=read(out/'collection.json');assert collection['completed']
prior=k/'artifacts'/'before002'
remote='xwnd255'
r=dict(case=case,physical_result=True,audibility_observed=False,physical_audio_qualified=False,hives=[],logs={},new_events={},offline_registry_edits=False)
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
if case=='install001':
    log=lines('install207.log');runner=lines('install-runner207.log')
    r['workload_passed']=required(log,['UPDATE_RESULT 1','UPDATE_ERROR 0','AFTER_SERVICE xwnaci207','INSTALL207_END 0'])
    targets=[s for s in log if s.startswith('TARGET_INSTANCE ')]
    r['workload_passed'] &= log.count('EXACT_TARGET_COUNT 1')==2 and len(targets)==2 and targets[0]==targets[1] and 'VEN_10DE&DEV_01B1&SUBSYS_00000000&REV_B1' in targets[0]
    r['joined_children']=required(runner,['HELPER_JOIN_RESULT 0','HELPER_EXIT 0','INSTALLER_JOIN_RESULT 0','INSTALLER_EXIT 0','NORMAL_RESTART_REQUEST 0','INSTALL_WAIT_RESULT 0','INSTALL_FINAL_RESULT 0'])
else:
    log=lines('audio207.log');rows=[s.split() for s in log];state=lines('state207.log');runner=lines('runner207.log')
    r['workload_passed']=bool(rows) and rows[-1]==['CHANNEL001_END','6','0'] and rows.count(['CHANNEL001_BEGIN','1','1'])==1
    for i in range(6):
        for tag in ['OPEN','PREPARE','WRITE','RESET','UNPREPARE','CLOSE']:r['workload_passed'] &= rows.count([tag,str(i),'0'])==1
        r['workload_passed'] &= rows.count(['DONE_AFTER_RESET',str(i),'1'])==1
        r['workload_passed'] &= rows.count(['PHASE_MASK',str(i),str(i%3+1)])==1 and rows.count(['CYCLE',str(i),'0'])==1
        if True:
            for tag,value in [('DONE_BEFORE_RESET','1'),('POSITION_RESULT','0'),('POSITION_TYPE','2'),('POSITION_SAMPLES','144000')]:r['workload_passed'] &= rows.count([tag,str(i),value])==1
    r['state_passed']=required(state,['ACTUAL_SERVICE xwnaci207','DEVNODE_STATUS_RESULT 0','DEVNODE_PROBLEM 0','TARGET_MODULE_COUNT 1','LEGACY_MODULE_COUNT 0','STATE207_END 0'])
    r['joined_children']=required(runner,['HELPER_JOIN_RESULT 0','HELPER_EXIT 0','STATE_JOIN_RESULT 0','STATE_EXIT 0','PROBE_JOIN_RESULT 0','PROBE_EXIT 0','NORMAL_RESTART_REQUEST 0','INSTALL_WAIT_RESULT 0','INSTALL_FINAL_RESULT 0'])
lines('wizard201.log')
r['normal_shutdown_count']=sum(v['source']=='EventLog' and v['event_id']==6006 for v in r['new_events']['system'])
r['dashboard_return']=read(out/'return.json')['dashboard_return']
a=read(out/'allocation.json');r['allocation_passed']=a['allocation_consistent'] and not a['errors'] and not a['orphan_cluster_count']
r['integrity_passed']=r['allocation_passed'] and collection['protected_files_unchanged'] and collection['startup_restored'] and all(v['sequences_equal'] and v['checksum_valid'] for v in r['hives']) and r['event_history_preserved'] and r['setupapi_history_preserved'] and all(r['typed_state'][n] for n in ['hive_headers_valid','selected_policy_unchanged','no_new_device_disabling','binding_metadata_unchanged'])
r['warnings_errors']=[v for group in r['new_events'].values() for v in group if v['type'] in [1,2]]
r['strict_events_passed']=not r['warnings_errors'] and not r['new_events']['application']
passed=r['workload_passed'] and r['joined_children'] and r['installed_binding']['passed'] and r['installed_binary_matches'] and r['installed_inf_matches'] and r['integrity_passed'] and r['normal_shutdown_count']==1 and r['dashboard_return'] and not r['new_events']['application']
r['scoped_installation_passed']=passed if case=='install001' else False
r['scoped_runtime_passed']=passed and r.get('state_passed',False) if case=='playback001' else False
r['strict_qualification_passed']=passed and r['strict_events_passed']
fields=['source','event_id','type','strings','data_hex']
signature=lambda v:{n:v[n] for n in fields}
prior_errors=read(repo/'outputs/demo-physical253/combined001/audit.json')['warnings_errors']
r['only_documented_boot_errors']=all(signature(v) in [signature(p) for p in prior_errors] for v in r['warnings_errors'])
r['scoped_runtime_passed'] &= r['only_documented_boot_errors']
r['limits']='Physical device/driver/log evidence only. Audible stereo and actual codec output are not inferred. Known unrelated wizard cancellation is not prompt-free installation. Ftdisk49 is never waived.'
dest.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({n:r[n] for n in ['case','workload_passed','joined_children','normal_shutdown_count','integrity_passed','scoped_installation_passed','scoped_runtime_passed','strict_qualification_passed']},indent=2))
