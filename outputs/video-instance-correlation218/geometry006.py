"""Derive observed byte displacement; no stock mount formula is assumed."""
import sys,json,struct
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sys.path.insert(0,str(ws/'outputs/video-gpu-handoff216'))
from common import ColdIO,m,sha,read
parent=Path('/mnt/e/Codex-archive/xbox-windows-native/gstate216/control001-source.qcow2')
assert sha(parent)==read(ws/'outputs/video-instance-backing217/inputs.json')['parent_sha256']
dest=k/'geometry006.json';assert not dest.exists()
with ColdIO(parent) as io:
 p=m.fatx.open_partition(io,parent,'F');w=m.Writer(io,p);at=1
 for name in ['winnt','system32','config','software']:
  _,_,e=w.directory(at)['entries'][name];at=struct.unpack_from('<I',e,44)[0]
 chain=list(w.chain(at));logical=read(k/'forensic-recovery006.json')['root_entry_offset']
 cluster=chain[logical//p.cluster_size];within=logical%p.cluster_size
 observed=p.cluster_offset(cluster)+within
 native_first=observed-(2679-1)*p.cluster_size
 r=dict(read_only=True,physical_access=False,software_first_cluster=at,
        software_chain_index=logical//p.cluster_size,software_cluster=cluster,within_cluster=within,
        observed_directory_2679_offset=observed,nt5_oracle_directory_2679_offset=p.cluster_offset(2679),
        observed_displacement=observed-p.cluster_offset(2679),inferred_native_cluster1_offset=native_first,
        nt5_cluster1_offset=p.cluster1_offset,stock_geometry_formula_proven=False,parent_unchanged=sha(parent)==read(ws/'outputs/video-instance-backing217/inputs.json')['parent_sha256'])
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
