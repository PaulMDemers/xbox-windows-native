"""Fresh248 active note; previous247/246 tails remain exact."""
import datetime,hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'continuation-active001.json';assert not dest.exists()
p=ws/'outputs/engineering-notes/CONTINUATION.md';old=p.read_bytes();snapshot=k/'artifacts/continuation-before248.md';assert not snapshot.exists();snapshot.write_bytes(old)
head='''#248 host-corrected worker barrier — NEW child prepared

247/preserve001 CLOSED FAILED: actual worker park/two fences completed, but host
compared saved UI report against reused worker reply and asserted. Bounded abort
released worker/reopened UI/resumed guest. Normal6006/dashboard/host exit and full
cold integrity passed; strict Ftdisk49 remains. Missing final marker prevents full
lifecycle qualification; worker-partial002.json separately records limited span.
Never relaunch/recollect247. Build001 permission/002 preparation/003 enum failure,
host adapter001/002 and proof001 mistakes retained. Compiled004 remains exact.

248 uses SAME compiled247004 emulator, new child and fixed host UI comparison.
Frozen1353 pins, actual source/fresh fixture/capacity review PASS. New host tests
pair54/guards72/close25/connection12/UI19/lifecycle20/worker-proof14 PASS. Actual
worker ASan/UBSan adapters from247 each3072 paths remain unchanged. No new build.

Inspect outputs/worker-barrier248/matrix001.json and preserve001/host-state.json
for actual actors. Sole new case nt5-phase248-preserve001, private E:/Codex-private-
artifacts/xbox-windows-feasibility/phase248-runs. Never duplicate launch/audit.
On close analyze-worker.py once, source/raw review/cold audit, final notes/commit.
Both gates retain shared resources and native permit remains refused. Latest
dirty flags at natural invalidation are observations; dirty GPU bytes there
are not preserved yet. Physical/peer baselines unchanged; emulator only.

'''
p.write_bytes(head.encode()+old);dest.write_text(json.dumps(dict(recorded_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),prior_sha256=hashlib.sha256(old).hexdigest(),current_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),physical_access=False,guest_launch=False),indent=2)+'\n');print('248 active note recorded')
