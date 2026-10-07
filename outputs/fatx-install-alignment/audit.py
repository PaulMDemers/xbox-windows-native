"""Cold audit of targeted GPU wizard completion: idle restart, selected binaries, hives and event deltas."""
import contextlib,importlib,json,re,subprocess,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'fatx-mapped-eof'))
from coldio import ColdIO
k=Path(__file__).resolve().parent;ws=k.parents[1]
sys.path.insert(0,str(ws/'outputs/native-windows-paint-save'));m=importlib.import_module('prepare-fixture')
sys.path.insert(0,'/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/python3/dist-packages')
import hivex
case=sys.argv[1];assert case in ['001','002']
out=k/case;art=out/'artifacts';art.mkdir(parents=True,exist_ok=True)
assert not (out/'audit.json').exists(), 'Preserve completed audit'
fixture=json.loads((k/('fixture-'+case+'.json')).read_text())
base=ws/'outputs/native-windows-fatx-forensics/artifacts'/fixture.get('fixture_name','fatx0098-soak-'+case+'.qcow2')
run=ws/('work/runs/nt5-fatx-install-alignment-'+case)
assert (run/'cleanup.json').exists() and m.filehash(base)==fixture['fixture_sha256']
m.fatx.PARTITIONS['F']=(15633072*512,472764096*512)
r=dict(scope=__doc__,case=case,physical_access=False,payloads=[],hives=[],new_events={})
with contextlib.ExitStack() as stack:
    readers=[]
    for disk in [base,run/'hdd.qcow2']:
        io=stack.enter_context(ColdIO(disk));readers.append({v:m.Writer(io,m.fatx.open_partition(io,disk,v)) for v in ['E','F']})
    before,after=readers
    for row in fixture['payloads']+fixture['preserved_payloads']:
        if row['path']=='winnt/system32/xwn-video-trace.bin':continue
        actual=m.sha(after['F'].read(row['path']))
        r['payloads'].append(dict(path=row['path'],sha256=actual,matched=actual==row['sha256']))
    r['runtime_binary_checks']=[]
    identities=json.loads((k.parent/'shutdown-popup-workload/site-review.json').read_text())
    identities['binaries'].update(json.loads((k.parent/'shutdown-popup-workload/caller-review.json').read_text())['binaries'])
    pairs=[('winnt/system32/'+n,v['sha256']) for n,v in identities['binaries'].items()]+[('winnt/system32/ntoskrnl.exe',identities['kernel_sha256'])]
    for path,sha in pairs:
        first=m.sha(before['F'].read(path));last=m.sha(after['F'].read(path))
        r['runtime_binary_checks'].append(dict(path=path,before_sha256=first,after_sha256=last,matched=first==last==sha))
    r['baseline_checks']={}
    for letter,path in [('F','winnt/system32/drivers/xwnfatx.sys'),('E','Applications/XWNFBoot/loader/halxboxnt5.dll'),('E','Applications/XWNFBoot/default.xbe'),('E','Applications/XWNFBoot/freeldr.sys')]:
        r['baseline_checks'][letter+'/'+path]=before[letter].read(path)==after[letter].read(path)
    r['fatx_exact']=m.sha(after['F'].read('winnt/system32/drivers/xwnfatx.sys'))==fixture['fatx_sha256']
    r['storage_workload_not_run']=True
    for path in ['xwns98/result.log','xwns98/matched.log']:
        for reader in [before,after]:
            try:reader['F'].read(path)
            except KeyError:pass
            else:r['storage_workload_not_run']=False
    for name in ['system','software','default','sam','security']:
        data=after['F'].read('winnt/system32/config/'+name);path=art/('after-'+name);path.write_bytes(data)
        h=hivex.Hivex(str(path));todo=[h.root()];seen=set();values=0
        while todo:
            node=todo.pop();assert node not in seen;seen.add(node)
            for v in h.node_values(node):h.value_key(v);h.value_value(v);values+=1
            todo.extend(h.node_children(node))
        r['hives'].append(dict(name=name,sha256=m.sha(data),keys=len(seen),values=values,parsed=True))
    known=[]
    for name,label in [('sysevent.evt','system'),('appevent.evt','application')]:
        decoded=[]
        for prefix,readers in [('before',before),('after',after)]:
            path=art/(prefix+'-'+name);path.write_bytes(readers['F'].read('winnt/system32/config/'+name))
            dest=out/(prefix+'-'+label+'-events.json')
            subprocess.run([sys.executable,str(ws/'outputs/native-windows-physical-f/decode-legacy-events.py'),str(path),'--output',str(dest)],check=True,stdout=subprocess.DEVNULL)
            decoded.append(json.loads(dest.read_text())['records'])
        a,b=decoded;by={v['record']:v for v in b};assert all(by.get(v['record'])==v for v in a)
        known.extend(a);boundary=max((v['record'] for v in a),default=0)
        r['new_events'][label]=[v for v in b if v['record']>boundary]
    try:log=after['F'].read('xwnidle/repeat.log' if case in ['005','006'] else 'xwnidle/result.log').decode('ascii')
    except KeyError:log=''
    r['log']=log
    r['window_observer_log']='' if case in ['005','006'] else after['F'].read('xwnidle/windows.log').decode('cp1252')
    match=re.fullmatch(r'ATTEMPT_ONCE 120000\r\nIDLE_COMPLETE_MS ([0-9]+)\r\nNORMAL_RESTART_REQUEST 0\r\n',log)
    r['idle_elapsed_ms']=int(match.group(1)) if match else None
    r['idle_completed']=bool(match) and r['idle_elapsed_ms']>=120000
    if case in ['001','002']:
        match=re.fullmatch(r'ATTEMPT_ONCE 120000\r\nIDLE_COMPLETE_MS ([0-9]+)\r\nINSTALL_QUEUE_IDLE_BEFORE_RESTART 0\r\nNORMAL_RESTART_REQUEST 0\r\n',log)
        r['idle_elapsed_ms']=int(match.group(1)) if match else None
        r['idle_completed']=bool(match) and r['idle_elapsed_ms']>=120000
        r['restart_blocked_pending_install']='RESTART_BLOCKED_PENDING_INSTALL' in log

