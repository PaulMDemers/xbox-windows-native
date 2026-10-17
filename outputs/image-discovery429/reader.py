# SPDX-License-Identifier: MIT
"""Bounded read-only FATX ownership discovery. Host prototype, not native code.

Read callback takes absolute byte offset/length; an immutable/offline medium is
required. No claim that two matching reads lock a concurrently writable disk.
"""
import array,struct,sys
from dataclasses import dataclass
class Refusal(ValueError):pass
def require(v,s):
    if not v:raise Refusal(s)
@dataclass(frozen=True)
class File:
    path:bytes
    size:int
    chain:tuple
    starts:tuple
class Volume:
    MAX_CLUSTERS=1048576
    MAX_ENTRIES=32768
    MAX_DIRS=2048
    MAX_DEPTH=32
    def __init__(self,read,disk_bytes,start,size):
        require(all(type(n) is int and 0<n<2**64 and n%512==0 for n in (disk_bytes,start,size)),'geometry')
        require(start+size<=disk_bytes,'partition containment')
        self.read=read;self.disk_bytes=disk_bytes;self.start=start;self.size=size;self.failed=False
        self.read_bytes=0;self.files={};self.directory_count=0;self.entry_count=0
        h=self.fetch(start,4096);require(h[:4]==b'FATX','magic')
        sectors,root=struct.unpack_from('<II',h,8)
        require(sectors in (1,2,4,8,16,32,64,128) and root==1,'cluster/root')
        self.cluster=sectors*512;self.count=size//self.cluster
        require(2<self.count<=self.MAX_CLUSTERS,'cluster capacity')
        self.width=4 if self.count>=0xfff4 else 2
        self.fat_size=(self.count*self.width+4095)&~4095
        self.data=start+4096+self.fat_size
        self.limit=min(self.count,(start+size-self.data)//self.cluster+1)
        require(self.limit>2,'data extent')
        raw=self.fetch(start+4096,self.fat_size)
        self.fat=array.array('I' if self.width==4 else 'H',raw)
        if sys.byteorder!='little':self.fat.byteswap()
        self.eoc=(1<<(8*self.width))-8
        self.owned=bytearray(self.limit)
        self.header=h;self.fat_raw=raw;self.scanned=False;self.started=False
    def fetch(self,offset,count):
        require(not self.failed,'failed reader')
        require(type(offset) is int and type(count) is int and offset>=self.start and count>0 and count<=4*1024**2 and offset+count<=self.start+self.size,'read bound')
        try:
            b=self.read(offset,count)
            require(type(b) is bytes and len(b)==count,'short read')
        except BaseException:
            self.failed=True;raise
        self.read_bytes+=count;return b
    def address(self,c):
        require(1<=c<self.limit,'cluster outside data')
        return self.data+(c-1)*self.cluster
    def claim(self,start):
        result=[];c=start
        while True:
            require(1<=c<self.limit and not self.owned[c],'loop/crosslink/range')
            self.owned[c]=1;result.append(c)
            n=self.fat[c]
            if n>=self.eoc:return tuple(result)
            require(n>0 and n<self.eoc-8,'free/reserved/bad chain')
            c=n
    def scan(self):
        require(not self.started,'one scan per instance');self.started=True
        try:return self._scan()
        except BaseException:
            self.failed=True;raise
    def _scan(self):
        pending=[(b'',1,0)]
        for path,start,depth in pending:
            require(depth<=self.MAX_DEPTH and len(pending)<=self.MAX_DIRS,'directory capacity')
            self.directory_count+=1;chain=self.claim(start);ended=False;names=set()
            for c in chain:
                block=self.fetch(self.address(c),self.cluster)
                for at in range(0,len(block),64):
                    e=block[at:at+64];length=e[0]
                    if length in (0,255):ended=True
                    if ended or length==229:continue
                    require(1<=length<=42,'name length');name=e[2:2+length]
                    require(not any(b<32 or b in b'\\/:*?"<>|' for b in name) and name not in (b'.',b'..'),'name syntax')
                    # FATX stores OEM bytes; use raw-byte ASCII folding for this
                    # ASCII-only image path. Non-ASCII entries still own clusters.
                    key=name.lower();require(key not in names,'duplicate name');names.add(key)
                    self.entry_count+=1;require(self.entry_count<=self.MAX_ENTRIES,'entry capacity')
                    first,size=struct.unpack_from('<II',e,44);full=path+b'/'+key
                    if e[1]&16:
                        require(first!=0,'directory cluster');pending.append((full,first,depth+1))
                    else:
                        clusters=self.claim(first) if first else ()
                        needed=(size+self.cluster-1)//self.cluster
                        require(len(clusters)==needed or (size==0 and len(clusters)==1),'file allocation length')
                        require(full not in self.files,'duplicate path')
                        self.files[full]=File(full,size,clusters,tuple(self.address(c) for c in clusters))
        for c in range(1,self.limit):require(bool(self.fat[c])==bool(self.owned[c]),'orphan/allocation mismatch')
        # Tail entries can contain formatter sentinels, but must not be addressable.
        require(self.fetch(self.start,4096)==self.header and self.fetch(self.start+4096,self.fat_size)==self.fat_raw,'metadata changed')
        self.scanned=True;return self
    def contiguous(self,path):
        require(self.scanned and not self.failed,'not scanned')
        require(type(path) is bytes and path.startswith(b'/') and len(path)<=1024,'path')
        require(all(1<=len(s)<=42 and all(32<=b<127 for b in s) and s not in (b'.',b'..') for s in path[1:].split(b'/')),'short ASCII path')
        f=self.files.get(path.lower());require(f is not None and f.size>65536 and f.size%512==0 and f.size<=0xfffffe00,'image size/missing')
        require(all(b==a+self.cluster for a,b in zip(f.starts,f.starts[1:])),'fragmented image')
        return f
