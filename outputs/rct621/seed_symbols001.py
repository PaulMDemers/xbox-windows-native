"""Read three exact protected DLLs from immutable seed, never reopen621 runtime."""
from pathlib import Path
import hashlib,json,sys,shutil
K=Path(__file__).resolve().parent
sys.path.insert(0,str(K.parent/'crypto-persistence423'))
from ntfs_read002 import Reader,sha
out=K/'seed-symbols001.json';dest=Path('/mnt/c/xwn621/seed-symbols001');assert not out.exists() and not dest.exists()
p=json.loads((K/'ntfs-preparation001.json').read_text());seed=Path(p['source']);assert sha(seed)==p['source_sha256']
m=json.loads(Path('/mnt/c/xwn621/pc001/cold1-002/manifest.json').read_text())
assert min(shutil.disk_usage('/mnt/c').free,shutil.disk_usage('/mnt/e').free)-10*1024**2>20*1024**3
dest.mkdir();rows=[]
with Reader(seed) as r:
 for n in ['winmm.dll','ntdll.dll','gdi32.dll']:
  v=m['winnt/system32/'+n];data=r.read(v['path']);h=hashlib.sha256(data).hexdigest();assert len(data)==v['bytes'] and h==v['sha256']
  f=dest/n;f.write_bytes(data);rows.append(dict(name=n,path=str(f),bytes=len(data),sha256=h,equals621_protected_file=True))
assert sha(seed)==p['source_sha256']
out.write_text(json.dumps(dict(passed=True,seed=str(seed),seed_sha256=p['source_sha256'],seed_unchanged=True,runtime_reopened=False,files=rows),indent=2)+'\n')
print('Three exact protected DLLs exported from immutable seed;621 not reopened')
