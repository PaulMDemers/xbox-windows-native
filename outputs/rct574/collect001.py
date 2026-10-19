"""MIT. First readback of this fresh, stopped PC control; private logs stay private."""
import hashlib,json,sys
from pathlib import Path
K=Path(__file__).resolve().parent; P=Path('/mnt/c/xwn574/pc001')
sys.path.insert(0,str(K.parent/'crypto-persistence423'));from ntfs_read002 import Reader,sha
state=json.loads((K/'ntfs-phase1.json').read_text())
cold=json.loads((K/'ntfs-cold1-002.json').read_text())
assert state['closed'] and cold['complete'] and sha(P/'disk.qcow2')==state['disk_sha256']==cold['disk_sha256']
out=K/'collection001.json'; dest=P/'collection001'; assert not out.exists() and not dest.exists()
manifest=json.loads((P/'cold1-002/manifest.json').read_text()); dest.mkdir(); rows={}
with Reader(P/'disk.qcow2') as reader:
    for name in sorted(n for n in manifest if n.startswith('xwn574/')):
        if name not in manifest: continue
        data=reader.read(manifest[name]['path']); assert hashlib.sha256(data).hexdigest()==manifest[name]['sha256']
        target=dest/Path(name).name; target.write_bytes(data)
        rows[name]=dict(path=str(target),bytes=len(data),sha256=sha(target))
assert sha(P/'disk.qcow2')==cold['disk_sha256']
out.write_text(json.dumps(dict(completed=True,files=rows,disk_unchanged=True,physical_access=False),indent=2)+'\n')
print('Collected',len(rows),'private runner files')
