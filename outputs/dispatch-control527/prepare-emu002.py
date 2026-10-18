"""Fresh unused blank fixture; stage owned folder before first execution."""
import hashlib,json,shutil,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];O=Path('/mnt/c/xwn527/preparation002')
S=Path('/mnt/c/Emulators/xemu/system/xbox_hdd.qcow2');X=Path('/mnt/c/xwn527/build001/bin/default.xbe')
out=K/'preparation002.json';assert not O.exists() and not out.exists()
assert shutil.disk_usage('/mnt/c').free-768*1024**2>=20*1024**3
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
build=json.loads((K/'build001.json').read_text());assert build['compiled'] and build['sdk_unchanged']
assert sha(X)==build['outputs']['bin\\default.xbe']['sha256']
sys.path.insert(0,str(W/'outputs/video-text-oracle206'));from common import ColdIO,m
sys.path.insert(0,str(W/'outputs/fresh-assembly405'));from writeio001 import WriteIO
m.fatx.PARTITIONS['E']=(5633024*512,10000048*512)
O.mkdir(parents=True);child=O/'seed.qcow2'
r=dict(status='preparing',physical_access=False,seed_never_executed=True,base=str(S),base_sha256=sha(S),candidate_sha256=sha(X),changes=[])
try:
 subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b','../../Emulators/xemu/system/xbox_hdd.qcow2',str(child)],check=True,timeout=30)
 owner=b'{"case":"dispatch527-emu001","purpose":"standalone runtime; no Windows"}\n'
 with WriteIO(child,8589934592,O) as io:
  wr=m.Writer(io,m.fatx.open_partition(io,child,'E'))
  for name,data in [('owner.json',owner),('default.xbe',X.read_bytes())]:
   r['changes'].append(wr.write('Applications/XWNDispatch527/'+name,data))
  wr.flush();io.flush()
 with ColdIO(child) as io:
  wr=m.Writer(io,m.fatx.open_partition(io,child,'E'))
  assert wr.read('Applications/XWNDispatch527/default.xbe')==X.read_bytes()
  assert wr.read('Applications/XWNDispatch527/owner.json')==owner
 assert sha(S)==r['base_sha256']
 check=json.loads(subprocess.check_output(['qemu-img','check','--output=json',str(child)],timeout=30));assert not check.get('corruptions',0) and not check.get('leaks',0)
 r.update(status='prepared',seed=str(child),seed_sha256=sha(child),qcow_check=check,base_unchanged=True)
except BaseException as e:r.update(status='failed',error=repr(e));raise
finally:out.write_text(json.dumps(r,indent=2)+'\n')
