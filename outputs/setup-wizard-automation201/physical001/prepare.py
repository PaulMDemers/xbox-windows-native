"""Freeze two cold-qualified emulator lifecycles and physical-only guardian; no console access."""
import ast, hashlib, json
from pathlib import Path
k=Path(__file__).resolve().parent;kit=k.parent;ws=k.parents[2]
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
dest=k/'ready.json';assert not dest.exists()
for case in ['cancel006','cancel007']:
    a=read(kit/case/'audit.json');assert a['diagnostic_usable'] and a['integrity_passed'] and a['normal_shutdown_count']==1
    assert read(kit/case/'closure.json')['closed']
prior=read(kit.parent/'video-phase-physical200/candidate001/closure.json');assert prior['closed'] and prior['baseline_restored']
assert read(kit.parent/'video-phase-physical200/candidate001/restored-verification.json')['passed']
files=list(k.glob('*.py'))
for p in files:ast.parse(p.read_text(encoding='utf-8'))
files += [kit/name for name in ['wizard006.c','policy.h','guardian-physical001.c','restart_gate201.h','setup_gate201.h',
    'build-review006.json','guardian-physical-review001.json','build006.json','guardian-physical-build001.json','policy-tests.json',
    'artifacts/build006/wizard.exe','artifacts/guardian-physical001/guardian.exe',
    'cancel006/audit.json','cancel006/closure.json','cancel007/audit.json','cancel007/closure.json']]
for name in ['build-review006.json','guardian-physical-review001.json']:
    r=read(kit/name);assert r['passed']
    binary=kit/('artifacts/build006/wizard.exe' if name.startswith('build') else 'artifacts/guardian-physical001/guardian.exe')
    assert sha(binary)==r['binary_sha256']
assert (kit/'guardian-physical001.c').read_text()==(kit/'guardian002.c').read_text().replace('/cancel-emulator','/cancel-physical')
files += [kit.parent/'device-observation188/atomic_json.py',kit.parent/'fatx0098-soak3/physical.py',
    kit.parent/'gpu-reset-banner152/ftp_deadline.py',kit.parent/'native-windows-physical-f/decode-legacy-events.py',
    kit.parent/'video-phase-physical200/capture.json',kit.parent/'video-phase-physical200/candidate001/closure.json',
    kit.parent/'video-phase-physical200/candidate001/restored-verification.json']
result=dict(prepared=True,physical_qualified=False,launch_performed=False,pins={p.relative_to(ws).as_posix():sha(p) for p in files},
    writes='Unique /F/xwnwiz201p helpers, rollback ZIP and startup backup; temporary startup only. No SYSTEM/driver/service/dump/device policy writes.',
    runtime='Known exact physical instances only, verified welcome/active/foreground Cancel button once per held process lifetime. No focus mutation or unknown-dialog cancellation. Joined helper0 and real idle then unforced normal restart.',
    gates='Two complete fresh cold emulator lifecycle scopes passed, strict Ft49 remains FALSE. Physical result untested. Actual dashboard/ownership/provider/baseline/absent-directory/readback guards before launch. Unknown replies never retried. Startup restored FIRST on collection.',
    limits='No benchmark or Welcome automation; this isolated trial is only wizard cancellation and normal restart.')
dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print('Physical201 protocol frozen; no console access or launch')
