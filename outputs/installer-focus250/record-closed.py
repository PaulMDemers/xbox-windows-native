"""Prepend actual closed state, retaining the entire prior continuation tail."""
import datetime,hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'continuation-closed001.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
assert read(k/'closed-review001.json')['review_passed'] and read(k/'process-closure001.json')['closed']
p=ws/'outputs/engineering-notes/CONTINUATION.md';old=p.read_bytes();original=(k.parent/'installer-focus249/artifacts/continuation-before249.md').read_bytes();assert old.endswith(original)
head='''#249/250 CLOSED — workload/UI/worker scope PASS; installer hold not reproduced

All owned sessions closed, no guest or hardware test queued.249 failed missing
inventory before Windows launch; resumed/teardown and full cold audit retained.
250 NEW corrected kit supplied/static-preflighted exact inventory, same compiled
247004 emulator and249 wait-only helper. One launch16:42:51UTC, dashboard16:44:11,
cold-audited closure16:44:49 October11. Never replay/recollect either closed case.

Only F/xwnret224/wizard.exe gained every-five-second read-only refused-action
foreground/GUI/title/class/process-creation telemetry. Original006 eligibility,
input/revalidation/idle/timeout and policy exact inverse reviewed; drivers,
settings, startup/device policy unchanged. No new focus/dialog/physical actions.
250 three real target1/2/5 closures and5100ms idle, completed23430ms. ZERO refused
wait snapshots: original248 foreground owner/conjunct/producer remains unresolved,
not fixed. Host malformed grammar/projection tests passed; wait branch runtime
unexercised. Keep telemetry for next justified experiment; no blind repeat boots.

250 raw scoped proofPASS: worker92948 two fences,266230100ns park; UI gate closure/
reopen,14993events23complete callbacks0CPU-stopped frees,1910UIloans1655accelerated
255fallback,one empty completeflush. CPU64leases65alloc/releases/refusals,
3194880verifiedbytes/fourjoined workers; eight retirement snapshots128reads still
refuse NO_OWNERSHIP/UNMODELED_BUSY. Normal6006/dashboardreturn. Cold6724files,
320dirs321dirclusters0errors/orphans,5hives28protected/history/policyPASS. Sole
Ftdisk49 strictFAIL; debugger never ordinary/physical/release/nativeGPUqualified.

Next common invalidation/latest-content discriminator:
outputs/installer-focus250/INVALIDATION-NEXT.md. Current247 flush-only82/83 records
no entries and misses other paths; earlier227 checkpoint may be stale. Observe
latest flags/controlled contents and actual dirty/clean CPU/GPU alias ordering,
refuse conflicts before any disposal change. Shared references/context bindings/
shader actor joins remain prerequisites. No graphics code changed this turn.

Closed portable249/250 caches hash/readback offloaded to E with original junctions;
no backing chains moved.20GiBguard unchanged; inspect actual capacity. Physical
0101/video0093,0088rollback,immutable0.1.0,peer devices and all failures preserved.
Unified preparation7638 and controllers55871/92551 closed; process-closure001
checks actual identities, never old-PID kills. Source/reports reviewed and pushed.

# Earlier record preserved

'''
p.write_bytes(head.encode()+old)
dest.write_text(json.dumps(dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),before_sha256=hashlib.sha256(old).hexdigest(),after_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),original_tail_sha256=hashlib.sha256(original).hexdigest(),all_owned_closed=True,physical_access=False),indent=2)+'\n')
print('249/250 actual closed continuation recorded; historical tail preserved')
