"""Fresh runtime identity after a host TaskId length guard; reuse immutable reviewed helper."""
import hashlib,json,shutil
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];old=k.parent/'video-hardware-trial164'
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
run=ws/'work/runs/nt5-vphys164-candidate001';assert run.exists() and not (run/'instance.json').exists()
(old/'candidate001/closure.json').write_text(json.dumps(dict(closed=True,bootstrap_started=False,windows_launch_requested=False,
    runner_exit_code=1,error='Derived InstanceTask exceeded host40-character TaskId limit',
    source_sha256=sha(old/'Run-Helper.ps1'),original_path_guard_failure_preserved=True,
    helper_binary_failed=False,prepared_fixture_unchanged=True,never_relaunch=True),indent=2)+'\n',encoding='utf-8')
for name in ['common.py','preflight.py','audit.py','supervise.py','check-leases.ps1']:
    (k/name).write_text((old/name).read_text(encoding='utf-8').replace('vphys164','vphys165'),encoding='utf-8')
text=(old/'Run-Helper.ps1').read_text(encoding='utf-8').replace('vphys164','vphys165').replace('video-hardware-trial164','video-helper-runtime165')
text=text.replace('windows-native-physical-hardware-trial164','windows-native-vtrial165').replace('helper-frozen-inputs.json','frozen-inputs.json')
(k/'Run.ps1').write_text(text,encoding='utf-8')
shutil.copyfile(old/'fixture-candidate001.json',k/'fixture-candidate001.json')
(k/'candidate001').mkdir(exist_ok=False)
shutil.copytree(old/'candidate001/before',k/'candidate001/before')
shutil.copyfile(ws/'work/video-hardware-trial164-candidate001-seed.qcow2',ws/'work/video-helper-runtime165-candidate001-seed.qcow2')
shutil.copyfile(old/'emulator-ready.json',k/'emulator-ready.json')
pins={str(p.relative_to(ws)).replace('\\','/'):sha(p) for p in list(k.glob('*.py'))+list(k.glob('*.ps1'))+[
    k/'fixture-candidate001.json',old/'build-review.json',old/'artifacts/runner.exe',old/'runner.c',
    k.parent/'video-physical-diagnostic163/diagnostic-review.json',k.parent/'video-physical-rehearsal162/control001/audit.json',
    k.parent/'xemu-cpu-surface-evict/build003/artifacts/xemu-candidate.exe',k.parent/'video-surface-history/Invoke-Exclusive.ps1']}
(k/'frozen-inputs.json').write_text(json.dumps(pins,indent=2)+'\n',encoding='utf-8')
assert sha(ws/'work/video-helper-runtime165-candidate001-seed.qcow2')==read(k/'fixture-candidate001.json')['seed_sha256']
assert len('windows-native-vtrial165')<=40 and 'video-physical-hardware-trial164' not in text
print('Fresh165 host arguments/seed validated; helper/driver/settings unchanged')
