"""Bounded offline FATX writer for disposable emulator fixtures.

Accepts the inspected FatxPartition geometry from the existing staging tool.
Handles chained directories and caches the FAT to avoid quadratic allocations.
No physical devices or formatting entry point is provided.
"""
import array,hashlib,struct,sys

class Writer:
    def __init__(self,fp,part):
        self.fp=fp;self.p=part;self.cursor=2;self.dirs={}
        assert part.entry_size in (2,4) and part.cluster_size>=512
        fp.seek(part.fat_offset);self.fat=array.array('I' if part.entry_size==4 else 'H')
        self.fat.frombytes(fp.read(part.fat_size))
        if sys.byteorder!='little':self.fat.byteswap()
        self.limit=min(part.cluster_count,(part.partition_offset+part.partition_size-part.cluster1_offset)//part.cluster_size+1)
        assert 2<self.limit<=len(self.fat)
        self.end=0xffffffff if part.entry_size==4 else 0xffff
        self.threshold=self.end-7
    def chain(self,start):
        seen=set();at=start
        while True:
            assert 1<=at<self.limit and at not in seen,('invalid/cyclic chain',at)
            seen.add(at);yield at
            nxt=self.fat[at]
            if nxt>=self.threshold:return
            assert nxt!=0,('free entry in chain',at)
            at=nxt
    def read_cluster(self,c):
        assert 1<=c<self.limit
        self.fp.seek(self.p.cluster_offset(c));b=self.fp.read(self.p.cluster_size)
        assert len(b)==self.p.cluster_size;return b
    def write_cluster(self,c,b):
        assert 1<=c<self.limit and len(b)<=self.p.cluster_size
        self.fp.seek(self.p.cluster_offset(c));self.fp.write(b.ljust(self.p.cluster_size,b'\0'))
    def allocate(self,count):
        found=[];at=self.cursor
        while at<self.limit and len(found)<count:
            if self.fat[at]==0:found.append(at)
            at+=1
        if len(found)!=count:raise RuntimeError('FATX fixture full')
        self.cursor=at
        for i,c in enumerate(found):self.fat[c]=found[i+1] if i+1<len(found) else self.end
        return found
    @staticmethod
    def parts(path):
        parts=path.replace('\\','/').strip('/').split('/')
        for s in parts:
            b=s.encode('ascii');assert 1<=len(b)<=42 and s not in ('.','..') and not any(x in s for x in ':*?"<>|'),path
        return parts
    def directory(self,start):
        if start in self.dirs:return self.dirs[start]
        entries={};slots=[];chain=list(self.chain(start));ended=False
        for c in chain:
            b=self.read_cluster(c)
            for off in range(0,len(b),64):
                marker=b[off]
                if marker in (0,255):ended=True
                if ended or marker==229:slots.append((c,off));continue
                assert 1<=marker<=42
                e=bytes(b[off:off+64]);name=e[2:2+marker].decode('ascii').lower()
                assert name not in entries;entries[name]=(c,off,e)
        result={'entries':entries,'slots':slots,'chain':chain};self.dirs[start]=result;return result
    def add(self,parent,name,flags,cluster,size):
        d=self.directory(parent);assert name.lower() not in d['entries'],('would overwrite',name)
        if not d['slots']:
            c=self.allocate(1)[0];self.write_cluster(c,b'\xff'*self.p.cluster_size);self.fat[d['chain'][-1]]=c;d['chain'].append(c)
            d['slots']=[(c,off) for off in range(0,self.p.cluster_size,64)]
        c,off=d['slots'].pop(0);entry=bytearray(64);encoded=name.encode('ascii')
        entry[0]=len(encoded);entry[1]=flags;entry[2:2+len(encoded)]=encoded
        struct.pack_into('<II',entry,44,cluster,size)
        for date in (54,58,62):struct.pack_into('<H',entry,date,0x2821) # 2000-01-01
        b=bytearray(self.read_cluster(c));b[off:off+64]=entry;self.write_cluster(c,b)
        d['entries'][name.lower()]=(c,off,bytes(entry))
    def mkdir(self,path):
        at=1
        for name in self.parts(path):
            e=self.directory(at)['entries'].get(name.lower())
            if e:
                assert e[2][1]&16;at=struct.unpack_from('<I',e[2],44)[0]
            else:
                c=self.allocate(1)[0];self.write_cluster(c,b'\xff'*self.p.cluster_size);self.add(at,name,16,c,0);at=c
        return at
    def read(self,path):
        at=1;parts=self.parts(path)
        for i,name in enumerate(parts):
            _,_,e=self.directory(at)['entries'][name.lower()];at=struct.unpack_from('<I',e,44)[0]
            if i<len(parts)-1:assert e[1]&16
        assert not e[1]&16;size=struct.unpack_from('<I',e,48)[0]
        if not size:return b''
        data=b''.join(self.read_cluster(c) for c in self.chain(at));assert len(data)>=size
        return data[:size]
    def write(self,path,data):
        parts=self.parts(path);parent=self.mkdir('/'.join(parts[:-1])) if len(parts)>1 else 1
        assert parts[-1].lower() not in self.directory(parent)['entries']
        assert len(data)<=0xffffffff
        chain=self.allocate(max(1,(len(data)+self.p.cluster_size-1)//self.p.cluster_size))
        for i,c in enumerate(chain):self.write_cluster(c,data[i*self.p.cluster_size:(i+1)*self.p.cluster_size])
        self.add(parent,parts[-1],32,chain[0],len(data))
        assert self.read(path)==data,path
        return {'path':path,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'clusters':len(chain)}
    def flush(self):
        b=self.fat[:]
        if sys.byteorder!='little':b.byteswap()
        self.fp.seek(self.p.fat_offset);self.fp.write(b.tobytes());self.fp.flush()
