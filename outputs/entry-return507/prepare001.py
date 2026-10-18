"""Stage exact499 in a fresh child of never-executed466 preparation."""
import hashlib,json,shutil,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];O=Path('/mnt/c/xwn507/preparation001');S=Path('/mnt/c/xwn466/preparation001/seed.qcow2')
out=K/'preparation001.json';assert not out.exists() and not O.exists()
assert shutil.disk_usage('/mnt/c').free-768*1024**2>=20*1024**3
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
prior=json.loads((K.parent/'marker-handoff466/preparation001.json').read_text());assert prior['seed_never_executed'] and sha(S)==prior['seed_sha256']
X=Path('/mnt/c/xwn504/build001/default.xbe');assert sha(X)=='95a9734048b552fb531cd0c83138f9d7b332c8542573a4f49d5fa385fb0b4ece'
sys.path.insert(0,str(W/'outputs/video-text-oracle206'));from common import ColdIO,m
sys.path.insert(0,str(W/'outputs/fresh-assembly405'));from writeio001 import WriteIO
m.fatx.PARTITIONS['E']=(5633024*512,10000048*512)
O.mkdir(parents=True);child=O/'seed.qcow2';r=dict(status='preparing',physical_access=False,seed_never_executed=True,source_sha256=sha(S),candidate_sha256=sha(X))
try:
 subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b','../../xwn466/preparation001/seed.qcow2',str(child)],check=True,timeout=30)
 with WriteIO(child,10000000000,O) as io:
  wr=m.Writer(io,m.fatx.open_partition(io,child,'E'))
  change=wr.write('Applications/XWNBoot504a/default.xbe',X.read_bytes());wr.flush();io.flush()
 with ColdIO(child) as io:
  wr=m.Writer(io,m.fatx.open_partition(io,child,'E'));assert wr.read('Applications/XWNBoot504a/default.xbe')==X.read_bytes()
  assert hashlib.sha256(wr.read('Applications/XWNEBoot/default.xbe')).hexdigest()=='6240a801d97c4894e56d516a934059da056446fb77cf895b5364bdd6cd24be9a'
 assert sha(S)==prior['seed_sha256']
 check=json.loads(subprocess.check_output(['qemu-img','check','--output=json',str(child)],timeout=30));assert not check.get('corruptions',0) and not check.get('leaks',0)
 r.update(status='prepared',seed=str(child),seed_sha256=sha(child),change=change,qcow_check=check,original_launcher_unchanged=True,source_unchanged=True)
except BaseException as e:r.update(status='failed',error=repr(e));raise
finally:out.write_bytes((json.dumps(r,indent=2)+'\n').encode())
