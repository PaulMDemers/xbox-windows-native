"""MIT. Fresh PC input-control child from the immutable404 NTFS seed."""
import hashlib,json,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent; W=K.parents[1]
sys.path.insert(0,str(W/'tools'));from build_space import require_space
sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
P=Path('/mnt/c/xwn584/pc001'); out=K/'ntfs-preparation001.json'
assert not P.exists() and not out.exists()
source=Path('/home/paul/xbox-windows-native/clean-media404-oem001/disk.qcow2')
assert sha(source)=='ece991e4dc6b662ece2a39dddba384a3c480173cafd89086135f6bb861b7f796'
helper=json.loads((K/'media001.json').read_text()); media=Path(helper['path'].replace(chr(92),'/').replace('C:/','/mnt/c/'))
assert sha(media)==helper['sha256']
review=json.loads((K/'media-review001.json').read_text()); assert review['passed'] and review['media_sha256']==helper['sha256']
retail=json.loads((K.parent/'rct577/disc-mapping001.json').read_text())['source_iso']; retail_path=retail['path'].replace(chr(92),'/').replace('C:/','/mnt/c/'); assert sha(retail_path)==retail['sha256']
runtime=json.loads((K.parent/'clean-media404/preparation001.json').read_text())['runtime_pins']
for p,h in runtime.items(): assert sha(p)==h,p
space=require_space(P,21); P.mkdir()
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(source),str(P/'disk.qcow2')],check=True)
chain=json.loads(subprocess.check_output(['qemu-img','info','--backing-chain','--output=json',str(P/'disk.qcow2')]))
assert len(chain)==2 and chain[1]['filename']==str(source)
r=dict(path=str(P),source=str(source),source_sha256=sha(source),child_sha256=sha(P/'disk.qcow2'),helper_media=str(media),helper_sha256=sha(media),retail_media=retail_path,retail_sha256=retail['sha256'],space=space,chain=chain,runtime_pins=runtime,inputs={str(p.resolve()):sha(p) for p in list(K.glob('*.py'))+list(K.glob('*.c'))+list(K.glob('*.h'))+[K/'edition.json',K/'DESIGN.md']},guest_launched=False,physical_access=False)
r['inputs'].update({str(p.resolve()):sha(p) for p in list((K.parent/'rct582').glob('*.c'))+list((K.parent/'rct582').glob('*.h'))+[K.parent/'rct582/build001.json',K.parent/'rct582/media001.json',K.parent/'rct582/final001.json']})
out.write_text(json.dumps(r,indent=2)+'\n'); print('Prepared fresh584, exact582 helper/media')
