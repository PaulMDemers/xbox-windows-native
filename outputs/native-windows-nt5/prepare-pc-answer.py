"""Create a private FAT12 setup floppy using the supplied media's answer key.
Never display or record the key in reports. No licensing bypass is applied.
"""
import io, pathlib, re, struct, sys, hashlib, json
root=pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0,str(root/'work/python-packages'))
import pycdlib
dest=root/'work/pc-fixture';dest.mkdir(exist_ok=True)
target=dest/'answer.img'
if target.exists():raise SystemExit('Refusing to replace an existing answer floppy')
iso=pycdlib.PyCdlib();iso.open(str(root/'outputs/Windows 2000 (SP4).iso'))
buf=io.BytesIO();iso.get_file_from_iso_fp(buf,iso_path='/I386/WINNT.SIF');iso.close()
text=buf.getvalue().decode('cp1252')
match=re.search(r'(?im)^\s*ProductID\s*=\s*"?([A-Z0-9]{5}(?:-[A-Z0-9]{5}){4})',text)
if not match:raise SystemExit('Supplied answer file has no usable product ID')
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
TimeZone=035
[UserData]
ProductID=KEY_PLACEHOLDER
FullName="Xbox Native Development"
OrgName="Local Test Fixture"
ComputerName=XWN-PC
[Identification]
JoinWorkgroup=WORKGROUP
[Networking]
InstallDefaultComponents=Yes
'''
payload=answer.replace('KEY_PLACEHOLDER',match[1]).replace('\n','\r\n').encode('ascii')
image=bytearray(1474560)
image[:3]=b'\xeb\x3c\x90';image[3:11]=b'XWNSETUP'
struct.pack_into('<HBHBHHBHHHII',image,11,512,1,1,2,224,2880,0xf0,9,18,2,0,0)
image[36:39]=b'\x00\x00\x29';struct.pack_into('<I',image,39,0x20261003)
image[43:54]=b'XWN ANSWER ';image[54:62]=b'FAT12   ';image[510:512]=b'\x55\xaa'
fat=bytearray(4608);fat[:3]=b'\xf0\xff\xff'
def entry(n,value):
    off=n+n//2
    if n&1: fat[off]=(fat[off]&15)|((value&15)<<4);fat[off+1]=value>>4
    else:fat[off]=value&255;fat[off+1]=(fat[off+1]&240)|(value>>8)
count=(len(payload)+511)//512
for n in range(2,2+count):entry(n,0xfff if n==count+1 else n+1)
image[512:512+4608]=fat;image[512+4608:512+9216]=fat
off=19*512;image[off:off+11]=b'WINNT   SIF';image[off+11]=0x20
struct.pack_into('<H',image,off+26,2);struct.pack_into('<I',image,off+28,len(payload))
image[33*512:33*512+len(payload)]=payload
target.write_bytes(image)
(root/'outputs/native-windows-nt5/setup-answer-redacted.sif').write_text(answer.replace('KEY_PLACEHOLDER','[REDACTED: from supplied media]'))
(dest/'answer-provenance.json').write_text(json.dumps({'source':'user-supplied Windows 2000 (SP4).iso /I386/WINNT.SIF','target_media':'Windows 2000 (SP4).iso','sha256':hashlib.sha256(image).hexdigest(),'key_in_reports':False},indent=2))
print('Created private setup floppy; embedded product ID omitted from output')
