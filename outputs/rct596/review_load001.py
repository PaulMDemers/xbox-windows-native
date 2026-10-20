"""MIT. Cold load-run integrity gates; scene restoration is reviewed separately."""
import hashlib,json,struct
from pathlib import Path
K=Path(__file__).resolve().parent
read=lambda n:json.loads((K/n).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
out=K/'load-run-review001.json';assert not out.exists()
st=read('stage001.json');col=read('collection001.json');a=read('audit1.json')
assert st['completed'] and col['completed'] and col['hook_removed']
row=col['files'].get('/E/xwn586p2/runner.txt');fields={}
if row:
    assert sha(row['path'])==row['sha256']
    for line in Path(row['path']).read_text().splitlines():
        if '=' in line and not line.startswith(('window ','module=')):
            key,value=line.split('=',1);fields.setdefault(key,[]).append(value)
checks=dict(runner_present=bool(row),manual_interval_started=fields.get('manual_observation_started')==['1'],manual_interval_finished=fields.get('manual_observation_finished')==['1'],manual_sequence_zero_expected=fields.get('input_sequence_submitted')==['0'],normal_shutdown=a['events']['system']['normal_shutdown_delta']==1,game_exit_zero=fields.get('game_exit')==['0'],no_forced_termination='forced_terminate' not in fields,desktop_preserved=fields.get('desktop_restored')==['1'],registry_restored=read('registry-review001.json')['passed'] and fields.get('registry_restored')==['1'],restart_requested=fields.get('restart_requested')==['1'],hives_clean=a['hives_clean'] and read('user-hive-audit001.json')['passed'],welcome_preserved=read('welcome-review001.json')['passed'],hook_removed=col['hook_removed'],protected_code_exact=col['protected_code_exact'])
saves={}
for name in ['XWN586.SV4','XWN593.SV4']:
    n='/E/xwn586-kit/game/Saved Games/'+name;row=col['files'].get(n)
    checks[name+'_preserved']=bool(row) and sha(row['path'])==row['sha256']==st['staged'][n]['sha256'] and Path(row['path']).stat().st_size==row['bytes']==st['staged'][n]['bytes']
    saves[name]=row
images={}
for n,row in col['files'].items():
    if not n.startswith('/E/xwn586p2/') or not n.endswith('.bmp'):continue
    b=Path(row['path']).read_bytes()
    valid=sha(row['path'])==row['sha256'] and len(b)==54+640*480*4 and b[:2]==b'BM' and struct.unpack_from('<I',b,2)[0]==len(b) and struct.unpack_from('<I',b,10)[0]==54 and struct.unpack_from('<IiiHHII',b,14)==(40,640,-480,1,32,0,640*480*4)
    images[n]=dict(valid=valid,**row)
checks['valid_captures']=bool(images) and all(v['valid'] for v in images.values())
r=dict(passed=all(checks.values()),checks=checks,saves=saves,images=images,runner_fields=fields,load_behavior_proved=False,limits='Lifecycle and retained-byte integrity only. User observation plus inspected before/moved/restored images required for Load behavior. Ftdisk49 and full-allocation limitations remain.')
out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(checks))
