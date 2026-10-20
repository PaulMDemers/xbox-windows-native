"""MIT. Pin unchanged loader and existing retained payload for cold-start admission."""
import datetime,hashlib,importlib.util,json,shutil,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
out=K/'package001.json';assert not out.exists()
prior=K.parent/'rct595';old=read(prior/'package001.json');col=read(prior/'collection001.json');st=read(prior/'stage001.json')
assert read(prior/'final001.json')['closed'] and not read(prior/'final001.json')['runner_present']
assert col['completed'] and col['hook_removed'] and 'result_directory' not in col
files=old['files'];expected={}
for n,row in files.items():
    if not n.startswith('game/'):continue
    remote='/E/xwn586-kit/'+n;v=col['files'].get(remote) or st['staged'][remote]
    assert v['sha256']==row['sha256'] and v['bytes']==row['bytes']
    expected[n[5:]]=dict(bytes=v['bytes'],sha256=v['sha256'])
preserved={n:r for n,r in col['files'].items() if n.startswith(('/E/xwn586-kit/','/E/xwn593-kit/')) and '/game/' not in n}
assert len(preserved)==9 and len(expected)==504
for row in list(files.values())+list(preserved.values()):
    p=Path(row['path']);assert p.stat().st_size==row['bytes'] and sha(p)==row['sha256']
assert files['load586.exe']['sha256']==read(K.parent/'rct586/phase2-source/media001.json')['exe_sha256']
test=read(K/'host001.json');assert test['passed']
for n,h in test['pins'].items():assert sha(K/n)==h
free=shutil.disk_usage('C:/').free;assert free-128*1024**2>=20*1024**3
space=read(prior/'console-space001.json');remaining=space['projected_remaining_bytes']-1024*1024
assert remaining>=128*1024**2
(K/'console-space001.json').write_text(json.dumps(dict(admitted=True,fresh_measurement=False,projected_remaining_bytes=remaining,source='595 load allowance was unused: no result directory. Reuse its88MiB reservation; deduct1MiB for hook/early-boot allowance. No game copy.'),indent=2)+'\n')
s=importlib.util.spec_from_file_location('package596controller',K/'controller001.py');c=importlib.util.module_from_spec(s);s.loader.exec_module(c);c.pair.verify()
pins=dict(read(K.parent/'windows-pair532/preflight001.json')['pins'])
for p in K.iterdir():
    if p.is_file() and p.name!='hardware-ready001.json':pins[str(p.resolve())]=sha(p)
for module in list(sys.modules.values()):
    n=getattr(module,'__file__',None)
    if n:
        p=Path(n).resolve()
        if p.is_relative_to(W) and p.is_file():pins[str(p)]=sha(p)
for rel in ['rct595/final001.json','rct595/collection001.json','rct595/stage001.json','rct586/final002.json','rct586/phase2-source/media001.json']:
    p=K.parent/rel;pins[str(p.resolve())]=sha(p)
r=dict(passed=True,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),files=files,reuse_expected=expected,preserved=preserved,runtime_module_pins=old['runtime_module_pins'],pins=pins,physical_attempt=596,pc_probe=586,allowed_launches=1,phase=2,helper_binary_unchanged=True,closed_runtime_reopened=False,cold_start_required=True,manual_observation_seconds=360,host_free_bytes=free,host_allowance_bytes=128*1024**2,preflight_scope='Full payload double-read at stage; before-state plus executable/config/saves/owners double-read at launch, directory equality and runtime-module hashes. No new writes or game activity between stage and launch.',limits='Manual Load, no behavior claim from elapsed time/input; no FPS/GPU claim.')
out.write_text(json.dumps(r,indent=2)+'\n');print('Frozen596; awaits explicit cold-ready record before any console operation')
