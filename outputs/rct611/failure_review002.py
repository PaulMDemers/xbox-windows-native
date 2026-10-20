"""Retain host-space stop and durable cold evidence without inventing a game run."""
import hashlib,json,sys
from pathlib import Path
K=Path(__file__).resolve().parent;P=Path('C:/xwn611/pc001/cold1-002')
out=K/'failure-review002.json';assert not out.exists()
read=lambda n:json.loads((K/n).read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
sys.path.insert(0,str(K.parents[1]/'work/python-packages'));from Registry import Registry
s=read('ntfs-phase1.json');a=read('ntfs-cold1-002.json');m=json.loads((P/'manifest.json').read_text())
assert s['closed'] and s['space_stop'] and s['host_quit'] and s['exit_code']==0 and not s['deadline']
assert not read('review001.json')['passed']
assert a['complete'] and a['audit_unchanged'] and a['source_unchanged'] and a['normal_shutdown_delta']==0
assert all(h['clean'] and h['header_valid'] and h['independent_raw_values_agree'] for h in a['hives'])
for row in read('build001.json')['rows']:
 assert m['xwn611-kit/'+Path(row['path']).name]['sha256']==row['sha256']
assets=read('asset-integrity001.json')
changes=[dict(name=n,before=v['sha256'],after=m['xwn611-kit/'+n.lower()]['sha256']) for n,v in assets.items() if m['xwn611-kit/'+n.lower()]['sha256']!=v['sha256']]
assert len(assets)==503 and {r['name'] for r in changes}=={'game/Data/Game.cfg'}
flag=P/'files/xwn611-kit/copy-verified.txt';text=flag.read_text();assert 'verified=1' in text and 'files=503' in text
assert not any(n.startswith('xwn611/') for n in m)
reg=Registry.Registry(str(P/'files/WINNT/system32/config/software'))
key=reg.open('Fish Technology Group/RollerCoaster Tycoon Setup'.replace('/',chr(92)))
assert key.value('Path').value()=='C:'+chr(92)+'xwn611-kit'+chr(92)+'game'
out.write_text(json.dumps(dict(passed=True,attempt_passed=False,normal_shutdown=False,cleanup_qualified=False,
 host_space_stop=True,host_quit=True,owned_runtime_closed=True,
 copied_assets_unchanged=502,asset_changes=changes,tools_unchanged=True,source_unchanged=True,clean_cold_hives=5,
 durable_runner_or_trace_records=False,durable_game_registry=True,new_system_events=a['new_system_events'],
 scope='Cold bytes verify copy admission and incomplete configuration cleanup. Last UI showed run611 console and Please wait. No durable runner/trace records, no reference/phase or normal shutdown. Do not infer that game entry never executed, or that RCT crashed.',
 copy_flag_sha256=sha(flag)),indent=2)+'\n')
