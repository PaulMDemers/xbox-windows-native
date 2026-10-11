"""Keep exact owned246 running state and prior continuation bytes."""
import datetime,json
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'continuation-active001.json';assert not dest.exists()
r=json.loads((k/'preserve001/host-state.json').read_text());p=ws/'outputs/engineering-notes/CONTINUATION.md';old=p.read_bytes();(k/'artifacts/continuation-before246.md').write_bytes(old)
prefix=f'''# Current:246 ACTIVE; one-shot frontend close/reopen diagnostic

Read outputs/frontend-close246/DESIGN.md and actual preserve001 host/trace/matrix
records before taking any action. Fresh nt5-phase246-preserve001, immutable239
seed; actual candidate build001. No native driver/policy/physical/peer changes.
One close/reopen request is allowed, never restart a recorded guest or collect
a completed stage again. Old244 failure and245 records remain unchanged.
Owned matrix exec session11204; case controller{r['controller_pid']},
runner{r['runner_pid']}, tracer{r['tracer_pid']}, observer{r['observer_pid']}.
Use actual records/process identity, not stale numeric PIDs, when resuming.
Only UI admission closes; renderer/display/shared references remain retained.
Host tests/refusals/atomic races passed. Actual GL completion/loan silence still
pending. Require reopen acknowledgement, full GDB teardown/mode0/resume, normal
restart/dashboard/orderly exit, complete existing cold audit and raw causal
analysis. Strict Ftdisk49 gate remains unchanged; no native ownership permit.
Preserve0101/video0093,0088rollback,immutable0.1.0 and all failed evidence.
Emulator only; no physical FTP/deploy/test.20GiB guard unchanged.

'''
p.write_bytes(prefix.encode()+old)
dest.write_text(json.dumps(dict(recorded_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),owned_state=r,session=11204,old_tail_preserved=True,physical_access=False),indent=2)+'\n')
