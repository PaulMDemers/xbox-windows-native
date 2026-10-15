"""Transparent NTFS compression of closed cold captures with exact before/after hashes."""
import hashlib,json,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent;root=Path('C:/xwn405').resolve();out=K/'compression008.json';assert not out.exists()
folders=[root/n for n in ['cold001','cold002','cold004','cold005','cold006']]
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
before={str(p):sha(p) for d in folders for p in d.rglob('*') if p.is_file()}
assert all(Path(p).resolve().is_relative_to(root) for p in before)
for d in folders:
    r=subprocess.run(['compact.exe','/C','/I','/Q','/S:'+str(d)],capture_output=True,text=True,timeout=60)
    assert r.returncode==0,r.stdout+r.stderr
assert all(sha(Path(p))==h for p,h in before.items())
with out.open('x') as f:json.dump(dict(files=before,exact_readback=True,scope='Transparent host storage compression; no guest disk, path or captured content change'),f,indent=2);f.write('\n')
print('Closed cold captures compressed and rehashed',len(before))
