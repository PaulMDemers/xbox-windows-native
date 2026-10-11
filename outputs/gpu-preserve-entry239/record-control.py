"""Close source/evidence report after a successful control and pre-VM capacity refusal."""
import hashlib,json,ast
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'control-review001.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
a=read(k/'control001/audit.json');t=read(k/'control001/trace.json');s=read(k/'preserve001/host-state.json');m=read(k/'matrix001.json')
assert a['cpu_scope_passed'] and a['guest_trace_scope_passed'] and a['integrity_passed'] and a['normal_shutdown_count']==1 and a['orderly_host_exit_passed']
assert t['passed'] and t['closed'] and t['guest_resumed'] and not t['remaining_breakpoints'] and not t['preservation']['request_accepted'] and not t['preservation']['ram']
assert s['closed'] and len(s['resource_attempts'])==1 and not s['resource_attempts'][0]['resource_busy'] and not s['resource_attempts'][0]['runner_start_exists'] and not s['resource_attempts'][0]['run_exists']
assert not (k/'preserve001/runner-start.json').exists() and not Path('E:/Codex-private-artifacts/xbox-windows-feasibility/phase239-runs/nt5-phase239-preserve001').exists()
assert not m['completed'] and not m['closed'];assert [(e['source'],e['event_id'],e['type']) for e in a['warnings_errors']]==[('Ftdisk',49,1)]
assert not a['strict_qualification_passed'] and not a['new_events']['application']
pins=read(k/'emulator-frozen.json')
for path,h in pins.items():assert sha(ws/path)==h,path
for p in k.glob('*.py'):ast.parse(p.read_text(encoding='utf-8'),filename=str(p))
r=dict(passed=True,control_scope_passed=True,preservation_guest_launched=False,preservation_qualified=False,frozen_inputs_unchanged=len(pins),matrix_closed_flag=False,matrix_flag_limit='Preserved matrix closed=False means the requested second guest did not exist, not that an owned VM remains running; actual controller process closure is separately verified',control_audit_sha256=sha(k/'control001/audit.json'),control_trace_sha256=sha(k/'control001/trace.json'),prevm_refusal_sha256=sha(k/'preserve001/host-state.json'),physical_access=False,strict_qualified=False)
dest.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
(k/'REPORT.md').write_text('''#239 control passed; preservation refused before VM creation

Fresh239/control001 reached pinned Xromwell11100 and FreeLoader200a20, observed three dirty non-overlapping surfaces3072000 bytes at Xromwell with empty FIFO/parser/no waits or frontend work, and resumed with complete breakpoint teardown. Control issued no preservation setter or RAM capture.

Unchanged224 CPU workload completed65 allocations/releases/exposure refusals,3194880 verified bytes and four worker joins. Eight retirement rounds/128 sequential MMIO reads still refuse UNMODELED_BUSY/NO_OWNERSHIP. One normal shutdown/dashboard return, orderly emulator exit0/no Kill, full allocation/selected protected hashes/five structural hives/startup/device policy/event and SetupAPI history passed. Sole Ftdisk49 type1 remains strict failure; application delta empty. This is debugger control evidence, not native acceleration/ownership or physical qualification.

239/preserve001 was refused by the conservative projected portable-copy20GiB guard before resource acquisition/runner-start/instance creation. No preservation VM, setter, write or cold collection exists. Matrix completed=False/closed=False remains exact failed evidence; actual process closure is separately recorded. Never replay that case. NEW240/preserve001 uses the same verified immutable239 seed and pairs with this control, without replaying the control.

Primary pinned qmp_pmemsave/physical-memory source proved RAM reads invoke GPU surface read callbacks. A before RAM capture could itself download dirty surfaces: source was corrected BEFORE any launch to perform no control/before capture. Candidate post-success captures are explicitly callback-bearing observations. The actual worker comparison, not these captures, is the preservation discriminator.

Host62 actual parser/experiment adapter checks,72 guard checks,12 single-connection checks and25 bounded orderly-close checks passed;560 frozen inputs remained unchanged. Preserve initial adapter-artifact collision, host command quoting refusals, numeric PID reuse refusal and portable guard failure. Closed238 build191820853 bytes and closed237/238/239 portable copies were readback hash verified to E with original junction paths; no backing chains moved. First portable-offload guard refused missing237 orderly exit metadata before copying; subsequent unique destination used the actual older forced-closure evidence without inventing durability qualification. Physical baseline/rollback/0.1.0 and peer branches unchanged.
''',encoding='utf-8')
print('239 control and pre-VM failure CLOSED evidence recorded')
