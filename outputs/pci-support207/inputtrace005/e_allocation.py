"""Read-only E: allocation ownership audit for closed owned QCOW2 fixtures."""
import hashlib,json,struct

def audit_tree(fat,limit,cluster_size,entry_size,read_cluster):
    end=(1<<(8*entry_size))-1;threshold=end-7;bad=end-8
    owners={};directory_hash=hashlib.sha256();files=directories=0
    pending=[('/',1,0,True)];names_seen=set()
    while pending:
        path,first,size,isdir=pending.pop()
        assert path not in names_seen,('duplicate path',path);names_seen.add(path)
        if isdir:directories+=1
        else:files+=1
        if not first:
            assert not size,('size without chain',path)
            continue
        chain=[];current=first
        while True:
            assert 0<current<limit,('out of range',path,current)
            assert current not in owners,('shared or cyclic cluster',path,current)
            owners[current]=path;chain.append(current);nxt=fat[current]
            if nxt>=threshold:break
            assert nxt and nxt!=bad,('invalid terminal',path,nxt)
            current=nxt
        assert len(chain)*cluster_size>=size,('short file chain',path,size)
        if not isdir:continue
        ended=False;names=set()
        for cluster in chain:
            data=read_cluster(cluster);assert len(data)==cluster_size
            directory_hash.update(struct.pack('<I',cluster));directory_hash.update(data)
            for at in range(0,cluster_size,64):
                row=data[at:at+64];n=row[0]
                if n in (0,255):ended=True
                if ended or n==229:continue
                assert 1<=n<=42,('name length',path,n)
                raw=row[2:2+n];assert not any(c in raw for c in (0,47,92)),('name bytes',path)
                name=raw.decode('cp1252').lower();assert name not in names,('duplicate name',path,name);names.add(name)
                child,length=struct.unpack_from('<II',row,44)
                pending.append((path.rstrip('/')+'/'+name,child,length,bool(row[1]&16)))
    allocated={i for i in range(1,limit) if fat[i] and fat[i]!=bad}
    assert allocated==set(owners),('orphan clusters',sorted(allocated-set(owners))[:32])
    return dict(allocation_consistent=True,directories=directories,files=files,owned_clusters=len(owners),bad_clusters=sum(fat[i]==bad for i in range(1,limit)),orphan_clusters=0,directory_sha256=directory_hash.hexdigest())

def scan_e(disk,dest):
    from common import ColdIO,m
    assert not dest.exists()
    with ColdIO(disk) as io:
        p=m.fatx.open_partition(io,disk,'E');w=m.Writer(io,p)
        result=audit_tree(w.fat,w.limit,p.cluster_size,p.entry_size,w.read_cluster)
        io.seek(p.partition_offset);meta=io.read(p.cluster1_offset-p.partition_offset)
        result.update(scope=__doc__,physical_access=False,read_only=True,partition_offset=p.partition_offset,partition_size=p.partition_size,cluster_size=p.cluster_size,entry_size=p.entry_size,cluster_limit=w.limit,metadata_sha256=hashlib.sha256(meta).hexdigest())
    dest.write_text(json.dumps(result,indent=2)+'\n');return result
