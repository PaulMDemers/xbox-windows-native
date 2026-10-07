"""Audit one recovery boot without treating a deliberate prior crash as ordinary PASS."""
import contextlib,struct,subprocess,sys
from common import *
from dumps import dump_files,cookie
from allocation import scan
sys.path.insert(0,'/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/python3/dist-packages')
import hivex
case='recovery003';out=k/case;art=out/'artifacts';art.mkdir(exist_ok=True)
assert not (out/'audit.json').exists()
f=read(k/'fixture-recovery003.json');base=ws/'outputs/native-windows-fatx-forensics/artifacts'/f['fixture_name']
disk=ws/'work/runs/nt5-atapi-lba48-recovery-recovery003/hdd.qcow2'
assert (disk.parent/'cleanup.json').exists() and sha(base)==f['fixture_sha256']
for row in f['parents']:assert sha(Path(row['path']))==row['sha256']
r=dict(scope=__doc__,physical_access=False,debugger=False,ordinary_qualified=False,
       protected=[],payloads=[],hives=[],saved_dumps=[],new_events={},parent_crash_unchanged=True)
with contextlib.ExitStack() as stack:
    before,after=[readers(stack.enter_context(ColdIO(p)),p) for p in [base,disk]]
    expected=before['F'].read('pagefile.sys')[:65536];assert cookie(expected) and m.sha(expected)==f['crash_payload_sha256']
    try:log=after['F'].read('xwnrecover105/result.log');(art/'result.log').write_bytes(log);r['log']=log.decode('ascii')
    except KeyError:r['log']=''
    baseline=dump_files(before['F']);saved=dump_files(after['F']);assert {n:m.sha(b) for n,b in baseline.items()}==f['before_dump_files']
    r['prior_dump_files_unchanged']=all(saved.get(n)==b for n,b in baseline.items())
    for name,data in saved.items():
        if name in baseline:continue
        target=art/('saved-'+name.rsplit('/',1)[-1]);target.write_bytes(data)
        r['saved_dumps'].append(dict(path=name,artifact=target.name,bytes=len(data),sha256=m.sha(data),exact_crash_payload=data==expected,exact_cookie=cookie(data)))
    for row in f['protected']:
        actual=m.sha(after[row['volume']].read(row['path']));r['protected'].append(dict(**row,actual_sha256=actual,matched=actual==row['sha256']))
    for row in f['payloads']:
        actual=m.sha(after['F'].read(row['path']));r['payloads'].append(dict(path=row['path'],actual_sha256=actual,matched=actual==row['sha256']))
    r['startup_unchanged']=m.sha(after['F'].read(STARTUP))==f['startup_sha256']
    for name in HIVES:
        data=after['F'].read('winnt/system32/config/'+name);p=art/('after-'+name);p.write_bytes(data)
        v=dict(name=name,sha256=m.sha(data),parsed=False)
        try:
            h=hivex.Hivex(str(p));todo=[h.root()];seen=set();count=0
            while todo:
                n=todo.pop();assert n not in seen;seen.add(n);h.node_name(n)
                for item in h.node_values(n):h.value_key(item);h.value_value(item);count+=1
                todo.extend(h.node_children(n))
            v.update(parsed=True,keys=len(seen),values=count)
        except Exception as exc:v['error']=repr(exc)
        r['hives'].append(v)
    r['event_history_preserved']=True
    for name,label in [('sysevent.evt','system'),('appevent.evt','application')]:
        rows=[]
        for phase,rr in [('before',before),('after',after)]:
            p=art/(phase+'-'+name);p.write_bytes(rr['F'].read('winnt/system32/config/'+name));dest=out/(phase+'-'+label+'-events.json')
            subprocess.run([sys.executable,str(ws/'outputs/native-windows-physical-f/decode-legacy-events.py'),str(p),'--output',str(dest)],check=True,stdout=subprocess.DEVNULL);rows.append(read(dest)['records'])
        a,b=rows;by={v['record']:v for v in b};r['event_history_preserved'] &= all(by.get(v['record'])==v for v in a)
        boundary=max((v['record'] for v in a),default=0);r['new_events'][label]=[v for v in b if v['record']>boundary]
scan(disk,art);allocation=read(out/'allocation.json');r['allocation_sha256']=sha(out/'allocation.json')
r['allocation_passed']=allocation['allocation_consistent'] and not allocation['errors'] and not allocation['orphan_cluster_count']
r['integrity_passed']=r['allocation_passed'] and all(v['parsed'] for v in r['hives']) and all(v['matched'] for v in r['protected']+r['payloads']) and r['startup_unchanged'] and r['prior_dump_files_unchanged']
r['warnings_errors']=[v for values in r['new_events'].values() for v in values if v['type'] in [1,2]]
r['strict_ordinary_events_passed']=not r['warnings_errors'] and not r['new_events']['application']
def expected_crash(v):
    if v['source']=='EventLog' and v['event_id']==6008:return True
    text=' '.join(v.get('strings',[])).lower()
    return v['source']=='Save Dump' and v['event_id']==1001 and all(n in text for n in ['e058d103','44554d50','00000103','00010000','00000001'])
r['expected_prior_crash_events']=[v for v in r['new_events']['system'] if expected_crash(v)]
r['unexpected_warnings_errors']=[v for v in r['warnings_errors'] if not expected_crash(v)]
r['normal_shutdown_count']=sum(v['source']=='EventLog' and v['event_id']==6006 for v in r['new_events']['system'])
r['dashboard_return']=read(out/'launch.json')['cycles'][0].get('dashboard_return') is True
r['recovery_file_passed']=len(r['saved_dumps'])==1 and all(v['exact_crash_payload'] and v['exact_cookie'] for v in r['saved_dumps'])
r['probe_passed']='RECOVERY_FILE_FOUND\r\n' in r['log'] and 'NORMAL_RESTART_REQUEST\r\n' in r['log'] and 'FAIL' not in r['log']
r['expected_event_counts_bounded']=sum(v['source']=='EventLog' and v['event_id']==6008 for v in r['expected_prior_crash_events'])<=1 and sum(v['source']=='Save Dump' and v['event_id']==1001 for v in r['expected_prior_crash_events'])<=1
r['no_unexpected_popup']=not any(v['source']=='Application Popup' for v in r['new_events']['system'])
r['recovery_qualified']=r['expected_event_counts_bounded'] and r['no_unexpected_popup'] and r['recovery_file_passed'] and r['probe_passed'] and r['integrity_passed'] and r['event_history_preserved'] and not r['unexpected_warnings_errors'] and not r['new_events']['application'] and r['normal_shutdown_count']==1 and r['dashboard_return']
r['limits']='Recovery gate explicitly permits the recorded deliberate prior crash (EventLog6008 and exact-cookie Save Dump1001); all other warning/error and application deltas fail. Ordinary qualification remains false. Independent debugger parsing and physical qualification are separate.'
save(out/'audit.json',r);print(json.dumps({n:r[n] for n in ['saved_dumps','recovery_file_passed','probe_passed','integrity_passed','normal_shutdown_count','warnings_errors','unexpected_warnings_errors','recovery_qualified']},indent=2))
