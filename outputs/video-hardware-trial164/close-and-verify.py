"""Close completed owned runs and verify runtime snapshots/source pins, not recollect disks."""
import ast,hashlib,json,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rows=[]
for folder,case,runid in [('video-physical-rehearsal162','control001','nt5-vphys162-control001'),
    ('video-physical-diagnostic163','candidate001','nt5-vphys163-candidate001'),
    ('video-helper-runtime165','candidate001','nt5-vphys165-candidate001')]:
    kit=k.parent/folder;out=kit/case;run=ws/'work/runs'/runid;dest=out/'closure.json';assert not dest.exists()
    cleanup=read(run/'cleanup.json');launch=read(out/'launch.json');a=read(out/'audit.json');instance=read(run/'instance.json')
    assert len(launch['cycles'])==1 and launch['cycles'][0]['dashboard_return'] and a['workload_passed'] and a['integrity_passed']
    pins=read(kit/'frozen-inputs.json');checked=0
    for name,digest in pins.items():assert sha(ws/name)==digest,name;checked+=1
    snapshot=out/'source';assert snapshot.exists()
    for p in snapshot.iterdir():
        if p.is_file():assert sha(p)==sha(kit/p.name),p.name
    r=dict(closed=True,run=runid,owned_pid=instance['processId'],cleanup_sha256=sha(run/'cleanup.json'),
        launch_sha256=sha(out/'launch.json'),audit_sha256=sha(out/'audit.json'),source_pins_checked=checked,
        source_snapshot_exact=True,physical_access=False,debugger=False,workload_passed=a['workload_passed'],
        integrity_passed=a['integrity_passed'],strict_qualification_passed=a['strict_qualification_passed'],
        normal_shutdown_count=a['normal_shutdown_count'],never_relaunch_or_recollect=True)
    dest.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');rows.append(r)
for folder in ['video-physical-review159','video-physical-rehearsal160','video-physical-rehearsal161','video-physical-rehearsal162','video-physical-diagnostic163','video-hardware-trial164','video-helper-runtime165']:
    for p in (k.parent/folder).rglob('*.py'):ast.parse(p.read_text(encoding='utf-8'))
(k/'series-closure.json').write_text(json.dumps(dict(owned_guest_runs_closed=True,runs=rows,
    physical_deployment_performed=False,pending='Actual unplugged Razer/UnleashX state before one hardware diagnostic',
    all_original_failures_preserved=True,strict_event_gates_not_waived=True),indent=2)+'\n',encoding='utf-8')
print('Three completed ordinary runs closed; snapshots/pins exact; hardware still pending')
