"""Readback-equal portable copy of181 normally shut down image, no reset."""
import shutil,subprocess
from common import *
dest=k/'parent-copy.json';assert not dest.exists()
old=k.parent/'device-settled-reboot181';assert read(old/'candidate001/closure.json')['closed']
assert read(old/'candidate001/package-verification.json')['configuration_observed']
source=ws/'work/runs/nt5-settled181-candidate001/hdd.qcow2';original=sha(source)
chain=json.loads(subprocess.check_output(['qemu-img','info','--backing-chain','--output=json',str(source)]))
parents=[dict(path=str(Path(v['filename']).resolve()),sha256=sha(Path(v['filename']))) for v in chain]
parent=ws/'outputs/native-windows-fatx-forensics/artifacts/video-dib183-parent181.qcow2';assert not parent.exists()
backing=Path(chain[1]['filename']).resolve();assert backing.parent==parent.parent
assert all(not v.get('backing-filename','').startswith('/') for v in chain)
shutil.copyfile(source,parent)
subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b',backing.name,str(parent)],check=True)
subprocess.run(['qemu-img','compare',str(source),str(parent)],check=True)
portable=json.loads(subprocess.check_output(['qemu-img','info','--backing-chain','--output=json',str(parent)]))
assert all(not v.get('backing-filename','').startswith('/') for v in portable)
for row in parents:assert sha(Path(row['path']))==row['sha256']
save(dest,dict(original_path=str(source),original_sha256=original,copied_path=str(parent),copied_sha256=sha(parent),virtual_disk_equal=True,metadata_only_rebase=True,stored_backings=[v.get('backing-filename') for v in portable],parents=parents,physical_access=False,no_diagnostic_file_reset=True))
print('181 closed image preserved; portable copy equal, no hives/log resets')
