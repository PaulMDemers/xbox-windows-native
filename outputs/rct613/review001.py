"""Once-only interpretation of this control's cached cold readback."""
import hashlib,json
from pathlib import Path
from cost_oracle import validate
K=Path(__file__).resolve().parent;P=Path('C:/xwn613/pc001/cold1-002')
out=K/'review001.json';assert not out.exists()
read=lambda n:json.loads((K/n).read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=dict(passed=False,physical_access=False)
try:
 s=read('ntfs-phase1.json');a=read('ntfs-cold1-002.json');b=read('build002.json')
 assert s['closed'] and s['exit_code']==0 and a['complete'] and a['normal_shutdown_delta']==1
 assert not any(s.get(n) for n in ['deadline','host_quit','host_terminate','host_kill','space_stop'])
 assert a['audit_unchanged'] and a['source_unchanged']
 assert all(h['clean'] and h['header_valid'] and h['independent_raw_values_agree'] for h in a['hives'])
 m=json.loads((P/'manifest.json').read_text())
 for v in b['rows']:assert m['xwn613-kit/'+Path(v['path']).name]['sha256']==v['sha256']
 logs=P/'files/xwn613'
 parent=(logs/'sampler.txt').read_text();children=[(logs/f'child{i}.txt').read_text() for i in range(6)]
 costs=validate(parent,children)
 (K/'cost-review001.json').write_text(json.dumps(costs,indent=2)+'\n')
 r.update(passed=True,cleanup_passed=True,costs=costs,normal_shutdown_delta=1,new_system_events=a['new_system_events'],
          logs={p.name:sha(p) for p in logs.glob('*.txt')})
except BaseException as e:r['error']=repr(e);raise
finally:out.write_text(json.dumps(r,indent=2)+'\n')
print('613 original process cost control and cold cleanup passed')
