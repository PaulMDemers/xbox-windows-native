"""Final247/248 note, preserve prior exact continuation tails."""
import datetime,hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'continuation-closed001.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'));r=read(k/'diagnostic-review001.json');assert r['review_passed'] and read(k/'process-closure001.json')['closed'] and read(k.parent/'worker-barrier247/process-closure001.json')['closed']
p=ws/'outputs/engineering-notes/CONTINUATION.md';old=p.read_bytes();snap=k/'artifacts/continuation-before248-closed.md';assert not snap.exists();snap.write_bytes(old)
head='''#247/248 CLOSED — worker/UI barrier scope PASS,248 workload FAIL

Compiled247/build004 SHA6bd9f6d6b1f8ea3453ba7366b81399e3c7f06c2948241f341d446a81a94fcdce,
same exact binary in both new children. All owned actors CLOSED; no guest queued.
247 failed a host UI/worker report comparison; complete lifecycle marker missing.
Preserved failed overall outcome and separate bounded partial worker proof.
248 fixed host comparison, two real loader pins, full breakpoint teardown/resume.
Never replay/recollect either child, old builds or previous closed cases.

248 actual worker120160 parked250234300ns, twoGL_CONDITION_SATISFIED fences,
zero current surface-list entries,14 context bindings; UI closure/reopening PASS.
14339 lifecycle events,23 complete callback chains,3 target retirements before
final marker,0CPU-stopped frees,1828 complete UI loans1574 accelerated254 fallback,
one complete empty natural flush,0null sync returns. All shared resources remain
retained; no deletion/native permit. Natural flush flags had0rows; other natural
invalidation paths remain uninstrumented. Latest dirty GPU bytes at later
invalidation are NOT preserved by this checkpoint or earlier227 readback.

248 overallFAIL: inherited wizard201 pending-install wait258 timed out120210ms.
No result.log/retirement.log; CPU workload never started, no6006/dashboardreturn.
Single live runtime snapshot shell_running/no bugcheck; eight-minute owned host
bound then orderly HMPstop/quit exit0. Cold allocation6722files320dirs321clusters,
0orphans/errors;5 structural hives/28 selected protected files/policy/history
passed. SoleFtdisk49 type1 remains strictFAIL. No blanket file-content/durability
or causal link from worker gate to install timeout is claimed.247 separately had
normal restart/cold integrity but stays failed for host assertion/missing marker.

Implementation/adapters reviewed: O0/O2ASanUBSan each3072actual-helper paths,
23296checks; locks dropped for fences, FIFO released during finite park.13source
borrows restored. Failed permission/preflight/enum-build/adapters and raw logs
preserved.248 diagnostic-review001.json is scoped barrier review, not ordinary
qualification. Legacy audit labels242/244 are inherited descriptive text; actual
new inputs/results are pinned247/248 records. No physical/peer changes.

Next: investigate the specific inherited pending-install timeout before another
end-to-end qualification, using bounded installer/window lifecycle evidence and
unchanged device policy. Do not force cancel/disable devices to obtainPASS.
Instrument ALL natural surface invalidations for latest flags/data; conflicting
CPU/GPU aliases must refuse. Require latest preservation before any new disposal,
actor-owned unbinding, individual retained identities and bounded save-thread
completion. Worker/UI fences do not retire callbacks or shared caches/contexts.
NativeGPU permit remains refused. Preserve0101/video0093,0088rollback,immutable0.1.0.
Emulator only; next hardware deployment requires separately qualified candidate.
Maintain20GiBguard/backing chains; closed portable offload is separately recorded.

'''
p.write_bytes(head.encode()+old);dest.write_text(json.dumps(dict(recorded_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),prior_sha256=hashlib.sha256(old).hexdigest(),current_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),all_owned_closed=True,barrier_scope_passed=True,overall248_passed=False,physical_access=False),indent=2)+'\n');print('247/248 closed note recorded, failed scopes explicit')
