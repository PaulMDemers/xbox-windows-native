"""Once-only review of605 exports after normal VM exit and cold audit."""
import hashlib,json
from pathlib import Path
from trace_oracle import validate
K=Path(__file__).resolve().parent;P=Path('C:/xwn607/pc001/cold1-002');out=K/'review001.json';assert not out.exists()
read=lambda n:json.loads((K/n).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=dict(passed=False,physical_access=False)
try:
 s=read('ntfs-phase1.json');a=read('ntfs-cold1-002.json');b=read('build002.json');m=json.loads((P/'manifest.json').read_text())
 assert s['closed'] and s['exit_code']==0 and a['complete'] and a['normal_shutdown_delta']==1
 assert not any(s.get(n) for n in ['deadline','host_quit','host_terminate','host_kill','space_stop'])
 assert a['audit_unchanged'] and a['source_unchanged']
 assert all(h['clean'] and h['header_valid'] and h['independent_raw_values_agree'] for h in a['hives'])
 for row in b['rows']:assert m['xwn607-kit/'+Path(row['path']).name]['sha256']==row['sha256']
 logs=P/'files/xwn607';run=(logs/'runner.txt').read_text();trace=(logs/'trace.txt').read_text()
 for token in ['control_wait=0','trace_wait=0','control_ok=1','trace_ok=1','restart_request=1']:assert token in run,token
 assert run.count('exit_code=0')==2 and 'owned_terminate=' not in run
 control=(logs/'control.txt').read_text();subject=(logs/'subject.txt').read_text();assert control==subject
 assert control.endswith('PHASE605 PASS: 71 exact copies, pending request, duplicate request\nNULL607 PASS: RGB and masks objects, invalid header, no output pointers\nSUBJECT601 PASS\n')
 assert 'DIB604 PROBES PASS' in control and 'GRAPHICS601 PASS' in control
 r.update(passed=True,trace=validate(trace,b['target_image_base'],b['target_image_size']),normal_shutdown_delta=1,subject_control_equal=True,new_system_events=a['new_system_events'],logs={n:sha(logs/n) for n in ['runner.txt','trace.txt','subject.txt','control.txt']})
except BaseException as e:r['passed']=False;r['error']=repr(e);raise
finally:out.write_text(json.dumps(r,indent=2)+'\n')
print('605 actual phase transition and capped samples passed')
