import json,hashlib,sys
from pathlib import Path
k=Path(__file__).resolve().parent;w=k.parents[1];sys.path.insert(0,str(w/'tools'));from build_space import require_space
sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
r=json.loads((k/'ntfs-preparation001.json').read_text());p=Path(r['path']);assert not (p/'phase1').exists() and not (k/'ntfs-phase1.json').exists()
assert sha(p/'disk.qcow2')==r['child_sha256']==json.loads((k/'ntfs-cold0-002.json').read_text())['disk_sha256']
for name,h in r['inputs'].items():assert sha(name)==h,name
m=json.loads((k/'media002.json').read_text());media=Path(m['path'].replace(chr(92),'/').replace('C:/','/mnt/c/'));assert sha(media)==m['sha256']
assert json.loads((k/'media-review002.json').read_text())['passed']
r['helper_media']=str(media);r['helper_sha256']=m['sha256'];r['space']=require_space(p,21)
r['amends_preparation001_sha256']=sha(k/'ntfs-preparation001.json');r['reason']='Correct pre-execution allowlisted Welcome path from independent immutable-seed cold manifest. No guest was launched; same unused child and cold0. Original admission retained. 21GiB prelaunch threshold unchanged.'
for name in ['runner003.c','build003.py','media002.py','vm002.py','amend001.py','media002.json','media-review002.json','runner-build003.json']:
 r['inputs'][str((k/name).resolve())]=sha(k/name)
out=k/'ntfs-preparation002.json';assert not out.exists();out.write_text(json.dumps(r,indent=2)+'\n');print('Amended unused fixture admission; threshold unchanged')
