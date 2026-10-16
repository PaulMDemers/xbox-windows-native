import ast,json,struct,sys,hashlib
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('/mnt/e/xwn414/cold001')
sys.path.insert(0,str(W/'outputs/video-text-oracle206'));from common import ColdIO,m,sha
sys.path.insert(0,str(W/'outputs/install-validation406'));from oem_reader import OemReader
m.fatx.PARTITIONS['E']=(5633024*512,10000048*512)
tree=ast.parse((W/'outputs/fresh-assembly405/normal-stage006.py').read_text());fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='inventory');exec(compile(ast.Module(body=[fn],type_ignores=[]),'owned-inventory','exec'))
paths=[Path('/mnt/e/xwn412/preparation002/fresh.qcow2'),Path('/mnt/e/xwn414/runs/nt5-cromwell414-emu001/hdd.qcow2')]
files=[];matches=[]
for phase,path in zip(['before','after'],paths):
    with ColdIO(path) as io:
        rd=OemReader(io,m.fatx.open_partition(io,path,'E'));items=inventory(rd);files.append(items)
        for cluster,d in rd.dirs.items():
            for name,(dc,offset,entry) in d['entries'].items():
                absolute=rd.p.cluster_offset(dc)+offset
                if absolute<=3628544184<absolute+64:
                    matches.append(dict(phase=phase,name=name,absolute_entry=absolute,entry_relative_changes=[p-absolute for p in [3628544184,3628544185,3628544186]],entry_hex=entry.hex()))
    (P/(phase+'-E-files.json')).write_text(json.dumps(items,indent=2)+'\n')
changed=[p for p in files[0].keys()|files[1].keys() if files[0].get(p)!=files[1].get(p)]
r=dict(E_file_contents_and_names_exact=files[0]==files[1],file_counts=[len(f) for f in files],changed_files=changed,changed_directory_entries=matches,strict_whole_disk_gate_still_false=True,writer_not_attributed=True,private_manifest_sha256={str(P/(phase+'-E-files.json')):sha(P/(phase+'-E-files.json')) for phase in ['before','after']})
with (P/'namespace-review.json').open('x') as f:json.dump(r,f,indent=2);f.write('\n')
summary=dict(E_file_contents_and_names_exact=r['E_file_contents_and_names_exact'],file_counts=r['file_counts'],changed_file_count=len(changed),strict_whole_disk_gate_still_false=True,writer_not_attributed=True,private_raw_sha256=sha(P/'namespace-review.json'),private_manifest_sha256=r['private_manifest_sha256'])
with (K/'emu001/namespace-summary.json').open('x') as f:json.dump(summary,f,indent=2);f.write('\n')
print(json.dumps(summary))
