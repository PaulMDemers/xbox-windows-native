"""Copy CLOSED deltas and shorten NEW-copy backing paths, proving virtual equality."""
import shutil,subprocess
from common import *
dest=k/'parents.json';assert not dest.exists();records={}
root=ws/'outputs/native-windows-fatx-forensics/artifacts'
for case,prior,prior_case,run_id in [('pending001','device-observation188','emulator001','nt5-observe188-emulator001'),('idle001','video-word-order186','candidate001','nt5-word186-candidate001')]:
    closure=k.parent/prior/prior_case/'closure.json';assert read(closure)['closed']
    source=ws/'work/runs'/run_id/'hdd.qcow2';assert (source.parent/'cleanup.json').exists()
    chain=json.loads(subprocess.check_output(['qemu-img','info','--backing-chain','--output=json',str(source)]))
    parents=[dict(path=str(Path(row['filename']).resolve()),sha256=sha(Path(row['filename']))) for row in chain]
    backing=Path(chain[1]['filename']).resolve();assert backing.parent==root.resolve()
    copy=root/('video-setup-runtime191-parent-'+case+'.qcow2');assert not copy.exists()
    shutil.copyfile(source,copy);assert sha(copy)==parents[0]['sha256']
    subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b',backing.name,str(copy)],check=True)
    comparison=subprocess.run(['qemu-img','compare','-f','qcow2','-F','qcow2',str(source),str(copy)],capture_output=True,text=True)
    assert comparison.returncode==0,comparison.stdout+comparison.stderr
    for row in parents:assert sha(Path(row['path']))==row['sha256']
    records[case]=dict(original_path=str(source),original_sha256=parents[0]['sha256'],copied_path=str(copy),copied_sha256=sha(copy),original_chain=parents,stored_backing=backing.name,virtual_disk_equal=True,compare_reply=comparison.stdout,metadata_only_rebase=True,closure_sha256=sha(closure),physical_access=False)
save(dest,records);print('191 NEW parent copies virtual-equal; original CLOSED chains byte-exact')
