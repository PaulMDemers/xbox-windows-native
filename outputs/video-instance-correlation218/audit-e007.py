"""Complete read-only E allocation and original file readback for closed007."""
import sys,json,struct
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sys.path.insert(0,str(ws/'outputs/video-gpu-handoff216'))
from common import ColdIO,m,sha,read
parent=Path('/mnt/e/Codex-archive/xbox-windows-native/gstate216/control001-source.qcow2')
run=Path('/mnt/e/Codex-private-artifacts/xbox-windows-feasibility/instance218-runs/stock-instance218-epath007')
disk=run/'hdd.qcow2';assert (run/'cleanup.json').exists()
assert sha(parent)==read(ws/'outputs/video-instance-backing217/inputs.json')['parent_sha256']
dest=k/'e-audit007.json';assert not dest.exists()
def observe(path):
    with ColdIO(path) as io:
        p=m.fatx.open_partition(io,path,'E');w=m.Writer(io,p)
        owners={};files={};dirs=[];todo=[(1,'')];errors=[]
        for first,name in todo:
            dirs.append(name)
            if first==0:continue
            for c in w.chain(first):
                if c in owners:raise AssertionError(('shared-directory',c,name))
                owners[c]=name+'/'
            for unused,unused2,e in w.directory(first)['entries'].values():
                n=e[2:2+e[0]].decode('ascii').lower();full=(name+'/'+n).lstrip('/')
                c,size=struct.unpack_from('<II',e,44)
                if e[1]&16:todo.append((c,full));continue
                chain=list(w.chain(c)) if c else []
                assert len(chain)*p.cluster_size>=size,(full,'short chain')
                for cluster in chain:
                    if cluster in owners:raise AssertionError(('crosslink',cluster,full,owners[cluster]))
                    owners[cluster]=full
                files[full]=dict(bytes=size,sha256=m.sha(w.read(full)))
        orphans=[c for c in range(1,w.limit) if w.fat[c] not in (0,w.end-8) and c not in owners]
        return dict(files=files,directories=dirs,orphan_clusters=orphans,allocation_passed=not orphans,
                    cluster_size=p.cluster_size,cluster_count=w.limit-1,owned_clusters=len(owners),bytes_read=io.read_bytes)
before=observe(parent);after=observe(disk)
expected={'xwninst218d/'+n for n in ['report.txt','cpu0.bin','gpu0.bin','cpu1.bin','gpu1.bin']}
same=all(after['files'].get(n)==v for n,v in before['files'].items())
r=dict(read_only=True,physical_access=False,debugger=False,before=before,after=after,
       original_files_unchanged=same,new_files=sorted(set(after['files'])-set(before['files'])),
       exact_new_files=set(after['files'])-set(before['files'])==expected,
       parent_unchanged=sha(parent)==read(ws/'outputs/video-instance-backing217/inputs.json')['parent_sha256'],disk_sha256=sha(disk))
r['passed']=same and r['exact_new_files'] and before['allocation_passed'] and after['allocation_passed'] and r['parent_unchanged']
dest.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({n:r[n] for n in ['passed','original_files_unchanged','exact_new_files','new_files']},indent=2))
