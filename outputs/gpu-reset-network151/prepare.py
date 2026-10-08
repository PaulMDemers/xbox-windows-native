"""One fresh native-Xbox E: app child; Windows and physical console are untouched."""
import subprocess
from common import *
case=sys.argv[1];assert case in ['control001','candidate001']
out=k/case;assert not out.exists();out.mkdir()
f=read(ws/'outputs/video-line-gdi/fixture-candidate001.json')
source=ws/'outputs/native-windows-fatx-forensics/artifacts'/f['fixture_name']
assert sha(source)==f['fixture_sha256']
target=source.parent/('gpu-reset-network151-'+case+'.qcow2')
seed=ws/('work/gpu-reset-network151-'+case+'-seed.qcow2')
assert not target.exists() and not seed.exists()
build=read(ws/'outputs/xemu-cpu-surface-evict/build003/build.json');assert build['passed']
probe=ws/'outputs/gpu-reset150/artifacts/default.xbe'
assert sha(probe)=='35ba328cebbf9e9e24b89bae79a1e5dbd60762b38302032199c6bdfcde4569a1'

chain=json.loads(subprocess.check_output(['qemu-img','info','--backing-chain','--output=json',str(source)]))
parents=[dict(path=str(Path(v['filename']).resolve()),sha256=sha(Path(v['filename']))) for v in chain]
with ColdIO(source) as io:
    before=inventory(e_reader(io,source))
assert before['allocation_consistent']
assert not any(p.startswith(('xwngpu150/','applications/xwngpu150/','xwngpu149/','applications/xwngpu149/')) for p in before['files'])
assert not any(p.lower() in ['xwngpu150','applications/xwngpu150'] for p in before['directories'])
save(out/'before-e.json',before)
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(source),str(target)],check=True)
m.target=target;w=e_reader(m.SliceIO(target),target)
payload=w.write('Applications/XWNGpu150/default.xbe',probe.read_bytes());w.write('Applications/XWNGpu149/default.xbe',(ws/'outputs/gpu-overlap149/artifacts/default.xbe').read_bytes());w.flush()
with ColdIO(target) as io:
    staged=inventory(e_reader(io,target))
assert staged['allocation_consistent']
assert staged['files']['applications/xwngpu150/default.xbe']['sha256']==sha(probe)
assert staged['files']['applications/xwngpu149/default.xbe']['sha256']==sha(ws/'outputs/gpu-overlap149/artifacts/default.xbe')
assert all(staged['files'][p]==r for p,r in before['files'].items())
save(out/'staged-e.json',staged)
subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b',source.name,str(target)],check=True)
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(target),str(seed)],check=True)
subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b','../../../outputs/native-windows-fatx-forensics/artifacts/'+target.name,str(seed)],check=True)
for row in parents:assert sha(Path(row['path']))==row['sha256']
save(k/('fixture-'+case+'.json'),dict(fixture_name=target.name,fixture_sha256=sha(target),seed_sha256=sha(seed),
    parents=parents,payload=payload,build_sha256=sha(ws/'outputs/xemu-cpu-surface-evict/build003/build.json'),physical_access=False,windows_launched=False,
    inherited_windows_configuration=f['inherited_configuration'],staged_e_sha256=sha(out/'staged-e.json')))
print('Unique native GPU app staged and readback verified; not launched')
