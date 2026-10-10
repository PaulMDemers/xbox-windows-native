"""Read-only byte/geometry evidence from CLOSED failed native006. No repair."""
import sys,json,struct,hashlib,dataclasses
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sys.path.insert(0,str(ws/'outputs/video-gpu-handoff216'))
from common import ColdIO,m,sha,read
parent=Path('/mnt/e/Codex-archive/xbox-windows-native/gstate216/control001-source.qcow2')
run=Path('/mnt/e/Codex-private-artifacts/xbox-windows-feasibility/instance218-runs/stock-instance218-native006')
disk=run/'hdd.qcow2';assert (run/'cleanup.json').exists()
assert sha(parent)==read(ws/'outputs/video-instance-backing217/inputs.json')['parent_sha256']
dest=k/'forensics006.json';assert not dest.exists()
r=dict(read_only=True,physical_access=False,cause_proven=False,full_payload_integrity_proven=False)
def observe(path):
    with ColdIO(path) as io:
        part=m.fatx.open_partition(io,path,'F');w=m.Writer(io,part)
        io.seek(part.partition_offset);region=io.read(20*1024*1024)
        out=dict(geometry={n:getattr(part,n) for n in ['partition_offset','partition_size','cluster_size','cluster_count','fat_offset','fat_size','cluster1_offset']},
                 root_entries=list(w.directory(1)['entries']),fat_head=list(w.fat[:8]))
        software=w.read('winnt/system32/config/software');out['software_sha256']=m.sha(software)
        out['software_probe_name_offsets']=[];start=0
        while True:
            at=software.find(b'xwninst218c',start)
            if at<0:break
            out['software_probe_name_offsets'].append(at);start=at+1
        out['low_region_probe_name_offsets']=[];start=0
        while True:
            at=region.find(b'xwninst218c',start)
            if at<0:break
            out['low_region_probe_name_offsets'].append(part.partition_offset+at);start=at+1
        return out,region,software,w.fat
before,breg,bs,bfat=observe(parent);after,areg,asw,afat=observe(disk)
r['before']=before;r['after']=after
r['changed_fat_entries']=[dict(cluster=i,before=a,after=b) for i,(a,b) in enumerate(zip(bfat,afat)) if a!=b]
r['software_changed_4k_pages']=[i for i in range(0,len(bs),4096) if bs[i:i+4096]!=asw[i:i+4096]]
r['low_region_changed_4k_pages']=[i for i in range(0,len(breg),4096) if breg[i:i+4096]!=areg[i:i+4096]]
r['parent_unchanged']=sha(parent)==read(ws/'outputs/video-instance-backing217/inputs.json')['parent_sha256']
r['disk_sha256']=sha(disk)
dest.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r,indent=2))
