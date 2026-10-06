"""Cold verification of mapped-file logs, exact durable data, payloads, hives and new events."""
import contextlib,importlib,json,subprocess,sys
from pathlib import Path
from coldio import ColdIO
from prepare import SIZES,expected,entry
k=Path(__file__).resolve().parent;ws=k.parents[1]
sys.path.insert(0,str(ws/'outputs/native-windows-paint-save'));m=importlib.import_module('prepare-fixture')
sys.path.insert(0,'/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/python3/dist-packages')
import hivex
case=sys.argv[1];assert case in ['old','fixed']
out=k/case;art=out/'artifacts';art.mkdir(parents=True,exist_ok=True)
fixture=json.loads((k/('fixture-'+case+'.json')).read_text())
base=ws/('outputs/native-windows-fatx-forensics/artifacts/fatx-mapped-eof-'+case+'.qcow2')
run=ws/('work/runs/nt5-fatx-mapped-eof-'+case)
assert (run/'cleanup.json').exists() and m.filehash(base)==fixture['fixture_sha256']
m.fatx.PARTITIONS['F']=(15633072*512,472764096*512)
r=dict(scope=__doc__,case=case,physical_access=False,payloads=[],files=[],hives=[],new_events={})
with contextlib.ExitStack() as stack:
    readers=[]
    for disk in [base,run/'hdd.qcow2']:
        io=stack.enter_context(ColdIO(disk));readers.append({v:m.Writer(io,m.fatx.open_partition(io,disk,v)) for v in ['E','F']})
    before,after=readers
    for row in fixture['payloads']+fixture['preserved_payloads']:
        if row['path']=='winnt/system32/xwn-video-trace.bin':continue
        actual=m.sha(after['F'].read(row['path']))
        r['payloads'].append(dict(path=row['path'],sha256=actual,matched=actual==row['sha256']))
    r['baseline_checks']={}
    for letter,path in [('F','winnt/system32/drivers/xwnfatx.sys'),('E','Applications/XWNFBoot/loader/halxboxnt5.dll'),('E','Applications/XWNFBoot/default.xbe'),('E','Applications/XWNFBoot/freeldr.sys')]:
        r['baseline_checks'][letter+'/'+path]=before[letter].read(path)==after[letter].read(path)
    r['fatx_exact']=m.sha(after['F'].read('winnt/system32/drivers/xwnfatx.sys'))==fixture['fatx_sha256']
    for i,size in enumerate(SIZES):
        for kind,round in [('input',0),('output',8)]:
            path=f'xwneof01/{kind}{i:02}.bin'
            try:data=after['F'].read(path)
            except KeyError:data=b''
            r['files'].append(dict(path=path,bytes=len(data),sha256=m.sha(data),exact=data==expected(i,size,round)))
    # The driver must zero the mapped buffer, not overwrite the disk's input slack.
    tails=[]
    for row in fixture['input_tails']:
        data=after['F'].read_cluster(row['last_cluster']);n=row['tail_bytes']
        tails.append(dict(path=row['path'],tail_bytes=n,unchanged=(not n or data[-n:]==b'\xd7'*n)))
    r['disk_tails']=tails
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
    try:log=after['F'].read('xwneof01/result.log').decode('ascii')
    except KeyError:log=''
    r['log']=log
def recurring(v):
    return (v['source'],v['event_id']) in {('Service Control Manager',7000),('Ftdisk',49)} and any(all(v[n]==old[n] for n in ['source','event_id','type','strings','data_hex']) for old in known)
r['unexpected_errors']=[v for group in r['new_events'].values() for v in group if v['type'] in [1,2] and not recurring(v)]
r['popup_records']=[v for v in r['new_events']['system'] if v['source']=='Application Popup']
r['normal_shutdown_count']=sum(v['source']=='EventLog' and v['event_id']==6006 for v in r['new_events']['system'])
launch=json.loads((out/'launch.json').read_text());r['dashboard_return']=len(launch['cycles'])==1 and launch['cycles'][0].get('dashboard_return') is True
rows=[line.split() for line in log.splitlines()]
checks=[(v[0],*map(int,v[1:])) for v in rows if v[0] in ['INPUT','OUTPUT'] and len(v)==4]
complete=[v for v in rows if v[0]=='COMPLETE'];rounds=[v for v in rows if v[0]=='ROUND']
r['mapping_checks']=len(checks);r['mapping_failures']=[dict(kind=v[0],index=v[1],content_mismatches=v[2],nonzero_tail_bytes=v[3]) for v in checks if v[2] or v[3]]
r['sequence_correct']=[(v[0],v[1]) for v in checks]==[('INPUT',i) for i in range(17)]+[('OUTPUT',i) for _ in range(8) for i in range(17)]
r['probe_completed']=r['sequence_correct'] and len(complete)==1 and complete[0]==['COMPLETE',str(len(r['mapping_failures'])),'17','8'] and len(checks)==153 and [v[1] for v in rounds]==list(map(str,range(1,9))) and log.startswith('ATTEMPT_ONCE 17 8 997\r\n') and log.endswith('NORMAL_RESTART_REQUEST 0 0 0\r\n') and 'FAIL_' not in log
r['persistence_passed']=all(v['exact'] for v in r['files']) and all(v['unchanged'] for v in r['disk_tails'])
r['ordinary_run_valid']=all([r['probe_completed'],r['dashboard_return'],r['normal_shutdown_count']==1,not r['unexpected_errors'],not r['popup_records'],not r['new_events']['application'],r['persistence_passed'],all(v['matched'] for v in r['payloads']),all(r['baseline_checks'].values()),r['fatx_exact']])
r['mapped_eof_passed']=r['ordinary_run_valid'] and not r['mapping_failures']
r['mapped_checks_passed']=r['probe_completed'] and not r['mapping_failures']
r['limits']='Serial API probe and ordinary synthetic-resource xemu; not hardware, concurrent mapped truncation, performance or PnP lifetime qualification. Allocation audit is separate.'
(out/'audit.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({**{n:r[n] for n in ['ordinary_run_valid','mapped_eof_passed','mapped_checks_passed','mapping_checks','persistence_passed','normal_shutdown_count']},'mapping_failure_count':len(r['mapping_failures']),'unexpected_errors':r['unexpected_errors'],'popups':r['popup_records']},indent=2))
