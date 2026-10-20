"""Review only the closed original graphics control; do not reopen guest."""
import datetime,hashlib,json
from pathlib import Path
from trace_oracle import validate
K=Path(__file__).resolve().parent;P=Path('C:/xwn601/pc001/cold1-002')
read=lambda n:json.loads((K/n).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=K/'review001.json';assert not out.exists()
r=dict(passed=False,physical_access=False)
try:
 s=read('ntfs-phase1.json');a=read('ntfs-cold1-002.json');b=read('build002.json');m=json.loads((P/'manifest.json').read_text())
 assert s['closed'] and s['exit_code']==0 and a['complete'] and a['normal_shutdown_delta']==1
 assert not any(s.get(n) for n in ['deadline','host_quit','host_terminate','host_kill','space_stop'])
 assert a['audit_unchanged'] and a['source_unchanged']
 assert all(h['clean'] and h['header_valid'] and h['independent_raw_values_agree'] for h in a['hives'])
 for row in b['rows']:assert m['xwn601-kit/'+Path(row['path']).name]['sha256']==row['sha256']
 logs=P/'files/xwn601';run=(logs/'runner.txt').read_text();text=(logs/'trace.txt').read_text()
 r['logs']={n:sha(logs/n) for n in ['runner.txt','trace.txt','subject.txt','control.txt']}
 for line in ['control_wait=0','trace_wait=0','control_ok=1','trace_ok=1','restart_request=1']:assert line in run,line
 assert run.count('exit_code=0')==2 and 'owned_terminate=' not in run
 control=(logs/'control.txt').read_text();subject=(logs/'subject.txt').read_text()
 assert control==subject and control.endswith('GRAPHICS601 PASS\nSUBJECT601 PASS\n')
 for line in ['bitblt_pixel_rounds=00000021','stretch_pixels=00000040','dd_hresult=00000000','surface_hresult=00000000','surface_blt_hresult=00000000']:assert line in control,line
 r['trace']=validate(text,b['target_image_base'],b['target_image_size'])
 r.update(passed=True,normal_shutdown_delta=1,subject_control_equal=True,new_system_events=a['new_system_events'])
except BaseException as e:r['error']=repr(e);raise
finally:out.write_text(json.dumps(r,indent=2)+'\n')
print('PC601 graphics control review passed')
