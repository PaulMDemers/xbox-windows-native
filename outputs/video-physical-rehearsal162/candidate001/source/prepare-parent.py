"""Private checkpoint path normalization with full virtual disk comparison."""
import subprocess,shutil
from common import *
original=ws/'work/runs/nt5-physical-f-high-allocation-r15/hdd.qcow2'
target=ws/'outputs/native-windows-fatx-forensics/artifacts/video-physical-rehearsal162-parent.qcow2'
dest=k/'parent-review.json';assert not dest.exists() and not target.exists()
assert (original.parent/'cleanup.json').exists()
chain=json.loads(subprocess.check_output(['qemu-img','info','--backing-chain','--output=json',str(original)]))
parents=[dict(path=str(Path(v['filename']).resolve()),sha256=sha(Path(v['filename']))) for v in chain]
assert Path(chain[1]['filename']).resolve()==target.parent/'lifetime-long-001.qcow2'
shutil.copyfile(original,target)
subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b','lifetime-long-001.qcow2',str(target)],check=True)
result=subprocess.run(['qemu-img','compare','-f','qcow2','-F','qcow2',str(original),str(target)],check=True,capture_output=True,text=True)
for row in parents:assert sha(Path(row['path']))==row['sha256']
save(dest,dict(virtual_contents_equal=True,comparison=result.stdout.strip(),original_sha256=parents[0]['sha256'],
    checkpoint_sha256=sha(target),parents=parents,physical_access=False,guest_launch=False,
    scope='Owned private leaf copy with shorter relative backing path; original chain unchanged. Full qemu virtual-content comparison, not physical reconstruction.'))
print('Short-path owned checkpoint virtual contents identical')
