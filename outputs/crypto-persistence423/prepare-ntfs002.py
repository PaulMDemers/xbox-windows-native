"""Adopt NEVER-BOOTED exact001 child after read-only auditor refusal, no disk writes."""
import json,sys
from pathlib import Path
from ntfs_read002 import sha,Volume
K=Path(__file__).resolve().parent;P=Path('/home/paul/xbox-windows-native/crypto423-ntfs001')
assert not (K/'ntfs-preparation002.json').exists() and not list(P.glob('phase*'))
old=json.loads((K/'ntfs-preparation001.json').read_text());assert sha(P/'disk.qcow2')==old['child_sha256'] and sha(P/'probe.img')==old['floppy_sha256'] and sha(Path(old['source']))==old['source_sha256']
review=json.loads((K/'preflight003.json').read_text());assert review['passed']
# Verify bounded chunking without allocating a 44 MB model input.
class Model:
 def __init__(self):self.pos=0;self.calls=[]
 def seek(self,p):self.pos=p
 def read(self,n):assert n<=1024**2;self.calls.append(n);return b'Q'*n
raw=Model();v=Volume(raw,512,50*1024**2);data=v.read(44033096)
assert len(data)==44033096 and data==b'Q'*len(data) and len(raw.calls)==42 and v.tell()==len(data)
old['inputs']={p.name:sha(p) for p in K.glob('*.py')};old['inputs']['probe.c']=sha(K/'probe.c')
old['adoption']={'never_booted':True,'child_and_floppy_byte_identical':True,'prior_preparation':'ntfs-preparation001.json','reason':'Read-only cold auditor refused 44,033,096-byte driver.cab extent; bounded 1 MiB transport chunking now tested','failed_audit_preserved':str(P/'cold0'),'model_bytes':len(data),'maximum_nbd_read':max(raw.calls),'calls':len(raw.calls)}
(K/'ntfs-preparation002.json').write_text(json.dumps(old,indent=2)+'\n');print('Never-booted child unchanged; bounded reader002 adopted.')
