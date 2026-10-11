"""Once-only final review of closed attempts and exact immutable inputs."""
import hashlib,importlib.util,json
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];out=k/'emu003'
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
dest=k/'final-review.json';assert not dest.exists()
assert read(out/'host-state.json')['closed'] and read(out/'closure.json')['closed']
assert read(k/'emu001/host-state.json')['closed'] and read(k/'emu002/closure.json')['refused_before_xemu']
frozen=read(k/'emulator-frozen003.json')
for n,h in frozen.items():assert sha(ws/n)==h,n
sp=importlib.util.spec_from_file_location('deps262',k/'runtime-dependencies003.py');deps=importlib.util.module_from_spec(sp);sp.loader.exec_module(deps)
assert deps.inventory()==read(k/'host-dependencies003.json')['files']
a,t=[read(out/n) for n in ['audit.json','trace.json']]
p=read(out/'preservation-proof.json') if (out/'preservation-proof.json').exists() else dict(passed=False,not_attempted='Stage1 refused before test surface; no complete guest pixels/callback evidence')
run=Path('E:/Codex-private-artifacts/xbox-windows-feasibility/coverage262/runs/nt5-coverage262-emu003')
host=read(run/'host-exit.json');protocol=read(run/'host-close.json') if (run/'host-close.json').exists() else dict(protocol_passed=False,not_invoked='Tracer quarantined and sent HMP quit before runner close helper')
r=dict(closed=True,physical_access=False,debugger=True,ordinary_qualified=False,native_gpu_ownership=False,
    frozen_inputs_verified=len(frozen),host_dependencies_verified=len(deps.inventory()),
    renderer_sha256=read(k/'renderer-build001.json')['executable_sha256'],
    native_attestations=sum(bool(c.get('attestation',{}).get('passed')) for c in t['checkpoints']),
    stages_completed=sum(c.get('state')==5 for c in t['checkpoints']),
    guest_probe=a['renderer_probe'],orderly_host_exit=host,host_close_protocol=protocol,
    integrity_passed=a['integrity_passed'],allocation=read(out/'allocation.json'),
    normal_shutdown_count=a['normal_shutdown_count'],dashboard_return=a['dashboard_return'],
    scoped_pixel_preservation_proved=p['passed'] and a['renderer_diagnostic_passed'] and host['passed'] and protocol['protocol_passed'],
    strict_qualification_passed=p.get('strict_qualification_passed',False),warnings_errors=a['warnings_errors'],
    actual_negative_controls=p.get('negative_controls',[]),synthetic_negative_controls=read(k/'proof-tests.json')['negative_controls'],
    complete_lifecycle=p.get('lifecycle',{}).get('full_callback_lifecycle_passed',False),
    raw_sha256=sha(run/'cpu-trace.log'),guest_result_sha256=sha(out/'artifacts/renderer-result.log') if (out/'artifacts/renderer-result.log').exists() else None,
    closed_attempts={'emu001':'Launch reply deadline expired before first native checkpoint; clean cold disk, no renderer stage; failure preserved.',
        'emu002':'Projected C capacity guard refused before xemu; no guest launch.',
        'emu003':'First native attestation passed; renderer stage1 refused reason7 (pending condition), no surface created. Interrupted disk retained with2orphans/2WBEMchain errors.'},
    limits='Owned diagnostic surface, unchanged header-locked probe and held arena only; no speedup/ordinary/physical promotion. Historical fixture policy differs from audio-integrated physical demo.')
assert not r['strict_qualification_passed'] or r['scoped_pixel_preservation_proved']
dest.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({n:r[n] for n in ['closed','scoped_pixel_preservation_proved','strict_qualification_passed','native_attestations','stages_completed','integrity_passed','normal_shutdown_count']},indent=2))
