import hashlib,importlib,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sys.path.insert(0,str(ws/'outputs/fatx-mapped-eof'))
from coldio import ColdIO
sys.path.insert(0,str(ws/'outputs/native-windows-paint-save'))
m=importlib.import_module('prepare-fixture')
m.fatx.PARTITIONS['F']=(15633072*512,472764096*512)
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads(p.read_text())
def save(p,r):
    assert not p.exists(),str(p)
    p.write_text(json.dumps(r,indent=2)+'\n')
def e_reader(io,disk):return m.Writer(io,m.fatx.open_partition(io,disk,'E'))

def inventory(w):
    """Read every reachable E: file and enforce unique, bounded chains."""
    import struct
    owners={};files={};dirs=[];todo=[('',1)];errors=[]
    def claim(first,owner):
        chain=[]
        for c in w.chain(first):
            assert c not in owners,(owner,owners.get(c),c)
            owners[c]=owner;chain.append(c)
        return chain
    for path,first in todo:
        chain=claim(first,'dir:'+path);dirs.append(path);ended=False
        for c in chain:
            data=w.read_cluster(c)
            for off in range(0,len(data),64):
                e=data[off:off+64];n=e[0]
                if n in [0,255]:ended=True
                if ended or n==229:continue
                assert 1<=n<=42
                name=e[2:2+n].decode('latin1');p=(path+'/'+name).strip('/')
                start,size=struct.unpack_from('<II',e,44)
                if e[1]&16:todo.append((p,start))
                else:
                    cells=claim(start,'file:'+p) if start else []
                    assert size<=len(cells)*w.p.cluster_size
                    b=w.read(p);assert len(b)==size
                    assert p.lower() not in files
                    files[p.lower()]=dict(bytes=size,sha256=m.sha(b),clusters=cells)
    # Do not reinterpret reserved FAT values as live allocation.
    live=[i for i in range(1,w.limit) if w.fat[i]!=0]
    orphans=[i for i in live if i not in owners]
    return dict(files=files,directories=dirs,owned_clusters=len(owners),orphan_clusters=orphans,
                allocation_consistent=not orphans,errors=errors)
