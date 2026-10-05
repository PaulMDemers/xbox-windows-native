"""Cold audit of all rebuilt files and the bounded drawing workload."""
import importlib,json
from pathlib import Path
import subprocess,sys
k=Path(__file__).resolve().parent;ws=k.parents[1]
sys.path.insert(0,str(ws/'outputs/native-windows-paint-save'))
m=importlib.import_module('prepare-fixture')
run=ws/'work/runs/nt5-rebuilt-overlay-001'
assert (run/'cleanup.json').exists()
fixture=json.loads((k/'fixture.json').read_text())
base=ws/'outputs/native-windows-fatx-forensics/artifacts/gdi-baseline-003.qcow2'
assert m.filehash(base)==fixture['source_sha256']
disk=run/'hdd.qcow2';m.fatx.PARTITIONS['F']=(15633072*512,472764096*512)
stream=m.SliceIO(disk)
writers={letter:m.Writer(stream,m.fatx.open_partition(stream,disk,letter)) for letter in ['E','F']}
r=dict(scope=__doc__,run=run.name,physical_access=False,payloads=[])
for row in fixture['payloads']:
    letter,path=row['path'].split('/',1);actual=m.sha(writers[letter].read(path))
    r['payloads'].append(dict(path=row['path'],sha256=actual,matches_package=actual==row['sha256']))
out=k/'artifacts';out.mkdir(exist_ok=True)
for name in ['attempt.log','gdi-baseline.txt']:
    data=writers['F'].read('xwnpaint/'+name);(out/name).write_bytes(data);r[name]=data.decode('ascii')
gdi=json.loads((ws/'outputs/video-next/probe-v3/fixture.json').read_text())
r['workload_payloads_match']=all(m.sha(writers['F'].read(row['path']))==row['sha256'] for row in gdi['payloads'])
beforestream=m.SliceIO(base);before=m.Writer(beforestream,m.fatx.open_partition(beforestream,base,'F'))
for name,label in [('sysevent.evt','system'),('appevent.evt','application')]:
    for prefix,w in [('before',before),('after',writers['F'])]:
        file=out/(prefix+'-'+name);file.write_bytes(w.read('winnt/system32/config/'+name))
        subprocess.run([sys.executable,str(ws/'outputs/native-windows-physical-f/decode-legacy-events.py'),str(file),'--output',str(k/(prefix+'-'+label+'-events.json'))],check=True,stdout=subprocess.DEVNULL)
events={}
for label in ['system','application']:
    a=json.loads((k/('before-'+label+'-events.json')).read_text())['records'];b=json.loads((k/('after-'+label+'-events.json')).read_text())['records']
    by={row['record']:row for row in b};assert all(by.get(row['record'])==row for row in a)
    events[label]=[row for row in b if row['record']>max((v['record'] for v in a),default=0)]
r['new_events']=events
r['normal_stop_recorded']=any(v['source']=='EventLog' and v['event_id']==6006 for v in events['system'])
r['new_delayed_write_events']=any(v['source']=='Ftdisk' and v['event_id']==50 or v['source']=='Application Popup' for v in events['system'])
log=r['gdi-baseline.txt'];r['gdi_passed']=log.endswith('PASS 0 0 0\r\n') and 'FAIL' not in log and all(f'COPY_stage_pass {i} 1 0\r\n' in log for i in range(4))
r['normal_restart_requested']=r['attempt.log']=='ATTEMPT_ONCE\r\nREPLAY_EXIT_ZERO\r\nNORMAL_RESTART_REQUEST\r\n'
r['dashboard_return']=json.loads((k/'launch.json').read_text()).get('dashboard_return',False)
r['passed']=all([r['workload_payloads_match'],r['gdi_passed'],r['normal_stop_recorded'],r['normal_restart_requested'],r['dashboard_return'],not r['new_delayed_write_events'],not events['application'],all(v['matches_package'] for v in r['payloads'])])
r['limits']='Single synthetic-xemu boot and GDI workload; not physical qualification, network stress, full storage audit or general stability'
(k/'audit.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
