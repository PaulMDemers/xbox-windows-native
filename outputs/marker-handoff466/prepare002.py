"""Offline stage the unchanged diagnostic into a fresh never-executed seed child."""
import hashlib,json,shutil,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];O=Path('/mnt/c/xwn466/preparation002')
S=Path('/mnt/c/xwn466/preparation001/seed.qcow2');out=K/'preparation002.json'
assert not out.exists() and not O.exists()
assert shutil.disk_usage('/mnt/c').free-256*1024**2>=20*1024**3
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
prior=json.loads((K/'preparation001.json').read_text());assert sha(S)==prior['seed_sha256']
b=json.loads((K/'build001.json').read_text());X=Path('/mnt/c/xwn466/build001/default.xbe');assert sha(X)==b['sha256']
sys.path.insert(0,str(W/'outputs/video-text-oracle206'));from common import ColdIO,m
sys.path.insert(0,str(W/'outputs/fresh-assembly405'));from writeio001 import WriteIO
m.fatx.PARTITIONS['E']=(5633024*512,10000048*512)
O.mkdir();child=O/'seed.qcow2';r=dict(status='preparing',physical_access=False,seed_never_executed=True)
try:
 subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b','../preparation001/seed.qcow2',str(child)],check=True)
 with WriteIO(child,10000000000,O) as io:
  wr=m.Writer(io,m.fatx.open_partition(io,child,'E'))
  change=wr.write('Applications/XWNBoot466a/default.xbe',X.read_bytes());wr.flush();io.flush()
 with ColdIO(child) as io:
  wr=m.Writer(io,m.fatx.open_partition(io,child,'E'))
  assert wr.read('Applications/XWNBoot466a/default.xbe')==X.read_bytes()
  installed=wr.read('Applications/XWNEBoot/default.xbe')
  assert hashlib.sha256(installed).hexdigest()=='6240a801d97c4894e56d516a934059da056446fb77cf895b5364bdd6cd24be9a'
 assert sha(S)==prior['seed_sha256']
 check=json.loads(subprocess.check_output(['qemu-img','check','--output=json',str(child)]));assert not check.get('corruptions',0) and not check.get('leaks',0)
 r.update(status='prepared',seed=str(child),seed_sha256=sha(child),source_unchanged=True,source_sha256=sha(S),change=change,qcow_check=check,original_launcher_unchanged=True)
except BaseException as e:r.update(status='failed',error=repr(e));raise
finally:out.write_text(json.dumps(r,indent=2)+'\n')
