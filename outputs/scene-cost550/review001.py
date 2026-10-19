"""Six independent scene oracles plus whole-process telemetry, from cold files."""
import hashlib,json,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sys.path.insert(0,str(W/'tools'));import graphics_scenebench as bench
from graphics_discovery import decode
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
out=K/'runtime-review002.json';assert not out.exists()
c=read(K/'ntfs-cold1-002.json');s=read(K/'ntfs-phase1.json');b=read(K/'build001.json')
assert c['complete'] and c['normal_shutdown_delta']==1 and s['closed'] and s['exit_code']==0
assert not s['deadline'] and not any(s.get(n) for n in ('host_quit','host_kill','host_terminate'))
p=Path(c['private_path'])/'files/xwn550'
for n in ('bench.exe','scene.exe'):
 row=next(r for r in b['rows'] if Path(r['path']).name==n);assert sha(p/n)==row['sha256']
runner=decode((p/'runner.txt').read_bytes())
keys={'schema','pid','start_tick','completed_cases','end_tick','restart_privilege','restart_request'}|{f'case{i}_{n}' for i in range(2) for n in ('start_tick','pid','wait','exit')}
assert set(runner)==keys and all(v.isdecimal() for v in runner.values())
assert runner['schema']=='550' and runner['completed_cases']=='2' and runner['restart_request']==runner['restart_privilege']=='1'
r=dict(rows=[],benchmarks=[],runner=runner,all_allowed_cases_passed=False,scope='Six separate software scene processes including pause and capture costs; no FPS/leak-free/GPU/game claim')
for i,(name,backend) in enumerate([('costd','default'),('costs','hel')]):
 assert runner[f'case{i}_wait']==runner[f'case{i}_exit']=='0'
 result=bench.validate_directory(p/name,backend);r['benchmarks'].append(result)
 for j,review in enumerate(result['scene_reviews']):
  prefix=name+f'-c{j}';raw=(p/(prefix+'.txt')).read_bytes();f=bench.scene.scene.decode(raw)
  r['rows'].append(dict(name=prefix,backend=backend,review=review,fields=f,process_exit=0))
for f in p.iterdir():
 if f.suffix in ('.txt','.exit'):
  dest=K/('pc001-'+f.name);assert not dest.exists();dest.write_bytes(f.read_bytes())
r['all_allowed_cases_passed']=True
r['frozen_dependencies']=read(K/'preflight001.json')['files']
for n,h in r['frozen_dependencies'].items():assert sha(Path(n))==h,n
r['launch_admission']=read(K/'launch-admission001.json')
r['private_files']={str(f):sha(f) for f in p.iterdir() if f.is_file()}
out.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(dict(passed=True,scenes=len(r['rows']),telemetry=[dict(backend=x['backend'],rows=x['rows']) for x in r['benchmarks']]),indent=2))
