"""Record closed245 and failed244 precisely; preserve prior continuation tail."""
import datetime,json
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];c=ws/'outputs/engineering-notes/CONTINUATION.md';dest=k/'continuation-closed001.json';assert not dest.exists()
assert json.loads((k/'process-closure001.json').read_text(encoding='utf-8-sig'))['closed']
assert json.loads((k/'review001.json').read_text())['passed']
old=c.read_bytes();(k/'artifacts/continuation-before245-closed.md').write_bytes(old)
prefix='''# Current:245 CLOSED; actual hooks retired, final frontend loan still active

Read outputs/gpu-lifecycle245/REPORT.md/DESIGN.md/NEXT.md/review001.json and
actual preserve001 lifecycle/trace/audit/matrix records. All root244/245 actors
CLOSED; no queued guest. Never replay/recollect started cases. Emulator only;
no physical IO, peer integration, native driver or policy change.

Actual244/build005 keeps QOM PCIDevice parent first, compiled offset-zero guard.
Failed244/build004 placed marker before parent; first marker refused, no
preservation issued; full point teardown/mode0/resume. Its cold audit failed
missing before-system; original trace/host/matrix failure retained. Separate
remainder completed previously unperformed metadata stages, no old PASS created;
old protected-hash result UNRECORDED. Older setup/build failures retained/restored.

NEW245 actual same-boot pins Xromwell11100/FreeLoader200a20, terminal3 preservation:
3dirty/3downloaded/3072000 compared bytes, paired readonly retained-reference
census unchanged.13648 lifecycle events,23 callback chains/23 actual frees,
all3 target hooks retired before FreeLoader marker during RUNNING CPU. Stopped
CPU queue execution NOT proved.1744 completed frontend fence/release chains,
1496 accelerated/248 fallback; marker loan counts0/1. One natural flush complete.
Zero sync-null returns; no runtime basis to patch that static branch.

Normal restart/dashboard/orderly exit0,65 allocations/releases/refusals,
3194880 verified CPU bytes/four joins, full clean6724files/320dirs/321clusters,
5hives/protected/startup/policy/event-history PASS. SoleFtdisk49 type1 remains
strictFALSE. Ordinary/physical/display quiescence/native ownership FALSE.
No all-file-content/power-loss/repeat-boot claim. Retain texture/surface alias,
shader/module/vertex/display refs and save-handle-versus-liveness distinction.

Next NEW protocol must close/drain actual frontend loan outside locks required
by actors, with bounded completion and actual shared-context/per-object ownership
evidence. No speculative disposal/native grant. Preservephysical0101/video0093,
0088rollback,immutable0.1.0 and all failures. Closed234 build/portable and244/245
portable files readback-verified on E with original junction paths; no backing
chains moved. Keep20GiB guard; new build/portable projection needs capacity check.

'''
c.write_bytes(prefix.encode()+old)
dest.write_text(json.dumps(dict(recorded_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),all_owned_closed=True,no_root_guest_queued=True,old_tail_preserved=True,physical_access=False),indent=2)+'\n')
