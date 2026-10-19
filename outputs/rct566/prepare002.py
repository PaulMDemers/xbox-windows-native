"""MIT. Prepare a new retail-media NT5 control, never an already-used runtime."""
import hashlib,json,subprocess,sys,time
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sys.path.insert(0,str(W/'tools'));from build_space import require_space
sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
num=566;assert len(sys.argv)==1
T=K.parent/f'rct{num}';e=json.loads((T/'edition.json').read_text());P=Path(e['fixture'])
assert not P.exists() and not (T/'ntfs-preparation001.json').exists()
media=json.loads((K.parent/'rct559/media001.json').read_text())[e['media_index']]
iso=Path('/mnt/c/Users/Paul/Desktop/rct_isos')/media['name'];assert sha(iso)==media['sha256']
source=Path('/home/paul/xbox-windows-native/clean-media404-oem001/disk.qcow2')
assert sha(source)=='ece991e4dc6b662ece2a39dddba384a3c480173cafd89086135f6bb861b7f796'
space=require_space(P,21);P.mkdir(parents=True)
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(source),str(P/'disk.qcow2')],check=True)
chain=json.loads(subprocess.check_output(['qemu-img','info','--backing-chain','--output=json',str(P/'disk.qcow2')]))
assert len(chain)==2 and chain[1]['filename']==str(source)
runtime=json.loads((K.parent/'clean-media404/preparation001.json').read_text())['runtime_pins']
for n,h in runtime.items():assert sha(n)==h,n
r=dict(path=str(P),source=str(source),source_sha256=sha(source),child_sha256=sha(P/'disk.qcow2'),
       media=str(iso),iso_sha256=media['sha256'],space=space,chain=chain,runtime_pins=runtime,
       inputs={str(p.resolve()):sha(p) for p in list(K.glob('*.py'))+list(T.glob('*.py'))+[T/'edition.json',K/'DESIGN.md']},
       guest_launched=False,physical_access=False)
(T/'ntfs-preparation001.json').write_text(json.dumps(r,indent=2)+'\n')
print('Prepared',num,media['name'])
