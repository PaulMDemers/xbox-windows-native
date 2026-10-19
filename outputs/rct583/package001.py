"""Freeze exact qualified runner and verified pristine assets, with bounded reuse budget."""
import ast,datetime,hashlib,importlib.util,json,shutil,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
host=lambda p:Path(p.replace('/mnt/c/','C:/'))
out=K/'package001.json';assert not out.exists() and not (K/'console-space001.json').exists()
final=read(K.parent/'rct584/final001.json');assert final['closed'] and final['input_qualified'] and final['cleanup_qualified'] and final['late_welcome_qualified']
for n,h in final['pins'].items():assert sha(K.parent/'rct584'/n)==h,n
test=read(K/'controller-host002.json');assert test['passed'] and test['source_sha256']==sha(K/'controller001.py')
b=read(K.parent/'rct582/build001.json');assert b['status']=='compiled'
for n,row in b['files'].items():assert sha(host(n))==row['sha256'],n
source=read(K.parent/'rct566/transfer001.json');assert source['passed']
files={n:dict(v,path=str(host(v['path']))) for n,v in source['files'].items()}
row=next(v for v in b['rows'] if v['path'].endswith('/run582.exe'));files['run582.exe']=dict(row,path=str(host(row['path'])))
assert row['bytes']<65536
sys.path.insert(0,str(W/'tools'));from fatx_names import check_path
for n,row in files.items():
 check_path('xwn582-kit/'+n,437);p=Path(row['path']);assert p.stat().st_size==row['bytes'] and sha(p)==row['sha256']
old=read(K.parent/'rct576/collection001.json');assert old['completed'] and old['hook_removed'] and read(K.parent/'rct576/final001.json')['closed']
expected={};restore=[]
for name,row in files.items():
 if not name.startswith('game/'):continue
 rel=name[5:];remote='/E/xwn575-kit/'+name;prior=old['files'].get(remote,row)
 assert remote in old['game_rows'];expected[rel]=dict(bytes=prior['bytes'],sha256=prior['sha256'])
 if prior['sha256']!=row['sha256']:
  assert sha(Path(prior['path']))==prior['sha256'];restore.append(rel)
assert set(restore)=={'Data/CSS0.DAT','Data/Game.cfg'} and len(expected)==502
space=read(K.parent/'rct576/console-space001.json');actual=sum(v['bytes'] for n,v in old['files'].items() if n.startswith('/E/xwn575/'))
remaining=space['projected_remaining_bytes']+space['charges']['new_results_allowance']-actual-24*1024**2-4*1024**2-65536
assert remaining>=128*1024**2
(K/'console-space001.json').write_text(json.dumps(dict(admitted=True,fresh_free_space_measurement=False,source='Previous576 conditional recorded-write budget, credit unused576 result allowance after exact collection; verified-assets-only move has no533MB allocation',previous_remaining=space['projected_remaining_bytes'],previous_result_allowance=space['charges']['new_results_allowance'],actual576_result_bytes=actual,new_result_allowance=24*1024**2,new_allocation_allowance=4*1024**2,new_helper_owner_allowance=65536,projected_remaining_bytes=remaining,minimum_spare_bytes=128*1024**2,assumptions=['No unrecorded external writes since dashboard reading','Not a fresh FATX free-cluster measurement; any mismatch/disk-full stops before hook']),indent=2)+'\n')
free=shutil.disk_usage('C:/').free;assert free-128*1024**2>=20*1024**3
for p in K.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
s=importlib.util.spec_from_file_location('package583controller',K/'controller001.py');c=importlib.util.module_from_spec(s);s.loader.exec_module(c);c.pair.verify();c.boot_work_closed()
pins={str(p.resolve()):sha(p) for p in K.iterdir() if p.is_file()}
pins.update(read(K.parent/'windows-pair532/preflight001.json')['pins'])
for module in list(sys.modules.values()):
 n=getattr(module,'__file__',None)
 if n:
  p=Path(n).resolve()
  if p.is_relative_to(W) and p.is_file():pins[str(p)]=sha(p)
for rel in ['rct584/final001.json','rct582/build001.json','rct584/integration-review001.json','rct566/transfer001.json','rct576/final001.json','rct576/collection001.json','rct576/stage002.json','context-adapter490/package001.json']:
 p=K.parent/rel;pins[str(p.resolve())]=sha(p)
modules=read(K.parent/'context-adapter490/package001.json')['runtime_module_pins']
owner=read(K.parent/'rct576/stage002.json')['staged']['/E/xwn575-kit/owner.json']['sha256']
r=dict(passed=True,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),files=files,reuse_expected=expected,restore_assets=restore,previous_owner_sha256=owner,runtime_module_pins=modules,pins=pins,physical_attempt=583,pc_probe=584,unchanged_binary_probe=582,allowed_launches=1,pc_injection_flag_staged=False,helper_binary_unchanged=True,retail_executable_unchanged=True,physical_access=False,host_space=dict(free_bytes=free,projected_new_bytes=128*1024**2,minimum_free_bytes=20*1024**3),limits='New physical runtime. Only verified pristine retail assets reused; closed576 remains closed. No FPS/GPU claim.')
out.write_text(json.dumps(r,indent=2)+'\n');print('Frozen assets-only physical583 package',len(files),'files')
