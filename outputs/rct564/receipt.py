"""MIT. Preserve the failed no-disc control receipt and selected game configuration."""
import json,sys,hashlib
from pathlib import Path
K=Path(__file__).resolve().parent;P=Path('/mnt/c/xwn564/pc001')
sys.path.insert(0,str(K.parent/'crypto-persistence423'));from ntfs_read002 import Reader,sha
c=json.loads((K/'ntfs-cold1-002.json').read_text());assert c['complete'] and sha(P/'disk.qcow2')==c['disk_sha256']
dest=P.parent/'selected001';assert not dest.exists();dest.mkdir();rows={}
with Reader(P/'disk.qcow2') as reader:
 for n in ['xwn565/runner.txt','xwn565/registry.bin','xwn565-kit/game/Data/Game.cfg']:
  b=reader.read(n);p=dest/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b);rows[n]=dict(path=str(p),bytes=len(b),sha256=sha(p))
assert sha(P/'disk.qcow2')==c['disk_sha256']
log=(dest/'xwn565/runner.txt').read_text();out=K/'receipt001.json';assert not out.exists()
out.write_text(json.dumps(dict(files=rows,log=log,game_without_disc_passed=False,transfer_qualified=False,scope='Preserved failed control, not game acceptance'),indent=2)+'\n');print(log)
