"""Preserve the qualified first boot as a compact checkpoint for a second emulator boot."""
import hashlib,json,pathlib,shutil,subprocess
ws=pathlib.Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility')
k=ws/'outputs/native-windows-fatx-forensics';run='nt5-physical-f-high-allocation-r9'
assert (ws/'work/runs'/run/'cleanup.json').exists()
assert json.loads((k/(run+'-qualification.json')).read_text())['passed']
source=ws/'work/runs'/run/'hdd.qcow2';target=k/'artifacts/rotate-checkpoint-001.qcow2'
parent=k/'artifacts/rotate-unlinked-001.qcow2';seed=ws/'work/rotate-reboot-seed.qcow2'
assert not target.exists() and not seed.exists()
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
before=sha(source);parent_hash=sha(parent)
assert parent_hash==json.loads((k/'rotate-unlinked-fixture.json').read_text())['fixture_sha256']
info=json.loads(subprocess.check_output(['qemu-img','info','--output=json',str(source)]))
assert pathlib.Path(info['full-backing-filename']).resolve()==parent.resolve()
shutil.copyfile(source,target);assert sha(target)==before
# Same parent bytes, only a shorter relative backing name to avoid Windows MAX_PATH.
subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b',parent.name,str(target)],check=True)
assert sha(source)==before and sha(parent)==parent_hash
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(target),str(seed)],check=True)
subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b','../../../outputs/native-windows-fatx-forensics/artifacts/'+target.name,str(seed)],check=True)
r=dict(scope=__doc__,source_run=run,source_sha256=before,checkpoint_sha256=sha(target),
       unchanged_parent_sha256=parent_hash,guest_data_modified=False)
(k/'rotate-reboot-fixture.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
