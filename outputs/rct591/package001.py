"""Freeze exact PC-qualified save helper for a fresh physical namespace."""
import ast,datetime,hashlib,importlib.util,json,shutil,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
host=lambda p:Path(p.replace('/mnt/c/','C:/'))
out=K/'package001.json';assert not out.exists() and not (K/'console-space001.json').exists()
assert read(K/'ready001.json')['cold_start_ready']
pc=K.parent/'rct586';final=read(pc/'final002.json');assert final['closed'] and final['passed']
assert all(final['checks'].values())
for phase in (1,2):
 state=read(pc/f'ntfs-phase{phase}.json');cold=read(pc/f'ntfs-cold{phase}-002.json')
 assert state['closed'] and state['exit_code']==0 and cold['complete'] and cold['normal_shutdown_delta']==1
 assert state['disk_sha256']==cold['disk_sha256']
helper=Path('C:/xwn586/build001/run586.exe');loader=Path('C:/xwn586/phase2-build001/load586.exe')
compiled=read(pc/'binary-review001.json');assert compiled['passed']
row=next(r for r in compiled['files'] if Path(r['path']).name=='run586.exe');assert sha(helper)==row['sha256']
load=read(pc/'phase2-source/media001.json');assert load['passed'] and sha(loader)==load['exe_sha256']
manifest=read(Path('C:/xwn586/pc001/cold1-002/manifest.json'))
assert manifest['xwn586-kit/run586.exe']['sha256']==sha(helper)
manifest2=read(Path('C:/xwn586/pc001/cold2-002/manifest.json'))
assert manifest2['xwn586-kit/load586.exe']['sha256']==sha(loader)
source=read(K.parent/'rct566/transfer001.json');assert source['passed']
files={n:dict(v,path=str(host(v['path']))) for n,v in source['files'].items()}
assert all(n.startswith('game/') for n in files)
files['run586.exe']=dict(path=str(helper),bytes=helper.stat().st_size,sha256=sha(helper))
sys.path.insert(0,str(W/'tools'));from fatx_names import check_path
for name,r in files.items():
 check_path('xwn586-kit/'+name,437);p=Path(r['path']);assert p.stat().st_size==r['bytes'] and sha(p)==r['sha256']
old=read(K.parent/'rct590/collection001.json');stage=read(K.parent/'rct590/stage001.json')
assert old['completed'] and old['hook_removed'] and read(K.parent/'rct590/final001.json')['closed']
expected={};restore=[]
for n,r in files.items():
 if not n.startswith('game/'):continue
 remote='/E/xwn589-kit/'+n;prior=old['files'].get(remote,stage['staged'][remote]);assert remote in old['game_rows']
 expected[n[5:]]=dict(bytes=prior['bytes'],sha256=prior['sha256'])
 if prior['sha256']!=r['sha256']:
  assert sha(Path(prior['path']))==prior['sha256'];restore.append(n[5:])
assert len(expected)==502 and set(restore)<= {'Data/Game.cfg','Data/CSS0.DAT'}
assert set(old['game_rows'])=={'/E/xwn589-kit/game/'+n for n in expected}
test=read(K/'controller-host001.json');assert test['passed'] and test['source_sha256']==sha(K/'controller001.py')
space=read(K.parent/'rct590/console-space001.json');remaining=space['projected_remaining_bytes']-128*1024**2
assert remaining>=128*1024**2
free=shutil.disk_usage('C:/').free;assert free-128*1024**2>=20*1024**3
for p in K.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
s=importlib.util.spec_from_file_location('package591controller',K/'controller001.py');c=importlib.util.module_from_spec(s);s.loader.exec_module(c);c.pair.verify();c.boot_work_closed()
(K/'console-space001.json').write_bytes((json.dumps(dict(admitted=True,fresh_free_space_measurement=False,source='Fresh590 photo budget already charged64MiB; subtract additional128MiB for both planned save/load phases, OS growth and allocation',previous_remaining=space['projected_remaining_bytes'],new_allowance=128*1024**2,projected_remaining_bytes=remaining,minimum_spare_bytes=128*1024**2),indent=2)+'\n').encode())
pins={str(p.resolve()):sha(p) for p in K.iterdir() if p.is_file()}
pins.update(read(K.parent/'windows-pair532/preflight001.json')['pins'])
for module in list(sys.modules.values()):
 n=getattr(module,'__file__',None)
 if n:
  p=Path(n).resolve()
  if p.is_relative_to(W) and p.is_file():pins[str(p)]=sha(p)
for rel in ['rct586/final002.json','rct586/binary-review001.json','rct586/phase2-source/media001.json','rct590/final001.json','rct590/collection001.json','rct590/stage001.json','rct566/transfer001.json']:
 p=K.parent/rel;pins[str(p.resolve())]=sha(p)
r=dict(passed=True,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),files=files,reuse_expected=expected,restore_assets=restore,previous_owner_sha256=stage['staged']['/E/xwn589-kit/owner.json']['sha256'],runtime_module_pins=read(K.parent/'context-adapter490/package001.json')['runtime_module_pins'],pins=pins,physical_attempt=591,pc_probe=586,allowed_launches=1,phase=1,overall_experiment='OPEN until planned phase2 or explicit incomplete close',pc_runtime_reopened=False,helper_binary_unchanged=True,retail_executable_unchanged=True,physical_access=False,phase2_loader=dict(path=str(loader),sha256=sha(loader)),host_space=dict(free_bytes=free,projected_new_bytes=128*1024**2,minimum_free_bytes=20*1024**3),limits='Prepared physical save phase only. PC evidence does not qualify Xbox save/load. No FPS/GPU claim.')
out.write_bytes((json.dumps(r,indent=2)+'\n').encode());print('Frozen physical591 save phase',len(files),'files; restore',restore)
