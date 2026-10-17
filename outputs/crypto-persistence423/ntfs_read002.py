"""Read-only NTFS over the existing owned read-only NBD transport; no mount."""
import hashlib,io,struct,sys
from pathlib import Path
K=Path(__file__).resolve().parent
sys.path.insert(0,str(K.parent/'fatx-mapped-eof'))
sys.path.insert(0,'/mnt/e/xwn423/ntfs-python001')
from coldio import ColdIO
from dissect.ntfs import NTFS

class Volume(io.RawIOBase):
 def __init__(self,raw,start,size):super().__init__();self.raw=raw;self.start=start;self.size=size;self.pos=0
 def readable(self):return True
 def seekable(self):return True
 def tell(self):return self.pos
 def seek(self,offset,whence=0):
  if whence not in (0,1,2):raise ValueError('invalid whence')
  p=offset+(self.pos if whence==1 else self.size if whence==2 else 0)
  if not 0<=p<=self.size:raise ValueError('seek outside partition')
  self.pos=p;return p
 def read(self,n=-1):
  if n is None or n<0:n=self.size-self.pos
  n=min(n,self.size-self.pos)
  if n>64*1024**2:raise ValueError('unbounded NTFS read')
  parts=[]
  while n:
   take=min(n,1024**2);self.raw.seek(self.start+self.pos);data=self.raw.read(take)
   if len(data)!=take:raise EOFError('short read-only partition read')
   parts.append(data);self.pos+=take;n-=take
  return b''.join(parts)
 def readinto(self,b):
  data=self.read(len(b));b[:len(data)]=data;return len(data)

class Reader:
 def __init__(self,path):self.path=path;self.raw=None
 def __enter__(self):
  self.raw=ColdIO(self.path)
  try:
   mbr=self.raw.read(512);assert mbr[510:]==b'\x55\xaa'
   entries=[mbr[446+i*16:462+i*16] for i in range(4)]
   allocated=[e for e in entries if e[4]];assert len(allocated)==1 and allocated[0][4]==7
   lba,sectors=struct.unpack_from('<II',allocated[0],8);self.start=lba*512;self.size=sectors*512
   assert self.start>=512 and self.start+self.size<=self.raw.size
   self.fs=NTFS(Volume(self.raw,self.start,self.size));return self
  except BaseException:self.raw.close();raise
 def read(self,name,limit=64*1024**2):
  with self.fs.mft.get(name).open() as f:
   data=f.read(limit+1);assert len(data)<=limit,name;return data
 def __exit__(self,*args):self.raw.close()

def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
