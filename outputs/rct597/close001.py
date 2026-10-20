"""One cold review of the synthetic debugger control; no guest reopen."""
import datetime,hashlib,json
from pathlib import Path
from trace_oracle import validate
K=Path(__file__).resolve().parent;P=Path('C:/xwn597/pc001/cold1-002')
read=lambda name:json.loads((K/name).read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=K/'final001.json';assert not out.exists()
s=read('ntfs-phase1.json');a=read('ntfs-cold1-002.json');b=read('build002.json');m=json.loads((P/'manifest.json').read_text())
assert s['closed'] and s['exit_code']==0 and not s['deadline'] and a['complete']
assert not any(s.get(n) for n in ['host_quit','host_terminate','host_kill','space_stop'])
assert a['audit_unchanged'] and a['source_unchanged'] and a['normal_shutdown_delta']==1
assert all(h['clean'] and h['header_valid'] and h['independent_raw_values_agree'] for h in a['hives'])
for row in b['rows']:
 name=Path(row['path']).name
 assert m['xwn597-kit/'+name]['sha256']==row['sha256']
logs=P/'files/xwn597';run=(logs/'runner.txt').read_text()
for line in ['control_wait=0','trace_wait=0','control_ok=1','trace_ok=1','restart_request=1']:assert line in run
assert run.count('exit_code=0')==2 and 'owned_terminate=' not in run
for name in ['subject.txt','control.txt']:assert (logs/name).read_text()=='SUBJECT597 begin\nSUBJECT597 PASS\n'
result=validate((logs/'trace.txt').read_text(),b['target_image_base'],b['target_image_size'])
result['private_log_sha256']=sha(logs/'trace.txt')
(K/'trace-review001.json').write_text(json.dumps(result,indent=2)+'\n')
result=dict(closed=True,passed=True,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            physical_access=False,owned_vm_closed=True,subject_requests=25,calling_threads=2,
            normal_shutdown_delta=1,console_state='Untouched; last dashboard with no hook.',
            limits='Original synthetic debugger control only. No RCT/API-return/surface-method/FPS/acceleration evidence. No Xbox boot after596 SOFTWARE cleanup.',
            checks={name:read(name)['passed'] for name in ['binary-review001.json','host-tests001.json','media-review001.json','trace-review001.json']},
            new_system_events=a['new_system_events'],
            inputs={str(p):sha(p) for p in sorted(K.iterdir()) if p.is_file()},
            logs={name:sha(logs/name) for name in ['trace.txt','subject.txt','control.txt','runner.txt']})
assert all(result['checks'].values())
out.write_text(json.dumps(result,indent=2)+'\n');print('PC597 CLOSED: 25 requests, two threads, paired subject controls and normal restart passed')