def recurring(v):
    return (v['source'],v['event_id']) in {('Service Control Manager',7000),('Ftdisk',49)} and any(all(v[n]==old[n] for n in ['source','event_id','type','strings','data_hex']) for old in known)
r['unexpected_errors']=[v for group in r['new_events'].values() for v in group if v['type'] in [1,2] and not recurring(v)]
r['popup_records']=[v for v in r['new_events']['system'] if v['source']=='Application Popup']
r['normal_shutdown_count']=sum(v['source']=='EventLog' and v['event_id']==6006 for v in r['new_events']['system'])
launch=json.loads((out/'launch.json').read_text());r['dashboard_return']=len(launch['cycles'])==1 and launch['cycles'][0].get('dashboard_return') is True
r['diagnostic_checks_passed']=all([r['idle_completed'],r['storage_workload_not_run'],r['dashboard_return'],r['normal_shutdown_count']==1,not r['unexpected_errors'],not r['popup_records'],not r['new_events']['application'],all(v['matched'] for v in r['payloads']),all(r['baseline_checks'].values()),r['fatx_exact'],all(v['matched'] for v in r['runtime_binary_checks'])])
r['ordinary_run_valid']=False
r['ui_assisted_diagnostic']=True
r['debugger_observation']=False
r['host_recorder_enabled']=False
r['limits']='Exact prior004 helper on a retained pre-install fixture with reviewed0101. Targeted GPU Finish/restart No and identified emulator placeholder Cancel alter timing. Restart is gated on completed actions and an idle install queue. No ordinary stability, hardware or corruption-root-cause qualification.'
(out/'audit.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({n:r[n] for n in ['diagnostic_checks_passed','idle_completed','idle_elapsed_ms','normal_shutdown_count','dashboard_return','unexpected_errors','popup_records','window_observer_log']},indent=2))
