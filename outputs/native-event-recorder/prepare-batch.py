"""Prepare exactly three independent, recorder-enabled reproduction attempts."""
import hashlib,json,shutil
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
f=json.loads((k/'fixture-002.json').read_text())
b=json.loads((k/'build.json').read_text())
source=ws/'work/native-event-recorder-002-seed.qcow2'
base=k.parent/'native-windows-fatx-forensics/artifacts'/f['fixture_name']
assert sha(source)==f['seed_sha256'] and sha(base)==f['fixture_sha256']
assert sha(k/'artifacts/xemu-events.exe')==b['binary_sha256']
cases=['003','004','005'];plan=k/'batch-plan.json'
assert not plan.exists()
for case in cases:
    assert not (k/('fixture-'+case+'.json')).exists()
    assert not (ws/('work/native-event-recorder-'+case+'-seed.qcow2')).exists()
    assert not (ws/('work/runs/nt5-native-event-recorder-'+case)).exists()
r=dict(scope=__doc__,cases=cases,maximum_launches=3,physical_access=False,
       stop_policy='Finish these three outcomes, including clean runs. Stop before another launch after a timeout, failed audit tool or invalid trace; preserve evidence and clean up owned processes.',
       seed_sha256=f['seed_sha256'],fixture_sha256=f['fixture_sha256'],emulator_sha256=b['binary_sha256'],
       intervention='None: recorder enabled in all three; no debugger, paused capture, driver change, registry edit or device removal.',
       source_manifest='fixture-002.json',resource_model=None,
       independent_clones=True,consecutive_guest_reboots=False)
plan.write_text(json.dumps(r,indent=2)+'\n')
for case in cases:
    dest=ws/('work/native-event-recorder-'+case+'-seed.qcow2')
    shutil.copyfile(source,dest);assert sha(dest)==f['seed_sha256']
    row=dict(f,case=case,role='recorder_enabled_reproduction',batch_plan='batch-plan.json')
    (k/('fixture-'+case+'.json')).write_text(json.dumps(row,indent=2)+'\n')
print('Prepared fixed batch: '+', '.join(cases))
