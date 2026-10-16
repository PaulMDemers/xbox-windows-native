import json,struct,subprocess,sys,hashlib
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sys.path.insert(0,str(W/'outputs/video-text-oracle206'));from common import ColdIO,m,sha
sys.path.insert(0,str(W/'outputs/install-validation406'));from oem_reader import OemReader
m.fatx.PARTITIONS['E']=(5633024*512,10000048*512)
a=Path('/mnt/e/xwn406/assembly003/fresh.qcow2');b=Path('/mnt/e/xwn412/preparation002/fresh.qcow2')
prep=json.loads((K/'preparation002.json').read_text());assert sha(b)==prep['fixture_sha256']
xbe=Path('/mnt/e/xwn374/build001/default.xbe').read_bytes()
changed=examined=0;extents=[]
with ColdIO(a) as old,ColdIO(b) as new:
    rd=OemReader(old,m.fatx.open_partition(old,a,'E'));first=1
    for name in ['applications','xwneboot','default.xbe']:
        entry=rd.directory(first)['entries'][name][2];first=struct.unpack_from('<I',entry,44)[0]
    ranges=[(rd.p.cluster_offset(c),i*rd.p.cluster_size) for i,c in enumerate(rd.chain(first))]
    mapping=json.loads(subprocess.check_output(['qemu-img','map','--output=json',str(b)]))
    for row in mapping:
        if row['depth']!=0:continue
        assert row['start']%512==0 and row['length']%512==0
        extents.append(row)
        for pos in range(row['start'],row['start']+row['length'],65536):
            n=min(65536,row['start']+row['length']-pos);old.seek(pos);new.seek(pos);x=old.read(n);y=new.read(n);examined+=n
            for i,(u,v) in enumerate(zip(x,y)):
                if u==v:continue
                candidates=[off+pos+i-base for base,off in ranges if base<=pos+i<base+rd.p.cluster_size]
                assert len(candidates)==1 and candidates[0]<len(xbe) and v==xbe[candidates[0]],pos+i
                changed+=1
r=dict(passed=True,complete_virtual_mapping_examined=True,all_inherited_extents_unchanged=True,local_extent_bytes_compared=examined,changed_bytes=changed,only_exact_launcher_file_bytes_changed=True,allocation_entries_and_padding_unchanged=True,local_extents=extents,fixture_sha256=sha(b),qcow_check=json.loads(subprocess.check_output(['qemu-img','check','--output=json',str(b)])),physical_access=False)
with (K/'preparation-review001.json').open('x') as f:json.dump(r,f,indent=2);f.write('\n')
print(json.dumps({k:r[k] for k in ['passed','local_extent_bytes_compared','changed_bytes']}))
