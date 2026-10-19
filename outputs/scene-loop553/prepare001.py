"""New private overlay of the CLOSED 404 NTFS source plus a read-only test floppy."""
import hashlib,json,struct,subprocess,sys
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'crypto-persistence423'))
from ntfs_read002 import sha
K=Path(__file__).resolve().parent;W=K.parents[1]
P=Path('/home/paul/xbox-windows-native/scene-loop553-pc001')
source=Path('/home/paul/xbox-windows-native/clean-media404-oem001/disk.qcow2')
sys.path.insert(0,str(W/'tools'));from build_space import require_space
assert not P.exists() and not (K/'ntfs-preparation001.json').exists()
review=json.loads((K.parent/'crypto-persistence423/preflight002.json').read_text());assert review['passed'] and sha(source)==review['source_sha256']
space=require_space(P,20+128/1024)
for name,h in review['package_files'].items():assert sha(Path('/mnt/e/xwn423/ntfs-python001')/name)==h
build=json.loads((K/'build001.json').read_text());assert build['exit_code']==0
P.mkdir();image=bytearray(1474560);image[:3]=b'\xeb\x3c\x90';image[3:11]=b'XWN553  '
struct.pack_into('<HBHBHHBHHHII',image,11,512,1,1,2,224,2880,0xf0,9,18,2,0,0)
image[36:39]=b'\0\0\x29';struct.pack_into('<I',image,39,0x20261017);image[43:54]=b'XWN553TEST ';image[54:62]=b'FAT12   ';image[510:512]=b'\x55\xaa'
fat=bytearray(4608);fat[:3]=b'\xf0\xff\xff'
def entry(n,v):
 off=n+n//2
 if n&1:fat[off]=(fat[off]&15)|((v&15)<<4);fat[off+1]=v>>4
 else:fat[off]=v&255;fat[off+1]=(fat[off+1]&240)|(v>>8)
cluster=2
for i,row in enumerate(build['rows']):
 p=Path(row['path']);assert sha(p)==row['sha256'];data=p.read_bytes();name=p.stem.upper().ljust(8).encode()+b'EXE';count=(len(data)+511)//512
 for n in range(cluster,cluster+count):entry(n,0xfff if n==cluster+count-1 else n+1)
 off=19*512+i*32;image[off:off+11]=name;image[off+11]=0x20;struct.pack_into('<H',image,off+26,cluster);struct.pack_into('<I',image,off+28,len(data))
 at=(33+cluster-2)*512;image[at:at+len(data)]=data;cluster+=count
assert len(image)==1474560
image[512:512+4608]=fat;image[512+4608:512+9216]=fat
from floppy_check import validate
floppy_review=validate(bytes(image),{Path(r['path']).name.upper():Path(r['path']).read_bytes() for r in build['rows']})
(P/'probe.img').write_bytes(image)
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(source),str(P/'disk.qcow2')],check=True,stdout=subprocess.DEVNULL)
info=json.loads(subprocess.check_output(['qemu-img','info','--backing-chain','--output=json',str(P/'disk.qcow2')]))
assert len(info)==2 and info[1]['filename']==str(source) and info[0]['virtual-size']==2*1024**3
pins={p.name:sha(p) for p in K.glob('*.py')};pins['runner.c']=sha(K/'runner.c')
record={'path':str(P),'source':str(source),'source_sha256':sha(source),'floppy_sha256':sha(P/'probe.img'),'child_sha256':sha(P/'disk.qcow2'),'space':space,'chain':info,'inputs':pins,'runtime_pins':json.loads((K.parent/'clean-media404/preparation001.json').read_text())['runtime_pins'],'physical_access':False,'guest_launched':False,'floppy_review':floppy_review,'scope':'New child continuation of 404 clean NTFS install, not a repeated clean ISO installation'}
(K/'ntfs-preparation001.json').write_text(json.dumps(record,indent=2)+'\n');print('Fresh NTFS child and immutable test floppy prepared.')
