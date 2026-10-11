"""Prepend247 active note, preserve exact prior continuation tail privately."""
import datetime,hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'continuation-active001.json';assert not dest.exists()
p=ws/'outputs/engineering-notes/CONTINUATION.md';old=p.read_bytes();snapshot=k/'artifacts/continuation-before247.md';assert not snapshot.exists();snapshot.write_bytes(old)
head='''#247 worker barrier — prepared, one new emulator child authorized

Compiled004 extends exact246 UI gate, native224/219/211 unchanged. Finite worker
checkpoint and two100ms context fences occur with no actor-required locks held.
Current surface flags explicitly refuse dirty/pending work; no new disposal.
Natural flush records latest flags before its existing invalidation. Latest
dirty GPU bytes at that disposal are NOT yet preserved; no native permit.

ASan/UBSan O0/O2 actual-worker adapters each3072 paths PASS; parser14 guards PASS,
existing host guards72/pair54/close25/connection12/UI19/lifecycle20 PASS.
Earlier permission/preflight/enum-build and adapter failures preserved under247.
All13 borrowed sources restored. Frozen1262 pins/prelaunch reviewed. C guard20GiB.

Next sole fresh case: outputs/worker-barrier247/preserve001, private
E:/Codex-private-artifacts/xbox-windows-feasibility/phase247-runs/nt5-phase247-preserve001.
Inspect matrix001.json/host-state.json for actual actors; never duplicate launch
or audit. On close analyze-worker.py once, raw review, cold audit, notes/commit.
Emulator only, no peer merge or hardware FTP/deploy/test. Physical0101/video0093,
0088rollback/immutable0.1.0 and all prior evidence retained. Strict Ftdisk49 gate
unchanged. This is not full shared-reference retirement/native ownership.

'''
p.write_bytes(head.encode()+old)
dest.write_text(json.dumps(dict(recorded_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),prior_continuation_sha256=hashlib.sha256(old).hexdigest(),current_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),guest_launch=False,physical_access=False),indent=2)+'\n')
print('247 active note recorded, exact old tail preserved')
