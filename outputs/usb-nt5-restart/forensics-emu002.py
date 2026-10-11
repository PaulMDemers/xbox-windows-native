"""Read-only cross-transport inspection of the closed subsequent-boot failure."""
import hashlib,importlib,json,struct,sys
from pathlib import Path
sys.dont_write_bytecode=True
k=Path(__file__).resolve().parent;repo=k.parents[1];run=repo/'work/runs/nt5xidrestart-emu002';parent=repo/'work/runs/nt5xidrestart-emu001'
assert (run/'cleanup.json').exists() and (parent/'cleanup.json').exists()
canon=Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility')
sys.path[:0]=[str(canon/'outputs/native-windows-paint-save'),str(canon/'outputs/fatx-mapped-eof')]
from coldio import ColdIO
m=importlib.import_module('prepare-fixture');m.fatx.PARTITIONS['F']=(15633072*512,472764096*512)
sha=lambda b:hashlib.sha256(b).hexdigest()
def entry(w,path):
    at=1;parts=w.parts(path)
    for part in parts[:-1]:at=struct.unpack_from('<I',w.directory(at)['entries'][part.lower()][2],44)[0]
    dc,offset,e=w.directory(at)['entries'][parts[-1].lower()]
    return dict(directory_cluster=dc,directory_offset=offset,first_cluster=struct.unpack_from('<I',e,44)[0],size=struct.unpack_from('<I',e,48)[0])
r=dict(physical_access=False,read_only=True,files={},parent_case='emu001')
with ColdIO(run/'hdd.qcow2') as a,ColdIO(parent/'hdd.qcow2') as b:
    w=m.Writer(a,m.fatx.open_partition(a,run/'hdd.qcow2','F'));old=m.Writer(b,m.fatx.open_partition(b,parent/'hdd.qcow2','F'))
    rangeio=m.SliceIO(run/'hdd.qcow2');independent=m.Writer(rangeio,m.fatx.open_partition(rangeio,run/'hdd.qcow2','F'))
    r['full_fat_transports_exact']=w.fat==independent.fat;assert r['full_fat_transports_exact']
    for name in ['verify.log','exit-verify.txt']:
        path='xwnxid/'+name;e=entry(w,path);assert e==entry(independent,path);chain=list(w.chain(e['first_cluster']));data=w.read(path)
        assert data==independent.read(path)==(run/name).read_bytes()
        prior=b''.join(old.read_cluster(c) for c in chain)[:len(data)]
        rows=[dict(cluster=c,parent_fat=old.fat[c],after_fat=w.fat[c]) for c in chain]
        hits={}
        for hive in ['system','software','default','sam','security']:
            content=(run/('before-'+hive)).read_bytes();at=content.find(data)
            if at>=0:hits[hive]=at
        r['files'][name]=dict(entry=e,chain=rows,length=len(data),sha256=sha(data),independent_transport_exact=True,
            equals_parent_same_clusters=data==prior,parent_bytes_sha256=sha(prior),complete_preboot_hive_matches=hits,
            ascii_text=all(v in [9,10,13] or 32<=v<127 for v in data))
    e=entry(w,'winnt/system32/wbem/repository/CIM.REC');assert e==entry(independent,'winnt/system32/wbem/repository/CIM.REC');e['fat_value']=w.fat[e['first_cluster']]
    e['parent_entry']=entry(old,'winnt/system32/wbem/repository/CIM.REC');e['parent_fat_value']=old.fat[e['first_cluster']]
    r['cim_rec']=e
    r['orphan_cluster']=dict(cluster=2144563,parent_fat=old.fat[2144563],after_fat=w.fat[2144563])
with (parent/'hdd.qcow2').open('rb') as f:r['parent_disk_sha256']=hashlib.file_digest(f,'sha256').hexdigest()
expected=json.loads((run/'stage.json').read_text())['parent_closed_disk_sha256'];r['parent_unchanged']=r['parent_disk_sha256']==expected;assert r['parent_unchanged']
r['limits']='Confirms cold bytes/metadata through independent qemu transports and retained parent. Does not identify the guest writer or infer HID success from corrupted logs.'
(k/'emu002/forensics.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
