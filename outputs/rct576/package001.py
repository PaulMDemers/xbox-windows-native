"""MIT. Freeze an exact qualified helper and supplied retail assets for new hardware runtime."""
import ast,datetime,hashlib,importlib.util,json,shutil,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
read=lambda p:json.loads(p.read_text(encoding='utf8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
host=lambda s:Path(s.replace('/mnt/c/','C:/'))
out=K/'package001.json';spaceout=K/'console-space001.json'
assert not out.exists() and not spaceout.exists()
closed=read(K.parent/'rct575/final001.json')
assert closed['closed'] and closed['input_qualified'] and closed['cleanup_qualified']
for n,h in closed['pins'].items():assert sha(K.parent/'rct575'/n)==h,n
for n in ['controller-host001.json','controller-host002.json']:
 r=read(K/n);assert r['passed'] and r['source_sha256']==sha(K/'controller001.py')
b=read(K.parent/'rct575/runner-build001.json');assert b['status']=='compiled' and b['exit_code']==0
for n,r in b['files'].items():assert sha(host(n))==r['sha256'],n
t=read(K.parent/'rct566/transfer001.json');assert t['passed']
files={n:dict(row,path=str(host(row['path']))) for n,row in t['files'].items()}
row=b['rows'][0];files['run575.exe']=dict(row,path=str(host(row['path'])))
sys.path.insert(0,str(W/'tools'));from fatx_names import check_path
for n,r in files.items():
 check_path('xwn575-kit/'+n,437);p=Path(r['path']);assert p.stat().st_size==r['bytes'] and sha(p)==r['sha256']
assert len({n.lower() for n in files})==len(files)
for n in t['directories']:check_path('xwn575-kit/'+n,437)
total=sum(v['bytes'] for v in files.values())
# Charge the entire565 installation, even files already present at the reported reading.
old=read(K.parent/'rct565/collection002.json');assert old['completed'] and old['hook_removed']
assert read(K.parent/'rct565/final001.json')['closed']
known=sum(v['bytes'] for n,v in old['files'].items() if n.startswith(('/E/xwn565-kit/','/E/xwn565/')))
for n in ['transport-probe001.json','transport-probe003.json','transport-probe005.json']:assert read(K.parent/'rct565'/n)['removed']
assert read(K.parent/'rct565/probe-cleanup001.json')['twice_listed_absent']
reported=read(K.parent/'rct565/console-space001.json')['free_bytes']
charges=dict(recorded565_payload_and_results=known,old_allocation_allowance=64*1024**2,
 os_and_other_growth_allowance=256*1024**2,new_payload=total,new_allocation_allowance=64*1024**2,
 new_results_allowance=32*1024**2)
remaining=reported-sum(charges.values());assert remaining>=128*1024**2
space=dict(admitted=True,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
 fresh_free_space_measurement=False,source='User dashboard reading recorded565 plus recorded-write accounting',
 reported_free_bytes=reported,charges=charges,projected_remaining_bytes=remaining,
 minimum_spare_bytes=128*1024**2,package_bytes=total,
 assumptions=['No unrecorded external writes since the user reading; all subsequent project game controls were PC-only.',
 'Allocation and OS-growth allowances are conservative budgeting, not a FATX free-cluster audit.'],
 limitations='FTP STAT is unsupported; prior HELP framing failures retained. Disk-full or transfer mismatch must stop before hook installation.')
spaceout.write_text(json.dumps(space,indent=2)+'\n')
free=shutil.disk_usage('C:/').free;assert free-128*1024**2>=20*1024**3
for p in K.glob('*.py'):ast.parse(p.read_text(encoding='utf8'),filename=str(p))
spec=importlib.util.spec_from_file_location('physical576package',K/'controller001.py')
c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c);c.pair.verify();c.boot_work_closed()
pins={str(p.resolve()):sha(p) for p in K.iterdir() if p.is_file()}
pins.update(read(K.parent/'windows-pair532/preflight001.json')['pins'])
for module in list(sys.modules.values()):
 n=getattr(module,'__file__',None)
 if n:
  p=Path(n).resolve()
  if p.is_relative_to(W) and p.is_file():pins[str(p)]=sha(p)
for n in ['outputs/rct575/final001.json','outputs/rct575/runner-build001.json','outputs/rct575/input-review001.json','outputs/rct575/notification-review001.json','outputs/rct566/transfer001.json','outputs/rct565/final001.json','outputs/rct565/collection002.json','outputs/context-adapter490/package001.json']:
 p=W/n;pins[str(p.resolve())]=sha(p)
modules=read(K.parent/'context-adapter490/package001.json')['runtime_module_pins']
r=dict(passed=True,files=files,directories=t['directories'],total_bytes=total,pins=pins,
 runtime_module_pins=modules,allowed_launches=1,pc_probe=575,physical_attempt=576,
 helper_binary_unchanged=True,retail_executable_unchanged=True,physical_access=False,
 host_space=dict(c_free_bytes=free,projected_new_bytes=128*1024**2,minimum_free_bytes=20*1024**3,wsl_backing_on_c=True),
 limits='New physical runtime, not reopening PC575. PC qualification does not prove Xbox game behavior, display output, FPS or GPU acceleration.')
out.write_text(json.dumps(r,indent=2)+'\n')
print('Frozen',len(files),'files;',total,'bytes; console conditional remaining',remaining,'bytes; source pins',len(pins))
