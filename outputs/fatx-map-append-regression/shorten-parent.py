import hashlib,json,shutil,subprocess
from pathlib import Path
ws=Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility');k=ws/'outputs/fatx-map-append-regression'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=json.loads((k/'mode0/preflight.json').read_text())
snap=k/'mode0/source';snap.mkdir(exist_ok=False)
for name,digest in old['sources'].items():
    assert sha(k/name)==digest;shutil.copyfile(k/name,snap/name)
run=ws/'work/runs/nt5-fatx-map-append-mode0'
for name in ['cleanup.json','instance.json','input-hashes.json','xemu-stderr.log','xemu-stdout.log']:shutil.copyfile(run/name,k/'mode0'/name)
(k/'mode0/host-failure.json').write_text(json.dumps(dict(guest_launched=False,windows_launch_requested=False,emulator_start_failed=True,reason='Windows xemu cannot resolve the expanded relative backing path; stderr preserved.',cleanup_complete=(run/'cleanup.json').exists(),never_relaunch_this_attempt=True),indent=2)+'\n')
source=ws/'work/runs/nt5-fatx-mapped-lifecycle-002/hdd.qcow2';target=ws/'outputs/native-windows-fatx-forensics/artifacts/map-append-parent.qcow2'
assert not target.exists();original=sha(source);shutil.copyfile(source,target)
subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b','fatx-install-draw-001.qcow2',str(target)],check=True)
result=subprocess.run(['qemu-img','compare','-f','qcow2','-F','qcow2',str(source),str(target)],capture_output=True,text=True)
assert result.returncode==0 and sha(source)==original,(result.returncode,result.stdout,result.stderr)
(k/'parent-copy.json').write_text(json.dumps(dict(source=str(source),source_sha256=original,copy=str(target),copy_sha256=sha(target),virtual_contents_identical=True,compare_stdout=result.stdout,compare_stderr=result.stderr,compare_returncode=result.returncode),indent=2)+'\n')
print('Short parent verified identical; original preserved')
