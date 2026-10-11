"""Preserve full allocated target clusters through independent cold readers."""
import hashlib,importlib,json,struct,sys
from pathlib import Path
sys.dont_write_bytecode=True
k=Path(__file__).resolve().parent;repo=k.parents[1];case=sys.argv[1]
assert case in ['emu001','emu002'];run=repo/('work/runs/nt5setup-'+case)
assert (run/'cleanup.json').exists()
stage=json.loads((run/'stage.json').read_text());parent=Path(stage['parent_path'])
canon=Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility')
sys.path[:0]=[str(canon/'outputs/native-windows-paint-save'),str(canon/'outputs/fatx-mapped-eof')]
from coldio import ColdIO
m=importlib.import_module('prepare-fixture');m.fatx.PARTITIONS['F']=(15633072*512,472764096*512)
sha=lambda b:hashlib.sha256(b).hexdigest()
out=k/case;art=out/'artifacts/cold-clusters';art.mkdir(parents=True,exist_ok=False)
targets=['xwnctl/status2.log','xwnctl/payload2.txt','xwnctl/exit2.txt']+['winnt/system32/config/'+n for n in ['system','software','default','sam','security']]
result=dict(physical_access=False,targets={},clusters={},missing_targets=[])
with ColdIO(run/'hdd.qcow2') as io,ColdIO(parent) as oldio:
    w=m.Writer(io,m.fatx.open_partition(io,run/'hdd.qcow2','F'))
    old=m.Writer(oldio,m.fatx.open_partition(oldio,parent,'F'))
    direct=m.SliceIO(run/'hdd.qcow2');ind=m.Writer(direct,m.fatx.open_partition(direct,run/'hdd.qcow2','F'))
    for path in targets:
        try:w.read(path)
        except KeyError:result['missing_targets'].append(path);continue
        at=1;parts=w.parts(path)
        for part in parts[:-1]:at=struct.unpack_from('<I',w.directory(at)['entries'][part.lower()][2],44)[0]
        _,_,e=w.directory(at)['entries'][parts[-1].lower()]
        first,size=struct.unpack_from('<II',e,44);chain=list(w.chain(first));data=w.read(path)
        assert data==ind.read(path)
        rows=[]
        for i,cluster in enumerate(chain):
            offset=w.p.cluster_offset(cluster);key=str(offset)
            if key not in result['clusters']:
                before=old.read_cluster(cluster);after=w.read_cluster(cluster)
                assert after==ind.read_cluster(cluster)
                for label,b in [('before',before),('after',after)]:(art/(key+'-'+label+'.bin')).write_bytes(b)
                result['clusters'][key]=dict(cluster=cluster,bytes=len(after),before_sha256=sha(before),after_sha256=sha(after),independent_exact=True)
            rows.append(dict(offset=offset,logical_offset=i*w.p.cluster_size,bytes=max(0,min(w.p.cluster_size,size-i*w.p.cluster_size))))
        result['targets'][path]=dict(bytes=size,sha256=sha(data),ranges=rows)
(out/'cold-ranges.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(dict(targets=len(result['targets']),clusters=len(result['clusters']),independent_exact=True)))
