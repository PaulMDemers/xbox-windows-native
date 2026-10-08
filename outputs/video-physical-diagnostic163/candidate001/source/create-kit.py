"""Prospective nonpromoting display diagnostic; do not relax162 strict gates."""
import datetime,hashlib,json,shutil
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];old=k.parent/'video-physical-rehearsal162'
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
a=read(old/'control001/audit.json');assert a['workload_passed'] and a['integrity_passed'] and not a['strict_qualification_passed']
events=a['warnings_errors'];assert len(events)==1 and events[0]['source']=='Ftdisk' and events[0]['event_id']==49
physical=read(k.parent/'video-physical-review159/system-events.json')['records']
fields=['source','event_id','type','strings','data_hex']
assert any(all(v[f]==events[0][f] for f in fields) for v in physical)
assert not (old/'candidate001/runner-start.json').exists()
for name in ['common.py','preflight.py','audit.py','Run.ps1','check-leases.ps1','supervise.py']:
    text=(old/name).read_text(encoding='utf-8').replace('vphys162','vphys163').replace('rehearsal162','diagnostic163')
    if name=='Run.ps1':
        text=text.replace("[ValidateSet('control001','candidate001')]", "[ValidateSet('candidate001')]")
        text=text.replace("Join-Path $PSScriptRoot control001/audit.json", "Join-Path $PSScriptRoot '../video-physical-rehearsal162/control001/audit.json'")
        text=text.replace("if(!$control.strict_qualification_passed){throw 'Control failed strict gates; diagnose first'}", "if(!$control.workload_passed -or !$control.integrity_passed){throw 'Control diagnostic prerequisites failed'}")
        text=text.replace('fixtures-ready.json','diagnostic-plan.json')
    if name=='audit.py':
        text=text.replace("r['startup_unchanged']=", "trace=after['F'].read('winnt/system32/xwn-video-trace.bin');(art/'video-trace.bin').write_bytes(trace)\n    initial=before['F'].read('winnt/system32/xwn-video-trace.bin');(art/'before-video-trace.bin').write_bytes(initial)\n    r['trace_sha256']=m.sha(trace)\n    r['startup_unchanged']=")
    (k/name).write_text(text,encoding='utf-8')
case=k/'candidate001';case.mkdir(exist_ok=False)
shutil.copyfile(old/'fixture-candidate001.json',k/'fixture-candidate001.json')
shutil.copytree(old/'candidate001/before',case/'before')
shutil.copyfile(ws/'work/video-physical-rehearsal162-candidate001-seed.qcow2',ws/'work/video-physical-diagnostic163-candidate001-seed.qcow2')
f=read(k/'fixture-candidate001.json');assert sha(ws/'work/video-physical-diagnostic163-candidate001-seed.qcow2')==f['seed_sha256']
pins=read(old/'frozen-inputs.json')
for name,digest in pins.items():assert sha(ws/name)==digest,name
for p in list(k.glob('*.py'))+list(k.glob('*.ps1'))+[k/'fixture-candidate001.json',old/'control001/audit.json']:
    pins[str(p.relative_to(ws)).replace('\\','/')]=sha(p)
(k/'frozen-inputs.json').write_text(json.dumps(pins,indent=2)+'\n',encoding='utf-8')
(k/'diagnostic-plan.json').write_text(json.dumps(dict(passed=True,planned_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    intent='Candidate display compatibility diagnostic, not promotion or release qualification',
    control_audit_sha256=sha(old/'control001/audit.json'),physical_signature_exact=True,known_control_error=events[0],
    same_immutable_prepared_candidate_fixture=True,candidate162_launched=False,
    physical_access=False,physical_qualified=False,deployment_ready=False,
    strict_gates_unchanged=True,strict_baseline_failed=True,
    additional_requirement='Exact shared-acquire trace and retained two typed xwnown bindings; all new events retained, no strict event exception.'),indent=2)+'\n',encoding='utf-8')
print('New nonpromoting diagnostic163 pinned; candidate162 remains unlaunched')
