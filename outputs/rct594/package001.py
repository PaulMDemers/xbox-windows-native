"""MIT. Freeze exact PC593 helper and verified retained assets for one console run."""
import ast,datetime,hashlib,importlib.util,json,shutil,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
host=lambda p:Path(p.replace('/mnt/c/','C:/'))
out=K/'package001.json';assert not out.exists() and not (K/'console-space001.json').exists()
pc=K.parent/'rct593';final=read(pc/'final001.json')
assert final['closed'] and final['passed'] and read(pc/'save-review002.json')['passed']
runtime=read(pc/'ntfs-phase1.json');cold=read(pc/'ntfs-cold1-002.json')
assert runtime['closed'] and runtime['exit_code']==0 and cold['complete'] and cold['normal_shutdown_delta']==1
assert runtime['disk_sha256']==cold['disk_sha256']
helper=Path('C:/xwn593/build002/run593.exe')
compiled=read(pc/'binary-review001.json');assert compiled['passed']
row=next(r for r in compiled['files'] if Path(r['path']).name=='run593.exe');assert sha(helper)==row['sha256']
manifest=read(Path('C:/xwn593/pc001/cold1-002/manifest.json'))
assert manifest['xwn593-kit/run593.exe']['sha256']==sha(helper)
source=read(K.parent/'rct566/transfer001.json');assert source['passed']
files={n:dict(v,path=str(host(v['path']))) for n,v in source['files'].items()}
assert len(files)==502 and all(n.startswith('game/') for n in files)
old=read(K.parent/'rct592/collection001.json');stage=read(K.parent/'rct592/stage001.json')
assert old['completed'] and old['hook_removed'] and read(K.parent/'rct592/final001.json')['closed']
oldsave='/E/xwn586-kit/game/Saved Games/XWN586.SV4'
saved=old['files'][oldsave];assert sha(saved['path'])==saved['sha256']
assert saved['sha256']=='87f2ddaf852a1ebfc9f8b2c734bbdedfffe83ce8e2a97fb33d0bb41ce7909fd2'
files['game/Saved Games/XWN586.SV4']={k:saved[k] for k in ['path','bytes','sha256']}
files['run593.exe']=dict(path=str(helper),bytes=helper.stat().st_size,sha256=sha(helper))
expected={};restore=[]
for n,r in files.items():
    if not n.startswith('game/'):continue
    remote='/E/xwn586-kit/'+n;prior=old['files'].get(remote) or stage['staged'][remote]
    assert remote in old['game_rows'];expected[n[5:]]=dict(bytes=prior['bytes'],sha256=prior['sha256'])
    if prior['sha256']!=r['sha256']:
        assert sha(prior['path'])==prior['sha256'];restore.append(n[5:])
assert len(expected)==503 and set(restore)<= {'Data/Game.cfg','Data/CSS0.DAT'}
assert set(old['game_rows'])=={'/E/xwn586-kit/game/'+n for n in expected}
assert not any(n.lower().endswith('/xwn593.sv4') for n in expected)
sys.path.insert(0,str(W/'tools'));from fatx_names import check_path
for n,r in files.items():
    check_path('xwn593-kit/'+n,437);p=Path(r['path'])
    assert p.stat().st_size==r['bytes'] and sha(p)==r['sha256']
test=read(K/'controller-host002.json');assert test['passed'] and test['source_sha256']==sha(K/'controller001.py')
space=read(K.parent/'rct592/console-space001.json');remaining=space['projected_remaining_bytes']-128*1024**2
assert remaining>=128*1024**2
free=shutil.disk_usage('C:/').free;assert free-128*1024**2>=20*1024**3
for p in K.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
s=importlib.util.spec_from_file_location('package594controller',K/'controller001.py');c=importlib.util.module_from_spec(s);s.loader.exec_module(c);c.pair.verify();c.boot_work_closed()
(K/'console-space001.json').write_text(json.dumps(dict(admitted=True,fresh_free_space_measurement=False,source='Prior592 conservative remaining reserve, minus128MiB for594/next load and OS growth; no duplicated game',previous_remaining=space['projected_remaining_bytes'],new_allowance=128*1024**2,projected_remaining_bytes=remaining,minimum_spare_bytes=128*1024**2),indent=2)+'\n')
pins={str(p.resolve()):sha(p) for p in K.iterdir() if p.is_file()}
pins.update(read(K.parent/'windows-pair532/preflight001.json')['pins'])
for module in list(sys.modules.values()):
    n=getattr(module,'__file__',None)
    if n:
        p=Path(n).resolve()
        if p.is_relative_to(W) and p.is_file():pins[str(p)]=sha(p)
for rel in ['rct593/final001.json','rct593/binary-review001.json','rct593/save-review002.json','rct592/final001.json','rct592/collection001.json','rct592/stage001.json','rct566/transfer001.json']:
    p=K.parent/rel;pins[str(p.resolve())]=sha(p)
r=dict(passed=True,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),files=files,reuse_expected=expected,restore_assets=restore,previous_owner_sha256=stage['staged']['/E/xwn586-kit/owner.json']['sha256'],runtime_module_pins=read(K.parent/'context-adapter490/package001.json')['runtime_module_pins'],pins=pins,physical_attempt=594,pc_probe=593,allowed_launches=1,phase=1,cold_start_confirmed=False,pc_runtime_reopened=False,helper_binary_unchanged=True,retail_executable_unchanged=True,physical_access=False,prior_save_preserved=saved['sha256'],host_space=dict(free_bytes=free,projected_new_bytes=128*1024**2,minimum_free_bytes=20*1024**3),limits='Physical save observation only. Later load required. No FPS/GPU claim.')
out.write_text(json.dumps(r,indent=2)+'\n');print('Frozen594',len(files),'payload entries; restore',restore)
