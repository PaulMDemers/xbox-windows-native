"""Independently read cold control payloads and compare their preboot clusters."""
import hashlib,importlib,json,struct,sys
from pathlib import Path
sys.dont_write_bytecode=True
k=Path(__file__).resolve().parent;repo=k.parents[1];case=sys.argv[1];run=repo/('work/runs/nt5stortrace-'+case)
assert case in ['emu001','emu002'] and (run/'cleanup.json').exists()
stage=json.loads((run/'stage.json').read_text());parent=Path(stage['parent_path']);phase=stage['phase']
canon=Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility')
sys.path[:0]=[str(canon/'outputs/native-windows-paint-save'),str(canon/'outputs/fatx-mapped-eof')]
from coldio import ColdIO
m=importlib.import_module('prepare-fixture');m.fatx.PARTITIONS['F']=(15633072*512,472764096*512)
sha=lambda b:hashlib.sha256(b).hexdigest()
def entry(w,path):
    at=1;parts=w.parts(path)
    for part in parts[:-1]:at=struct.unpack_from('<I',w.directory(at)['entries'][part.lower()][2],44)[0]
    dc,off,e=w.directory(at)['entries'][parts[-1].lower()]
    return dict(directory_cluster=dc,directory_offset=off,first_cluster=struct.unpack_from('<I',e,44)[0],size=struct.unpack_from('<I',e,48)[0])
r=dict(case=case,phase=phase,physical_access=False,files={})
with ColdIO(run/'hdd.qcow2') as a,ColdIO(parent) as b:
    w=m.Writer(a,m.fatx.open_partition(a,run/'hdd.qcow2','F'));old=m.Writer(b,m.fatx.open_partition(b,parent,'F'))
    rio=m.SliceIO(run/'hdd.qcow2');ind=m.Writer(rio,m.fatx.open_partition(rio,run/'hdd.qcow2','F'))
    r['full_fat_transports_exact']=w.fat==ind.fat;assert r['full_fat_transports_exact']
    for n in ['status'+str(phase)+'.log','payload'+str(phase)+'.txt','exit'+str(phase)+'.txt']:
        path='xwnctl/'+n
        try:e=entry(w,path)
        except KeyError:r['files'][n]=dict(absent=True);continue
        assert e==entry(ind,path);chain=list(w.chain(e['first_cluster']));data=w.read(path);assert data==ind.read(path)==(run/n).read_bytes()
        prior=b''.join(old.read_cluster(c) for c in chain)[:len(data)]
        r['files'][n]=dict(entry=e,sha256=sha(data),length=len(data),transport_exact=True,
            chain=[dict(cluster=c,parent_fat=old.fat[c],after_fat=w.fat[c]) for c in chain],
            equals_parent_same_clusters=data==prior,parent_bytes_sha256=sha(prior),
            ascii_text=all(v in [9,10,13] or 32<=v<127 for v in data))
    p='winnt/system32/wbem/repository/CIM.REC';e=entry(w,p);assert e==entry(ind,p)
    e['fat_value']=w.fat[e['first_cluster']];e['parent_entry']=entry(old,p);e['parent_fat_value']=old.fat[e['first_cluster']];r['cim_rec']=e
with parent.open('rb') as f:r['parent_sha256']=hashlib.file_digest(f,'sha256').hexdigest()
r['parent_unchanged']=r['parent_sha256']==stage['parent_sha256'];assert r['parent_unchanged']
r['limits']='Cold read-only evidence. Matching stale bytes does not identify the writer or establish execution of lost status records.'
(k/case/'forensics.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
