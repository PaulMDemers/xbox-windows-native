"""Mutate actual fresh fixture metadata in RAM; never edit preserved disk."""
import hashlib,json,struct
from pathlib import Path
from reader import Volume,Refusal
from ntfs_header import validate
K=Path(__file__).resolve().parent;P=Path('E:/xwn429/fixture001');out=K/'tests001.json'
assert not out.exists();original=(P/'fatx.raw').read_bytes();inner=(P/'inner.ntfs').read_bytes()
r=json.loads((K/'fixture001.json').read_text());assert r['passed']
assert hashlib.sha256(original).hexdigest()==r['disk_sha256']
START=1048576;SIZE=64*1024**2;FAT=START+4096;DATA=START+4096+32768;tests=[]
def read_image(data):return lambda at,n:bytes(data[at:at+n])
def scan(data):return Volume(read_image(data),len(data),START,SIZE).scan()
def refuse(name,action):
 try:action()
 except Refusal:tests.append(name)
 else:raise AssertionError('accepted '+name)
def mutate(name,at,fmt,value,resolve=False):
 b=bytearray(original);struct.pack_into(fmt,b,at,value)
 def action():
  v=scan(b)
  if resolve:v.contiguous(b'/windows.img')
 refuse(name,action)
mutate('invalid sectors',START+8,'<I',3)
mutate('root unsupported',START+12,'<I',2)
mutate('file self cycle',FAT+2*2,'<H',2)
mutate('file free middle',FAT+2*4,'<H',0)
mutate('bad cluster link',FAT+2*4,'<H',0xfff7)
mutate('reserved cluster link',FAT+2*4,'<H',0xfff0)
mutate('out of volume link',FAT+2*4,'<H',20000)
mutate('truncated chain',FAT+2*4,'<H',0xffff)
mutate('orphan allocated',FAT+2*10000,'<H',0xffff)
mutate('crosslink root/file',DATA+44,'<I',1)
mutate('nonzero missing chain',DATA+44,'<I',0)
mutate('file length too long',DATA+48,'<I',r['files']['inner.ntfs']['bytes']+65536+4096)
mutate('file length shorter allocated',DATA+48,'<I',512)
mutate('invalid name length',DATA,'B',43)
mutate('forbidden slash',DATA+2,'B',47)
mutate('directory self-cycle',DATA+1,'B',16)
mutate('early directory end causes orphan',DATA,'B',0)
b=bytearray(original);b[DATA+64:DATA+128]=b[DATA:DATA+64];refuse('duplicate name',lambda:scan(b))
# A legal ownership chain with swapped adjacent cluster order is still refused
# as an image mapping, independently of corrupt NTFS contents.
b=bytearray(original)
for c,n in ((2,4),(4,3),(3,5)):struct.pack_into('<H',b,FAT+2*c,n)
refuse('valid fragmented chain',lambda:scan(b).contiguous(b'/windows.img'))
v=scan(original);f=v.contiguous(b'/WINDOWS.IMG');assert f.starts[0]==r['discovery']['file_start']
for path in (b'/missing',b'/../windows.img',b'windows.img',b'//windows.img',b'/\xff'):
 refuse('path '+repr(path),lambda path=path:v.contiguous(path))
refuse('second scan',v.scan)
for nth in range(1,6):
 calls=[0]
 def short(at,n):
  calls[0]+=1;a=original[at:at+n];return a[:-1] if calls[0]==nth else a
 def action():
  q=Volume(short,len(original),START,SIZE)
  try:q.scan()
  except Refusal:
   assert q.failed and not q.scanned
   refuse('failed scan cannot resolve',lambda:q.contiguous(b'/windows.img'))
   raise
 refuse('short read '+str(nth),action)
# Changed metadata between the two observations must refuse, without claiming
# that successful rereads exclude arbitrary live-disk ABA.
counts={}
def changed(at,n):
 counts[at]=counts.get(at,0)+1;a=bytearray(original[at:at+n])
 if at==START and counts[at]==2:a[4]^=1
 return bytes(a)
refuse('metadata reread changed',lambda:Volume(changed,len(original),START,SIZE).scan())
for attr,val in [('MAX_ENTRIES',0),('MAX_DIRS',0),('MAX_CLUSTERS',16)]:
 old=getattr(Volume,attr);setattr(Volume,attr,val)
 try:refuse('capacity '+attr,lambda:scan(original))
 finally:setattr(Volume,attr,old)
# FAT32 synthetic on-disk encoding; no native FAT32 runtime claim.
size32=32*1024**2;start32=512;count=size32//512;fs=(count*4+4095)&~4095;d=start32+4096+fs
b=bytearray(start32+size32);b[start32:start32+4]=b'FATX';struct.pack_into('<III',b,start32+4,123,1,1)
struct.pack_into('<II',b,start32+4096,0xfffffff8,0xffffffff)
b[d:d+512]=b'\xff'*512;e=bytearray(64);e[0]=5;e[1]=32;e[2:7]=b'I.IMG';struct.pack_into('<II',e,44,2,131072);b[d:d+64]=e
for c in range(2,258):struct.pack_into('<I',b,start32+4096+4*c,c+1 if c<257 else 0xffffffff)
q=Volume(read_image(b),len(b),start32,size32).scan();assert q.width==4 and len(q.contiguous(b'/i.img').chain)==256
tests.append('FAT32 complete raw ownership')
# Same byte fixture addressed above128GiB, proving arithmetic only.
delta=1<<37
q=Volume(lambda at,n:bytes(b[at-delta:at-delta+n]),len(b)+delta,start32+delta,size32).scan()
assert q.contiguous(b'/i.img').starts[0]==d+512+delta;tests.append('64bit physical origin')
boot=inner[:512];backup=inner[-512:];start=r['discovery']['inner_start'];serial=struct.unpack_from('<Q',boot,72)[0]
for at,fmt,value in [(11,'<H',4096),(13,'B',3),(28,'<I',0),(40,'<Q',len(inner)//512),(48,'<Q',0),(56,'<Q',2**63),(64,'b',0),(68,'b',-17),(72,'<Q',serial^1),(510,'<H',0)]:
 a=bytearray(boot);struct.pack_into(fmt,a,at,value)
 refuse('NTFS semantic '+str(at),lambda a=bytes(a):validate(a,a,len(inner),start,serial))
refuse('backup differs',lambda:validate(boot,backup[:-1]+b'0',len(inner),start,serial))
assert hashlib.sha256((P/'fatx.raw').read_bytes()).hexdigest()==r['disk_sha256']
record=dict(passed=True,cases=len(tests),tests=tests,original_fixture_unchanged=True,inputs={n:hashlib.sha256((K/n).read_bytes()).hexdigest() for n in ('reader.py','ntfs_header.py','tests001.py')},scope='Actual fixture mutations and synthetic FAT32/high origin, host-only; no native mount/exclusion proof')
out.write_text(json.dumps(record,indent=2)+'\n');print(json.dumps({'passed':True,'cases':len(tests)}))
