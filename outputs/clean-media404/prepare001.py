"""Fresh private blank PC fixture and answer floppy; never print product keys."""
import hashlib,io,json,os,re,struct,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sys.path.insert(0,str(W/'work/python-packages'));import pycdlib
sys.path.insert(0,str(W/'tools'));from build_space import require_space
P=Path('/home/paul/xbox-windows-native/clean-media404-oem001');space=require_space(P);P.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
media=W/'outputs/Windows 2000 (SP4).iso';expected='75ae5e4980e074377d3f0c2ab2e82dff0e3f80400da13c8e2d5a1479d2ccda1f'
assert sha(media)==expected
iso=pycdlib.PyCdlib();iso.open(str(media));b=io.BytesIO();iso.get_file_from_iso_fp(b,iso_path='/I386/WINNT.SIF');iso.close()
match=re.search(rb'(?im)^\s*ProductID\s*=\s*"?([A-Z0-9]{5}(?:-[A-Z0-9]{5}){4})',b.getvalue());assert match
answer='''[Data]
AutoPartition=1
MsDosInitiated="0"
UnattendedInstall="Yes"
[Unattended]
UnattendMode=FullUnattended
OemSkipEula=Yes
OemPreinstall=No
TargetPath=WINNT
FileSystem=ConvertNTFS
Repartition=Yes
WaitForReboot=No
[GuiUnattended]
AdminPassword=*
EncryptedAdminPassword="No"
OEMSkipRegional=1
OemSkipWelcome=1
AutoLogon=Yes
AutoLogonCount=2
TimeZone=035
[UserData]
ProductID=PRIVATE_KEY_PLACEHOLDER
FullName="Clean Media Validation"
OrgName="Local Isolated Fixture"
ComputerName=XWN-CLEAN404
[Identification]
JoinWorkgroup=WORKGROUP
[Networking]
InstallDefaultComponents=Yes
[GuiRunOnce]
"A:\\PROBE.EXE"
'''
payload=answer.replace('PRIVATE_KEY_PLACEHOLDER',match[1].decode()).replace('\n','\r\n').encode('ascii')
probe=Path('/home/paul/xbox-windows-native/clean-media404-build002/PROBE.EXE')
assert sha(probe)==json.loads((K/'probe-build002.json').read_text())['binary_sha256']
image=bytearray(1474560);image[:3]=b'\xeb\x3c\x90';image[3:11]=b'XWN404  '
struct.pack_into('<HBHBHHBHHHII',image,11,512,1,1,2,224,2880,0xf0,9,18,2,0,0)
image[36:39]=b'\0\0\x29';struct.pack_into('<I',image,39,0x20261015);image[43:54]=b'XWN CLEAN  ';image[54:62]=b'FAT12   ';image[510:512]=b'\x55\xaa'
fat=bytearray(4608);fat[:3]=b'\xf0\xff\xff'
def entry(n,v):
 off=n+n//2
 if n&1:fat[off]=(fat[off]&15)|((v&15)<<4);fat[off+1]=v>>4
 else:fat[off]=v&255;fat[off+1]=(fat[off+1]&240)|(v>>8)
cluster=2
for index,(name,data) in enumerate([(b'WINNT   SIF',payload),(b'PROBE   EXE',probe.read_bytes())]):
 count=(len(data)+511)//512
 for n in range(cluster,cluster+count):entry(n,0xfff if n==cluster+count-1 else n+1)
 off=19*512+index*32;image[off:off+11]=name;image[off+11]=0x20
 struct.pack_into('<H',image,off+26,cluster);struct.pack_into('<I',image,off+28,len(data))
 at=(33+cluster-2)*512;image[at:at+len(data)]=data;cluster+=count
image[512:512+4608]=fat;image[512+4608:512+9216]=fat
(P/'answer.img').write_bytes(image);os.chmod(P/'answer.img',0o600)
subprocess.run(['qemu-img','create','-f','qcow2',str(P/'disk.qcow2'),'2G'],check=True,stdout=subprocess.DEVNULL)
runtime=Path('/home/paul/xbox-windows-native/toolchains/qemu-pc/root')
pins={str(p):sha(p) for p in [runtime/'usr/bin/qemu-system-i386',runtime/'usr/share/seabios/bios.bin',runtime/'usr/share/seabios/vgabios-cirrus.bin'] if p.exists()}
r={'fixture':str(P),'media':str(media),'iso_sha256':expected,'iso_sha1':hashlib.sha1(media.read_bytes()).hexdigest(),'blank_disk_sha256':sha(P/'disk.qcow2'),'answer_sha256':sha(P/'answer.img'),'probe_sha256':sha(probe),'runtime_pins':pins,'space':space,'key_source':'Only this supplied OEM disc WINNT.SIF; value never in reports','blank_disk_no_parent':True,'network_device':False,'physical_access':False}
(K/'answer-redacted.sif').write_text(answer.replace('PRIVATE_KEY_PLACEHOLDER','[PRIVATE: supplied media]'))
(K/'preparation001.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'prepared':True,'fixture':str(P),'media_sha256':expected}))
