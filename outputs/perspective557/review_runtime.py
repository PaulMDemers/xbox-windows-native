"""Offline matched Xbox sustained-scene evidence; no runtime or launch action."""
import hashlib,json,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sys.path.insert(0,str(W/'tools'));import graphics_perspective as g
from graphics_discovery import decode
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def host(s):return Path('/mnt/'+s[0].lower()+s[2:].replace(chr(92),'/')) if sys.platform!='win32' and len(s)>2 and s[1]==':' else Path(s)
out=K/'runtime-review001.json';assert not out.exists()
c=read(K/'collection001.json');a=read(K/'audit1.json');q=read(K/'package001.json')
assert c['completed'] and c['hook_removed'] and c['protected_code_exact'] and a['closed'] and a['hives_clean']
for n,row in c['files'].items():assert sha(host(row['path']))==row['sha256'],n
p=host(c['files']['/E/xwn557/runner.txt']['path']).parent
assert sha(p/'d3d.exe')==q['files']['d3d.exe']['sha256']
runner=decode((p/'runner.txt').read_bytes())
keys={'schema','pid','start_tick','completed_cases','end_tick','restart_privilege','restart_request'}|{f'case{i}_{n}' for i in range(2) for n in ('start_tick','pid','wait','exit')}
assert set(runner)==keys and all(v.isdecimal() and 0<=int(v)<=0xffffffff for v in runner.values())
assert runner['schema']=='557' and runner['completed_cases']=='2' and runner['restart_privilege']==runner['restart_request']=='1'
r=dict(rows=[],runner=runner,all_allowed_cases_passed=False,normal_restart_supported=a['events']['system']['normal_shutdown_delta']==1,hardware_acceleration_proved=False)
for i,(name,backend) in enumerate([('r09fd','default'),('r09fs','hel')]):
 assert runner[f'case{i}_wait']==runner[f'case{i}_exit']=='0'
 raw=(p/(name+'.txt')).read_bytes();code=int((p/(name+'.exit')).read_text());assert code==0
 review=g.validate(raw,*[(p/(name+'-'+n+'.bin')).read_bytes() for n in ('clear','draw','source-before','source-after')],backend,code)
 assert review['report_sha256']==hashlib.sha256(raw).hexdigest()
 r['rows'].append(dict(name=name,backend=backend,review=review,fields=g.decode(raw),process_exit=code))
for f in p.iterdir():
 if f.suffix in ('.txt','.exit'):
  dest=K/('physical001-'+f.name);assert not dest.exists();dest.write_bytes(f.read_bytes())
for n,h in q['pins'].items():assert sha(host(n))==h,n
r.update(all_allowed_cases_passed=True,scope='Two software contexts, five offscreen varying-W cases each. No presentation, GPU, games or performance claim')
out.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print('PASS two Xbox perspective controls and ten offscreen cases')
