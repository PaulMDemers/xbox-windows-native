"""Closed ordinary run audit; missing or failed workload is retained, never relaunched."""
import contextlib,subprocess,sys
from common import *
from protocol import expected_bytes,source_valid
from allocation import scan
sys.path.insert(0,'/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/python3/dist-packages')
import hivex
case=sys.argv[1];assert case in ['control001','candidate001'];out=k/case;art=out/'artifacts';art.mkdir(exist_ok=True)
assert not (out/'audit.json').exists(),'Do not repeat completed collection'
fixture=read(k/('fixture-'+case+'.json'));base=ws/'outputs/native-windows-fatx-forensics/artifacts'/fixture['fixture_name']
disk=ws/('work/runs/nt5-vobserve-'+case+'/hdd.qcow2')
assert (disk.parent/'cleanup.json').exists() and sha(base)==fixture['fixture_sha256']
for row in fixture['parents']:assert sha(Path(row['path']))==row['sha256']
r=dict(scope=__doc__,case=case,physical_access=False,debugger=False,explicit_ui_intervention=False,files=[],payloads=[],protected=[],hives=[],new_events={})
if (out/'timeout-memory.json').exists():
    r.update(debugger=False,debugger_during_bounded_workload=False,post_timeout_snapshot=True,
             timeout_snapshot_sha256=sha(out/'timeout-memory.json'))
with contextlib.ExitStack() as stack:
    before,after=[readers(stack.enter_context(ColdIO(p)),p) for p in [base,disk]]
    def optional(path):
        try:return after['F'].read(path)
        except KeyError:return None
    trace=optional('winnt/system32/xwn-video-trace.bin')
    assert trace is not None and len(trace)==4096
    (art/'video-trace.bin').write_bytes(trace);r['trace_sha256']=m.sha(trace)
    log=optional('xwnmove137/result.log');r['log']=None if log is None else log.decode('ascii',errors='backslashreplace')
    if log is not None:(art/'result.log').write_bytes(log)
    r['protocol_details']=validate_log(log,case=='candidate001');r['protocol_exact']=r['protocol_details']['passed']
    source=optional('xwnmove137/source.rgb');r['source_valid']=source is not None and source_valid(source,r['protocol_details'].get('source_metadata',[]))
    if source is not None:(art/'source.rgb').write_bytes(source)
    r['source_sha256']=None if source is None else m.sha(source)
    r['observed']=[]
    for index in range(18):
        for prefix in ['move','draw']:
            name=prefix+'%02d.rgb'%index;data=optional('xwnmove137/'+name)
            if data is not None:(art/name).write_bytes(data)
            r['observed'].append(dict(name=name,sha256=None if data is None else m.sha(data)))
    for index in range(18):
        path='xwnmove137/ref%02d.rgb'%index;data=optional(path)
        if data is not None:(art/('ref%02d.rgb'%index)).write_bytes(data)
        expected=next((v['reference_hash'] for v in r['protocol_details'].get('cases',[]) if v['index']==index),None)
        matched=data is not None and source is not None and data==expected_bytes(index,source) and fnv(data)==expected
        r['files'].append(dict(path=path,sha256=None if data is None else m.sha(data),matched=matched))
    for row in fixture['payloads']:
        actual=m.sha(after['F'].read(row['path']));r['payloads'].append(dict(path=row['path'],sha256=actual,matched=actual==row['sha256']))
    r['startup_unchanged']=m.sha(after['F'].read(STARTUP))==fixture['startup_sha256']
    for row in fixture['protected']:
        actual=m.sha(after[row['volume']].read(row['path']));r['protected'].append(dict(**row,after_sha256=actual,matched=actual==row['sha256']))
    for name in HIVES:
        data=after['F'].read('winnt/system32/config/'+name);path=art/('after-'+name);path.write_bytes(data)
        record=dict(name=name,sha256=m.sha(data),parsed=False)
        try:
            h=hivex.Hivex(str(path));todo=[h.root()];seen=set();values=0
            while todo:
                node=todo.pop();assert node not in seen;seen.add(node)
                for v in h.node_values(node):h.value_key(v);h.value_value(v);values+=1
                todo.extend(h.node_children(node))
            record.update(parsed=True,keys=len(seen),values=values)
        except Exception as exc:record['error']=repr(exc)
        r['hives'].append(record)
    r['event_history_preserved']=True;known=[]
    for name,label in [('sysevent.evt','system'),('appevent.evt','application')]:
        decoded=[]
        for prefix,rr in [('before',before),('after',after)]:
            p=art/(prefix+'-'+name);p.write_bytes(rr['F'].read('winnt/system32/config/'+name));dest=out/(prefix+'-'+label+'-events.json')
            subprocess.run([sys.executable,str(ws/'outputs/native-windows-physical-f/decode-legacy-events.py'),str(p),'--output',str(dest)],check=True,stdout=subprocess.DEVNULL)
            decoded.append(read(dest)['records'])
        a,b=decoded;by={v['record']:v for v in b};r['event_history_preserved'] &= all(by.get(v['record'])==v for v in a)
        boundary=max((v['record'] for v in a),default=0);known.extend(a);r['new_events'][label]=[v for v in b if v['record']>boundary]
r['warnings_errors']=[v for group in r['new_events'].values() for v in group if v['type'] in [1,2]]
r['recurring_exact_baseline']=[v for v in r['warnings_errors'] if any(all(v[n]==old[n] for n in ['source','event_id','type','strings','data_hex']) for old in known)]
r['strict_events_passed']=not r['warnings_errors'] and not r['new_events']['application'] and not any(v['source']=='Application Popup' for v in r['new_events']['system']) and r['event_history_preserved']
r['normal_shutdown_count']=sum(v['source']=='EventLog' and v['event_id']==6006 for v in r['new_events']['system'])
launch=read(out/'launch.json');r['dashboard_return']=len(launch['cycles'])==1 and launch['cycles'][0].get('dashboard_return') is True
if not (out/'allocation.json').exists():scan(disk,art)
allocation_path=out/'allocation.json'
allocation=read(allocation_path)
r['allocation_passed']=allocation['allocation_consistent'] and not allocation['errors'] and not allocation['orphan_cluster_count']
r['allocation_sha256']=sha(allocation_path)
r['workload_and_persistence_passed']=r['protocol_exact'] and r['source_valid'] and all(v['matched'] for v in r['files']) and r['normal_shutdown_count']==1 and r['dashboard_return']
r['integrity_passed']=r['allocation_passed'] and all(v['parsed'] for v in r['hives']) and all(v['matched'] for v in r['protected']+r['payloads']) and r['startup_unchanged']
r['strict_qualification_passed']=r['workload_and_persistence_passed'] and r['integrity_passed'] and r['strict_events_passed']
r['limits']='Eighteen actual native moves plus forced repaints; independent composition uses a checked guest-generated font bitmap; matched RAM0110 control or RAM0112 candidate. No driver lifecycle callback coverage claimed. No physical throughput or window-drag FPS claim. All warning/error/application deltas fail strict qualification; inherited device policy explicit.'
save(out/'audit.json',r)
print(json.dumps({key:r[key] for key in ['case','protocol_exact','workload_and_persistence_passed','integrity_passed','strict_events_passed','strict_qualification_passed','normal_shutdown_count','warnings_errors']},indent=2))
