"""Review actual cold NT5 presentation results, retaining partial failures."""
import hashlib,json,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sys.path.insert(0,str(W/'tools'));import graphics_sprites as g
from mode_receipt import validate_mode
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=K/'runtime-review001.json';assert not out.exists()
cold=json.loads((K/'ntfs-cold1-002.json').read_text());state=json.loads((K/'ntfs-phase1.json').read_text())
assert state['closed'] and state['exit_code']==0 and not state['deadline'] and not any(state.get(k) for k in ('host_quit','host_kill','host_terminate'))
assert cold['complete'] and cold['normal_shutdown_delta']==1
p=Path(cold['private_path'])/'files/xwn450'
build=json.loads((K/'build001.json').read_text());assert sha(p/'sprites.exe')==build['rows'][1]['sha256']
runner={}
for line in (p/'runner.txt').read_text().splitlines():
 k,v=line.split('=',1);assert k not in runner and v.isdecimal();runner[k]=v
assert runner['schema']=='450' and runner['completed_cases']=='6' and runner['restart_request']=='1' and runner['restart_privilege']=='1'
mode_review=validate_mode(runner)
record=dict(mode_review=mode_review,runner=runner,rows=[],all_allowed_cases_passed=False,scope='Actual Windows2000 PC control; GDI readback, not scanout or GPU')
for i,(name,backend,fmt) in enumerate([('r04di','default','index8'),('r04si','hel','index8'),('r04d6','default','rgb565'),('r04s6','hel','rgb565'),('r04d3','default','rgb32'),('r04s3','hel','rgb32')]):
 assert runner[f'case{i}_wait']=='0'
 code=int((p/(name+'.exit')).read_text());assert code==int(runner[f'case{i}_exit'])
 raw=(p/(name+'.txt')).read_bytes();fields=g.decode(raw)
 assert [fields[k] for k in ('os.major','os.minor','os.build')]==['5','0','2195']
 assert [fields[k] for k in ('mode.width','mode.height','mode.bpp')]==['640','480','24']
 row=dict(name=name,format=fmt,backend=backend,process_exit=code,fields=fields)
 captures={k:(p/(name+'-'+k+'.bin')).read_bytes() for k in g.KINDS}
 try:row['review']=g.validate(raw,captures,backend,fmt,code)
 except Exception as e:row['review_failure']=str(e)
 for ext in ('.txt','.exit'):(K/('pc001-'+name+ext)).write_bytes((p/(name+ext)).read_bytes())
 record['rows'].append(row)
(K/'pc001-runner.txt').write_bytes((p/'runner.txt').read_bytes())
record['all_allowed_cases_passed']=all('review' in r for r in record['rows'])
record['files']={str(f):sha(f) for f in p.iterdir() if f.is_file()}
record['frozen_dependencies']=json.loads((K/'preflight001.json').read_text())['files']
for f,h in record['frozen_dependencies'].items():assert sha(Path(f))==h,f
admission=json.loads((K/'launch-admission001.json').read_text());assert admission['preflight_finished_ns']<=admission['validated_ns']
record['launch_admission']=admission
out.write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(dict(passed=record['all_allowed_cases_passed'],rows=[dict(name=r['name'],exit=r['process_exit'],error=r.get('review_failure'),bytes=r.get('review',{}).get('exact_bytes')) for r in record['rows']])))
