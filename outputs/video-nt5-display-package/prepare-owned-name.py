"""Use a project-owned display DLL filename, without changing the binary or signing policy."""
import importlib,json,shutil,subprocess,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sys.path.insert(0,str(ws/'outputs/native-windows-paint-save'));m=importlib.import_module('prepare-fixture')
parent=ws/'outputs/native-windows-fatx-forensics/artifacts/video-nt5-display-package-002.qcow2'
r=json.loads((k/'fixture-002.json').read_text());parent_hash=r['fixture_sha256'];assert m.filehash(parent)==parent_hash
target=parent.with_name('video-nt5-display-package-003.qcow2');seed=ws/'work/video-nt5-display-package-003-seed.qcow2'
assert not target.exists() and not seed.exists() and shutil.disk_usage('/mnt/c').free>8*1024**3
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(parent),str(target)],check=True)
m.target=target;m.fatx.PARTITIONS['F']=(15633072*512,472764096*512)
io=m.SliceIO(target);w=m.Writer(io,m.fatx.open_partition(io,target,'F'))
system=w.read('winnt/system32/config/system');software=w.read('winnt/system32/config/software')
inf=(k/'xwnvideo.inf').read_bytes();binary=w.read('winnt/system32/framebuf.dll')
assert m.sha(binary)=='3d4c5c2659c06f9ae4c9a735a99ad972d4e773e02a0f1b7d4d8c2d18053e9db7'
m.replace(w,'xwninf01/xboxvnt5.inf',inf)
r['payloads'].append(w.write('xwninf01/xwnfb.dll',binary));w.flush()
fresh=m.Writer(io,m.fatx.open_partition(io,target,'F'))
for row in r['payloads']:
    if row['path']=='xwninf01/xboxvnt5.inf':row.update(sha256=m.sha(inf),bytes=len(inf))
    assert m.sha(fresh.read(row['path']))==row['sha256']
assert fresh.read('winnt/system32/config/system')==system and fresh.read('winnt/system32/config/software')==software
assert m.filehash(parent)==parent_hash
subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b',parent.name,str(target)],check=True)
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(target),str(seed)],check=True)
subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b','../../../outputs/native-windows-fatx-forensics/artifacts/'+target.name,str(seed)],check=True)
r.update(scope=__doc__,parent_fixture_sha256=parent_hash,fixture_sha256=m.filehash(target),seed_sha256=m.filehash(seed),
         display_package_name='xwnfb.dll',display_binary_unchanged=True,registry_hives_unchanged_during_staging=True,
         installation_method='Preloaded DevicePath, project-owned display filename; original signing policy unchanged')
(k/'fixture-003.json').write_text(json.dumps(r,indent=2)+'\n');print('Project-owned display filename fixture verified')
