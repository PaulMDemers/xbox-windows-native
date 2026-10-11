"""Review actual closed safe refusal; no re-launch/collection or positive gate substitution."""
import json,hashlib
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'refusal-review001.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=read(k/'preserve001/trace.json');a=read(k/'preserve001/audit.json');s=read(k/'preserve001/host-state.json');m=read(k/'matrix001.json')
assert s['closed'] and s['cleanup_record_exists'] and s['audit_exit_code']==0 and m['closed'] and not m['completed']
assert r['closed'] and not r['passed'] and r['guest_resumed'] and not r['remaining_breakpoints'] and r['physical_mode_restored']
p=r['preservation'];q=p['result'];assert p['request_accepted'] and p['terminal_state']==4 and p['immutable_reread_matched'] and not p['ram']
assert q['state']==4 and q['reason']==21 and q['consume_stop']==5 and not any(q[n] for n in ['surfaces','dirty','downloaded','bytes','error','old_halt','consume_steps','consume_words','wait_before','wait_after'])
assert q['request']==q['gate']==[0,0,0,0,1,0,0,16,0,1]
assert a['cpu_scope_passed'] and a['integrity_passed'] and a['normal_shutdown_count']==1 and a['orderly_host_exit_passed']
assert not a['guest_trace_scope_passed'] and not a['backend_preservation_scope_passed'] and not a['strict_qualification_passed']
assert [(v['source'],v['event_id'],v['type']) for v in a['warnings_errors']]==[('Ftdisk',49,1)] and not a['new_events']['application']
pins=read(k/'emulator-frozen.json')
for n,h in pins.items():assert sha(ws/n)==h,n
record=dict(evidence_review_passed=True,preservation_passed=False,request_accepted=True,closed_safe_refusal=True,no_downloads=True,cold_integrity_passed=True,cpu_scope_passed=True,normal_shutdown_count=1,strict_qualified=False,physical_access=False,frozen_inputs_unchanged=len(pins),trace_sha256=sha(k/'preserve001/trace.json'),audit_sha256=sha(k/'preserve001/audit.json'),reason=21,consume_stop=5,limits='Inactive pusher rejected before empty queue check. No actual fence/readback/retirement. Source evidence justifies a NEW narrow consume correction, not a runtime gate waiver.')
dest.write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
(k/'REPORT.md').write_text('''#240 CLOSED safe preservation refusal

The one unique accepted request at resident-pinned Xromwell11100 published immutable state4/reason21/consume_stop5. Raw request/gate were identical GET=PUT=0, parser0, PUSH0=0/DMA_PUSH=0, waits0; no commands or steps consumed. Actual pinned pfifo_run_pusher rejects disabled/suspended pusher access before checking whether the queue is empty. No GL fence/download or RAM capture occurred. This is failed preservation evidence, not GPU loss or a native-driver crash. Request was not retried.

The safe refusal restored prior admission. Both executing loader32-byte pins matched, two breakpoints removed, virtual mode0 verified and guest resumed. Native224 workload completed65 allocations/releases/exposure refusals/3194880 verified bytes/four joins; eight retirement rounds/128 sequential MMIO reads still reject ownership. Windows normal shutdown6006 once/dashboard return and orderly host exit0/no Kill. Full clean allocation/selected hashes/five hives/startup/policy/SetupAPI and event history passed. Sole Ftdisk49 type1 remained strict failure; application delta empty. Overall preservation/ordinary/physical/native ownership remain FALSE. Matrix completed=False with closed=True is preserved.

Fresh240 runtime reused the exact immutable239 seed and completed239 control, unchanged238 host executable and native224/219/211 policy/no synthetic null binding.600 frozen inputs unchanged. Host62 parser/experiment adapter checks,72 guard checks,12 one-connection checks and25 closure checks passed. Generic copied report labels239/238 refer to inherited helper names; actual output paths, binary hashes and records identify240. review-closed.py is the pre-authored success reviewer and was NEVER executed on this failure; review-refusal.py preserves the actual negative gates.

The justified next change241 skips consumer invocation only for a live request with no waits and an empty completed parser, under the real FIFO lock and halted producer admission. It does not enable pusher access, clear errors/waits or fake completion. Existing renderer locks, gates, fences/downloads, byte comparisons and reference-retention contract remain required. No physical access, peer integration or baseline/rollback/release changes.
''',encoding='utf-8')
print('240 closed refusal preserved; preservation FALSE')
