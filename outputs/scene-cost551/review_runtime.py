"""Offline six-scene Xbox resource comparison; no boot or GPU promotion."""
import hashlib,json,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sys.path.insert(0,str(W/'tools'));import graphics_scenebench as b
from graphics_discovery import decode
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def host(s):return Path('/mnt/'+s[0].lower()+s[2:].replace(chr(92),'/')) if sys.platform!='win32' and len(s)>2 and s[1]==':' else Path(s)
out=K/'runtime-review001.json';assert not out.exists()
c=read(K/'collection001.json');a=read(K/'audit1.json');q=read(K/'package001.json')
assert c['completed'] and c['hook_removed'] and c['protected_code_exact'] and a['closed'] and a['hives_clean']
for n,row in c['files'].items():assert sha(host(row['path']))==row['sha256'],n
p=host(c['files']['/E/xwn551/runner.txt']['path']).parent
for name in ('bench.exe','scene.exe'):assert sha(p/name)==q['files'][name]['sha256']
runner=decode((p/'runner.txt').read_bytes())
keys={'schema','pid','start_tick','completed_cases','end_tick','restart_privilege','restart_request'}|{f'case{i}_{n}' for i in range(2) for n in ('start_tick','pid','wait','exit')}
assert set(runner)==keys and all(v.isdecimal() for v in runner.values())
assert runner['schema']=='551' and runner['completed_cases']=='2' and runner['restart_privilege']==runner['restart_request']=='1'
r=dict(rows=[],benchmarks=[],runner=runner,all_allowed_cases_passed=False,normal_restart_supported=a['events']['system']['normal_shutdown_delta']==1,hardware_acceleration_proved=False)
for i,(name,backend) in enumerate([('costd','default'),('costs','hel')]):
 assert runner[f'case{i}_wait']==runner[f'case{i}_exit']=='0'
 result=b.validate_directory(p/name,backend);r['benchmarks'].append(result)
 for j,review in enumerate(result['scene_reviews']):
  prefix=name+f'-c{j}';raw=(p/(prefix+'.txt')).read_bytes()
  r['rows'].append(dict(name=prefix,backend=backend,review=review,fields=b.scene.scene.decode(raw)))
for f in p.iterdir():
 if f.suffix in ('.txt','.exit'):
  dest=K/('physical001-'+f.name);assert not dest.exists();dest.write_bytes(f.read_bytes())
for n,h in q['pins'].items():assert sha(host(n))==h,n
r.update(all_allowed_cases_passed=True,scope='Six separately owned software scene processes with checked pixels and whole-process costs including pauses/capture I/O; no FPS, leak-free, GPU or game claim')
out.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print('PASS six Xbox scenes and process-cost receipts')
