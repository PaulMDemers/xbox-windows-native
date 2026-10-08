"""Preserve closed161 host failure; shorten owned parent path without editing parents."""
import datetime,hashlib,json,shutil
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];old=k.parent/'video-physical-rehearsal161'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
run=ws/'work/runs/nt5-vphys161-control001';assert (run/'cleanup.json').exists()
p=old/'control001/closure.json';assert not p.exists()
p.write_text(json.dumps(dict(closed=True,recorded_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    runner_exit_code=1,owned_pid=91956,emulator_started=True,windows_launch_requested=False,
    cpu_trace_bytes=(run/'cpu-trace.log').stat().st_size,
    error='Windows xemu could not open accumulated nested backing paths; private-link monitor failed after process exit.',
    stderr_sha256=sha(run/'xemu-stderr.log'),cleanup_sha256=sha(run/'cleanup.json'),
    strict_qualification_passed=False,physical_writes=False,never_relaunch=True,
    candidate_prepared=True,candidate_launched=False),indent=2)+'\n',encoding='utf-8')
for name in ['restore.py','test-restore.py','restore-tests.json','common.py','preflight.py','audit.py','Run.ps1','freeze-runtime.py','prepare.py','DESIGN.md']:
    text=(old/name).read_text(encoding='utf-8').replace('rehearsal161','rehearsal162').replace('vphys161','vphys162')
    if name=='prepare.py':
        text=text.replace("source=ws/'work/runs/nt5-physical-f-high-allocation-r15/hdd.qcow2';assert (source.parent/'cleanup.json').exists()",
            "source=ws/'outputs/native-windows-fatx-forensics/artifacts/video-physical-rehearsal162-parent.qcow2';assert read(k/'parent-review.json')['virtual_contents_equal']")
        text=text.replace("str(source.relative_to(ws)).replace('\\\\','/').replace('work/','../../../work/',1)","source.name")
    if name=='freeze-runtime.py':text=text.replace('nt5-vtime156-','nt5-vtime156-')
    (k/name).write_text(text,encoding='utf-8')
pins=json.loads((old/'frozen-inputs.json').read_text(encoding='utf-8'))
pins={n:d for n,d in pins.items() if not n.startswith('outputs/video-physical-rehearsal161/')}
for path in k.glob('*'):
    if path.suffix in ['.py','.ps1','.md','.json']:pins[str(path.relative_to(ws)).replace('\\','/')]=sha(path)
(k/'frozen-inputs.json').write_text(json.dumps(pins,indent=2)+'\n',encoding='utf-8')
print('Closed161 failure preserved; new162 sources created')
