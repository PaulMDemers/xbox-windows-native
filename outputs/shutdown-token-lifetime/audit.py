"""Cold audit of the diagnostic emulator run; no physical qualification or popup waiver."""
import contextlib,importlib,json,subprocess,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];case=sys.argv[1];assert case in ['001','002'];out=k/case;art=out/'artifacts';art.mkdir(exist_ok=True)
sys.path.insert(0,str(ws/'outputs/fatx-mapped-eof'));from coldio import ColdIO
sys.path.insert(0,str(ws/'outputs/native-windows-paint-save'));m=importlib.import_module('prepare-fixture')
sys.path.insert(0,'/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/python3/dist-packages');import hivex
fixture=json.loads((k/'fixture-001.json').read_text());run=ws/('work/runs/nt5-shutdown-token-lifetime-'+case)
assert (run/'cleanup.json').exists()
base=ws/'outputs/native-windows-fatx-forensics/artifacts'/fixture['fixture_name'];assert m.filehash(base)==fixture['fixture_sha256']
m.fatx.PARTITIONS['F']=(15633072*512,472764096*512)
r=dict(scope=__doc__,physical_access=False,payloads=[],hives=[],new_events={})
with contextlib.ExitStack() as stack:
    readers=[]
    for disk in [base,run/'hdd.qcow2']:
        io=stack.enter_context(ColdIO(disk));readers.append(m.Writer(io,m.fatx.open_partition(io,disk,'F')))
    before,after=readers
    r['runtime_binary_checks']=[]
    identities=dict(json.loads((k/'site-review.json').read_text())['binaries'])
    identities.update(json.loads((k/'unwind-review.json').read_text())['binaries'])
    for name,identity in identities.items():
        path='winnt/system32/'+name;initial=m.sha(before.read(path));final=m.sha(after.read(path))
        r['runtime_binary_checks'].append(dict(path=path,before_sha256=initial,after_sha256=final,matched=initial==final==identity['sha256']))
    for path,expected in [('winnt/system32/ntoskrnl.exe',json.loads((k/'site-review.json').read_text())['kernel_sha256']),('winnt/system32/ntdll.dll',json.loads((k/'parameter-review.json').read_text())['sha256'])]:
        initial=m.sha(before.read(path));final=m.sha(after.read(path))
        r['runtime_binary_checks'].append(dict(path=path,before_sha256=initial,after_sha256=final,matched=initial==final==expected))
    for row in fixture['payloads']+[{ 'path':p,'sha256':h} for p,h in fixture['unchanged'].items() if '/config/' not in p]:
        h=m.sha(after.read(row['path']));r['payloads'].append(dict(path=row['path'],sha256=h,matched=h==row['sha256']))
    try:log=after.read('xwnsd01/probe.log').decode('cp1252',errors='backslashreplace')
    except KeyError:log=''
    r['log']=log;(art/'probe.log').write_text(log)
    r['samples']=[line for line in log.splitlines() if line.startswith('SAMPLE ')]
    r['commands']=[line for line in log.splitlines() if 'newdev.dll,DevInstall' in line]
    r['windows']=[line for line in log.splitlines() if line.startswith('WINDOW ')]
    r['volume_observations']=[line for line in log.splitlines() if line.startswith(('DRIVE ','TARGET ','BYTES ','CLUSTERS ','SPACE_'))]
    r['completed']=log.startswith('SHUTDOWN_DIAGNOSTIC_V1') and len(r['samples'])==5 and 'COMPLETE 5 ' in log and log.endswith('NORMAL_RESTART_REQUEST\r\n')
    for phase,w in [('before',before),('after',after)]:
        data=w.read('winnt/setupapi.log');(art/(phase+'-setupapi.log')).write_bytes(data)
    known=[]
    for name,label in [('sysevent.evt','system'),('appevent.evt','application')]:
        decoded=[]
        for phase,w in [('before',before),('after',after)]:
            path=art/(phase+'-'+name);path.write_bytes(w.read('winnt/system32/config/'+name));dest=out/(phase+'-'+label+'-events.json')
            subprocess.run([sys.executable,str(ws/'outputs/native-windows-physical-f/decode-legacy-events.py'),str(path),'--output',str(dest)],check=True,stdout=subprocess.DEVNULL)
            decoded.append(json.loads(dest.read_text())['records'])
        a,b=decoded;by={v['record']:v for v in b};assert all(by.get(v['record'])==v for v in a)
        known.extend(a);boundary=max((v['record'] for v in a),default=0);r['new_events'][label]=[v for v in b if v['record']>boundary]
    for name in ['system','software','default','sam','security']:
        data=after.read('winnt/system32/config/'+name);path=art/('after-'+name);path.write_bytes(data)
        h=hivex.Hivex(str(path));todo=[h.root()];seen=set();nvalues=0
        while todo:
            node=todo.pop();assert node not in seen;seen.add(node)
            for v in h.node_values(node):h.value_key(v);h.value_value(v);nvalues+=1
            todo.extend(h.node_children(node))
        r['hives'].append(dict(name=name,sha256=m.sha(data),keys=len(seen),values=nvalues,parsed=True))
def recurring(v):
    return (v['source'],v['event_id']) in {('Service Control Manager',7000),('Ftdisk',49)} and any(all(v[n]==old[n] for n in ['source','event_id','type','strings','data_hex']) for old in known)
r['unexpected_errors']=[v for group in r['new_events'].values() for v in group if v['type'] in [1,2] and not recurring(v)]
r['popups']=[v for v in r['new_events']['system'] if v['source']=='Application Popup']
r['normal_shutdown_count']=sum(v['source']=='EventLog' and v['event_id']==6006 for v in r['new_events']['system'])
launch=json.loads((out/'launch.json').read_text());r['dashboard_return']=launch['cycles'][0].get('dashboard_return',False)
r['diagnostic_checks_passed']=r['completed'] and r['dashboard_return'] and r['normal_shutdown_count']==1 and not r['unexpected_errors'] and not r['popups'] and not r['new_events']['application'] and all(v['matched'] for v in r['payloads']+r['runtime_binary_checks'])
r['ordinary_boot_qualified']=False
r['limits']='Debugger-interrupted installer trace; artifact checks cannot qualify an ordinary boot or a popup fix.'
(out/'audit.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({n:r[n] for n in ['completed','dashboard_return','diagnostic_checks_passed','popups','commands']},indent=2))
