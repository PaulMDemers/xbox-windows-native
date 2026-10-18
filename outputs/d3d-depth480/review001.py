"""Independent actual NT5 lifecycle receipts; no loss/restore or leak-free claim."""
import hashlib,json,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sys.path.insert(0,str(W/'tools'));import graphics_depth as g
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=K/'runtime-review001.json';assert not out.exists()
c=json.loads((K/'ntfs-cold1-002.json').read_text());s=json.loads((K/'ntfs-phase1.json').read_text())
assert s['closed'] and s['exit_code']==0 and not s['deadline'] and not any(s.get(k) for k in ('host_quit','host_kill','host_terminate'))
assert c['complete'] and c['normal_shutdown_delta']==1
p=Path(c['private_path'])/'files/xwn480';b=json.loads((K/'build001.json').read_text());assert sha(p/'d3d.exe')==b['rows'][1]['sha256']
runner=g.decode((p/'runner.txt').read_bytes())
required={'schema','pid','start_tick','completed_cases','end_tick','restart_privilege','restart_request'}|{f'case{i}_{n}' for i in range(2) for n in ['start_tick','pid','wait','exit']}
assert set(runner)==required and all(v.isdecimal() for v in runner.values())
assert runner['schema']=='480' and runner['completed_cases']=='2' and runner['restart_request']=='1' and runner['restart_privilege']=='1'
r=dict(rows=[],runner=runner,all_allowed_cases_passed=False,scope='Actual NT5 RGB software offscreen depth/order controls, no presentation/GPU/performance claim')
for i,(name,backend) in enumerate([('r08bd','default'),('r08bs','hel')]):
 assert runner[f'case{i}_wait']=='0';code=int((p/(name+'.exit')).read_text());assert code==int(runner[f'case{i}_exit'])
 raw=(p/(name+'.txt')).read_bytes();f=g.decode(raw)
 assert [f[k] for k in ('os.major','os.minor','os.build')]==['5','0','2195']
 row=dict(name=name,backend=backend,process_exit=code,fields=f)
 try:row['review']=g.validate(raw,[(p/(name+'-'+suffix+'.bin')).read_bytes() for suffix in g.SUFFIXES],backend,code)
 except Exception as e:row['review_failure']=str(e)
 for ext in ['.txt','.exit']:(K/('pc001-'+name+ext)).write_bytes((p/(name+ext)).read_bytes())
 r['rows'].append(row)
(K/'pc001-runner.txt').write_bytes((p/'runner.txt').read_bytes())
r['all_allowed_cases_passed']=all('review' in row for row in r['rows'])
r['frozen_dependencies']=json.loads((K/'preflight001.json').read_text())['files']
for name,h in r['frozen_dependencies'].items():assert sha(Path(name))==h,name
admission=json.loads((K/'launch-admission001.json').read_text());assert admission['preflight_finished_ns']<=admission['validated_ns'];r['launch_admission']=admission
r['private_files']={str(f):sha(f) for f in p.iterdir() if f.is_file()}
out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(dict(passed=r['all_allowed_cases_passed'],rows=[dict(name=x['name'],exit=x['process_exit'],review=x.get('review'),failure=x.get('review_failure')) for x in r['rows']])))
