"""Review actual cold NT5 presentation results, retaining partial failures."""
import hashlib,json,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sys.path.insert(0,str(W/'tools'));import graphics_present as g
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=K/'runtime-review001.json';assert not out.exists()
cold=json.loads((K/'ntfs-cold1-002.json').read_text());state=json.loads((K/'ntfs-phase1.json').read_text())
assert state['closed'] and state['exit_code']==0 and not state['deadline'] and not any(state.get(k) for k in ('host_quit','host_kill','host_terminate'))
assert cold['complete'] and cold['normal_shutdown_delta']==1
p=Path(cold['private_path'])/'files/xwn439'
build=json.loads((K/'build001.json').read_text());assert sha(p/'present.exe')==build['rows'][1]['sha256']
runner={}
for line in (p/'runner.txt').read_text().splitlines():
 k,v=line.split('=',1);assert k not in runner and v.isdecimal();runner[k]=v
assert runner['schema']=='439' and runner['completed_cases']=='2' and runner['restart_request']=='1' and runner['restart_privilege']=='1'
record=dict(runner=runner,rows=[],all_allowed_cases_passed=False,scope='Actual Windows2000 PC control; GDI readback, not scanout or GPU')
for i,(name,backend) in enumerate([('r03d','default'),('r03s','hel')]):
 assert runner[f'case{i}_wait']=='0'
 code=int((p/(name+'.exit')).read_text());assert code==int(runner[f'case{i}_exit'])
 raw=(p/(name+'.txt')).read_bytes();fields=g.decode(raw)
 assert [fields[k] for k in ('os.major','os.minor','os.build')]==['5','0','2195']
 row=dict(name=name,process_exit=code,fields=fields)
 captures={k:(p/(name+'-'+k+'.bin')).read_bytes() for k in ('source','before','after')}
 try:row['review']=g.validate(raw,captures,backend,code)
 except Exception as e:row['review_failure']=str(e)
 for ext in ('.txt','.exit'):(K/('pc001-'+name+ext)).write_bytes((p/(name+ext)).read_bytes())
 record['rows'].append(row)
(K/'pc001-runner.txt').write_bytes((p/'runner.txt').read_bytes())
record['all_allowed_cases_passed']=all('review' in r for r in record['rows'])
record['files']={str(f):sha(f) for f in p.iterdir() if f.is_file()}
record['frozen_dependencies']=json.loads((K/'preflight001.json').read_text())['files']
for f,h in record['frozen_dependencies'].items():assert sha(Path(f))==h,f
out.write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({k:record[k] for k in ('all_allowed_cases_passed','rows')}))
