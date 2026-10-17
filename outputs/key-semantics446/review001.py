"""Review complete diagnostic transport without accepting unexpected pixels."""
import json,sys,struct
from pathlib import Path
from launch_gate import sha
K=Path(__file__).resolve().parent;W=K.parents[1]
sys.path.insert(0,str(W/'tools'));import graphics_keyprobe as g
out=K/'runtime-review001.json';assert not out.exists()
cold=json.loads((K/'ntfs-cold1-002.json').read_text());state=json.loads((K/'ntfs-phase1.json').read_text())
assert state['closed'] and state['exit_code']==0 and not state['deadline'] and not any(state.get(k) for k in ('host_quit','host_kill','host_terminate'))
assert cold['complete'] and cold['normal_shutdown_delta']==1
p=Path(cold['private_path'])/'files/xwn446'
build=json.loads((K/'build001.json').read_text());assert sha(p/'keyprobe.exe')==build['rows'][1]['sha256']
runner=g.decode((p/'runner.txt').read_bytes())
assert runner['schema']=='446' and runner['completed_cases']=='2' and runner['restart_request']=='1' and runner['restart_privilege']=='1'
record=dict(runner=runner,rows=[],scope='Actual NT5 raw RGB32 diagnostic; no display-mode change or hardware access')
for i,(name,backend) in enumerate([('keyd','default'),('keys','hel')]):
 assert runner[f'case{i}_wait']=='0'
 code=int((p/(name+'.exit')).read_text());assert code==int(runner[f'case{i}_exit'])
 raw=(p/(name+'.txt')).read_bytes();src=(p/(name+'-source.bin')).read_bytes();dst=(p/(name+'-dest.bin')).read_bytes()
 review=g.validate(raw,src,dst,backend,code)
 # Explanatory model is separate from full-width expected semantics.
 actual=struct.unpack('<9216I',dst);models=[]
 for stage in range(12):
  predicted=[0x335577]*768
  for sy in range(12):
   for sx in range(16):
    x,y=sx+4,sy+4;v=g.SOURCE[sy*16+sx]
    visible=not ((stage//2)%2) or (5<=y<15 and (6<=x<12 or 14<=x<19))
    if visible and (not stage%2 or (v&65535)!=(g.KEYS[stage//4]&65535)):predicted[y*32+x]=v
  models.append(dict(stage=stage,low16_comparison_model_mismatches=sum(a!=b for a,b in zip(actual[stage*768:(stage+1)*768],predicted))))
 record['rows'].append(dict(name=name,backend=backend,process_exit=code,review=review,low16_model=models))
 for ext in ('.txt','.exit'):(K/('pc001-'+name+ext)).write_bytes((p/(name+ext)).read_bytes())
(K/'pc001-runner.txt').write_bytes((p/'runner.txt').read_bytes())
record['all_semantics_passed']=all(r['review']['semantics_passed'] for r in record['rows'])
record['files']={str(f):sha(f) for f in p.iterdir() if f.is_file()}
record['frozen_dependencies']=json.loads((K/'preflight001.json').read_text())['files']
for f,h in record['frozen_dependencies'].items():assert sha(f)==h,f
admission=json.loads((K/'launch-admission001.json').read_text())
assert admission['preflight_finished_ns']<=admission['validated_ns']
record['launch_admission']=admission
out.write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(all_semantics_passed=record['all_semantics_passed'],rows=[dict(backend=r['backend'],mismatches=r['review']['mismatches'],modes=r['review']['modes'],stages=r['review']['rows']) for r in record['rows']]),indent=2))
