"""Final scope result only from closed real trace, guest bytes and cold audit."""
import hashlib,importlib.util,json,re
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];out=k/'emu001'
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
dest=k/'final-review.json';assert not dest.exists()
assert read(out/'host-state.json')['closed'] and read(out/'closure.json')['closed']
frozen=read(k/'emulator-frozen.json')
for n,h in frozen.items():assert sha(ws/n)==h,n
sp=importlib.util.spec_from_file_location('deps263',k/'runtime-dependencies.py');deps=importlib.util.module_from_spec(sp);sp.loader.exec_module(deps)
assert deps.inventory()==read(k/'host-dependencies.json')['files']
a,t=[read(out/n) for n in ['audit.json','trace.json']]
p=read(out/'preservation-proof.json') if (out/'preservation-proof.json').exists() else dict(passed=False)
run=Path('E:/Codex-private-artifacts/xbox-windows-feasibility/pending263/runs/nt5-pending263-emu001')
host=read(run/'host-exit.json');protocol=read(run/'host-close.json') if (run/'host-close.json').exists() else dict(protocol_passed=False)
masks=[]
for stage in t['checkpoints'][:4]:
    matches=re.findall(r'slot'+str(stage['stage'])+r'_pending_mask=(\d+)',stage.get('renderer_report',''))
    if len(matches)==1:masks.append(int(matches[0]))
sp=importlib.util.spec_from_file_location('sites263',k/'analyze-sites.py');sites=importlib.util.module_from_spec(sp);sp.loader.exec_module(sites)
parsed=sites.parse((run/'cpu-trace.log').read_bytes())
r=dict(closed=True,physical_access=False,debugger=True,ordinary_qualified=False,native_gpu_ownership=False,
    frozen_inputs_verified=len(frozen),host_dependencies_verified=len(deps.inventory()),
    renderer_sha256=read(k/'renderer-build001.json')['executable_sha256'],
    native_attestations=sum(bool(c.get('attestation',{}).get('passed')) for c in t['checkpoints']),
    stages_completed=sum(c.get('state')==5 for c in t['checkpoints']),pending_masks=masks,
    scalar_groups=parsed['groups'],scalar_sites=parsed['sites'],truncated_sites=parsed['truncated_sites'],
    guest_probe=a['renderer_probe'],orderly_host_exit=host,host_close_protocol=protocol,
    integrity_passed=a['integrity_passed'],allocation=read(out/'allocation.json'),
    normal_shutdown_count=a['normal_shutdown_count'],dashboard_return=a['dashboard_return'],
    scoped_pixel_preservation_proved=p['passed'] and a['renderer_diagnostic_passed'] and host['passed'] and protocol['protocol_passed'] and masks==[0,0,0,0] and not parsed['truncated_sites'],
    strict_qualification_passed=p.get('strict_qualification_passed',False),warnings_errors=a['warnings_errors'],
    actual_negative_controls=p.get('negative_controls',[]),synthetic_negative_controls=read(k/'proof-tests.json')['negative_controls'],
    complete_lifecycle=p.get('lifecycle',{}).get('full_callback_lifecycle_passed',False),
    raw_sha256=sha(run/'cpu-trace.log'),guest_result_sha256=sha(out/'artifacts/renderer-result.log') if (out/'artifacts/renderer-result.log').exists() else None,
    earlier262_reason7_producer_resolved=False,
    limits='Exact owned diagnostic surface and historical emulator fixture only. A zero current pending mask does not identify the earlier262 producer. No ordinary/performance/physical/native GPU grant; strict event gate remains unchanged.')
assert not r['strict_qualification_passed'] or r['scoped_pixel_preservation_proved']
dest.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({n:r[n] for n in ['closed','scoped_pixel_preservation_proved','strict_qualification_passed','native_attestations','stages_completed','integrity_passed','normal_shutdown_count','pending_masks','scalar_groups','truncated_sites']},indent=2))
