"""Clone the cold successful installation disk for an ordinary second boot, without guest edits."""
import hashlib,json,shutil,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
report=json.loads((k/'003/audit.json').read_text())
# This is a follow-up investigation of the completed installation, not promotion
# of the installation run: its shutdown popup remains a strict failure.
assert all(report[n] for n in ['pnp_binding_present','installed_inf_exact','installed_owned_display_exact','owned_display_registered','graphics_passed','one_dashboard_return'])
assert report['normal_shutdown_count']==1 and not report['unexpected_errors']
assert all(v['matched'] for v in report['payloads']) and all(report['baseline_checks'].values())
r=json.loads((k/'fixture-003.json').read_text())
source=ws/'work/runs/nt5-video-nt5-display-package-003/hdd.qcow2'
assert (source.parent/'cleanup.json').exists()
parent=ws/'outputs/native-windows-fatx-forensics/artifacts/video-nt5-display-package-003.qcow2'
target=parent.with_name('video-nt5-display-package-004.qcow2');seed=ws/'work/video-nt5-display-package-004-seed.qcow2'
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
assert not target.exists() and not seed.exists()
assert sha(parent)==r['fixture_sha256']
info=json.loads(subprocess.check_output(['qemu-img','info','--output=json',str(source)]))
assert (source.parent/info['backing-filename']).resolve()==parent.resolve()
source_hash=sha(source);shutil.copyfile(source,target);assert sha(target)==source_hash
subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b',parent.name,str(target)],check=True)
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(target),str(seed)],check=True)
subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b','../../../outputs/native-windows-fatx-forensics/artifacts/'+target.name,str(seed)],check=True)
assert sha(source)==source_hash
r.update(scope=__doc__,postinstall_source_sha256=source_hash,parent_fixture_sha256=r['fixture_sha256'],fixture_sha256=sha(target),seed_sha256=sha(seed),
         initial_trace_clean=False,host_reset_between_boots=False,guest_file_edits=False,installation_run_strict_passed=report['passed'],
         installation_method='Second ordinary boot from completed installation state; existing runner advances to xwnlag02')
r.pop('trace_sha256',None)
r['payloads']=[v for v in r['payloads'] if v['path']!='winnt/system32/xwn-video-trace.bin']
r['payloads'].append(dict(path='winnt/system32/xwnfb.dll',sha256=report['installed_owned_display_sha256']))
(k/'fixture-004.json').write_text(json.dumps(r,indent=2)+'\n');print('Installed state preserved for second boot; no guest files changed')
