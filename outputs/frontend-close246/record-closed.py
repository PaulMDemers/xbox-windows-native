"""Record actual closed246 and preserve the entire prior continuation byte tail."""
import datetime,hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'continuation-closed001.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'));assert read(k/'review001.json')['passed'] and read(k/'process-closure001.json')['closed']
p=ws/'outputs/engineering-notes/CONTINUATION.md';old=p.read_bytes();(k/'artifacts/continuation-before246-closed.md').write_bytes(old)
prefix='''# Current:246 CLOSED; real UI loans closed/reopened, shared contexts retained

Read outputs/frontend-close246/DESIGN.md/REPORT.md/NEXT.md/review001.json and
actual preserve001/frontend/trace/audit/matrix/process-closure records. ALL owned
246 processes CLOSED; build session45619 and matrix11204 CLOSED0. No guest queued.
Never relaunch or recollect old cases. Emulator only; hardware/peer/native policy
unchanged. Preservephysical0101/video0093,0088rollback,immutable0.1.0/all failures.

Actual build001 changes only four emulator source files relative244/build005;
all borrowed sources restored. One QOM request closes UI frame admission; real
UI actor acknowledges loan0/BQL0 and GL_CONDITION_SATISFIED in its own context.
Raw evidence:298488700ns closed interval,zero new loans,acknowledged reopen and
resumed real loans. Context65537/thread32308,last fallbacktexture26 already
deleted(live0),program9/arraybuffer5/elementbuffer6/VAO3 still bound. No bindings
cleared, cache/object/context disposal or native GPU ownership permit.

16989 lifecycleevents,23 completecallbackchains,3/3 targethooks retired while
CPU RUNNING,1 complete naturalflush,2162 completeframes(1908accelerated/254fallback),
zero sync-null returns. Actual sameboot Xromwell/FreeLoader residentpins,three
dirty surfaces/3072000bytes prior same-path readback,fullGDBteardown/mode0/resume.
Latest dirty data at natural invalidation remains unobserved; prior preservation
does not prove a later draw survives disabled-download flush.

Normalrestart/dashboard/orderlyexit0,65allocations/releases/refusals,3194880CPU
verifiedbytes/fourjoins,full clean6724files/320dirs/321dirclusters,5structuralhives,
28selectedprotected/staged/startup/policy/SetupAPI/event-history PASS. SoleFtdisk49
type1 remains strictFALSE. Ordinary/physical/fullsharedretirement/nativeFALSE.
No all-file-content,power-loss or repeat-boot durability claim. Host actualhelper
O0/O2 ASan/UBSan each2304freshlifecycles/256joinedactorraces passed;1140pins exact.
Preliminary missingtestassertmacro compilefailure and missingGDBcapsule setup
retained; no product/binary change to make tests pass. Old244/245 untouched.

Next NEW bounded protocol: worker-owned renderer/display admission barrier,
actual context/binding/per-object completion; capture latest dirty data before
any disposal. No actor wait under BQL/FIFO/PG/renderer-required locks and no
native grant from UI silence. Savehandles are not thread-liveness evidence.
Closed246 portable copied/readback-verified to E, original junction retained;
no disk backing chain moved. Keep20GiB guard and explicit capacity projection.

'''
p.write_bytes(prefix.encode()+old);dest.write_text(json.dumps(dict(recorded_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),all_owned_closed=True,no_root_guest_queued=True,old_tail_preserved=True,old_tail_sha256=hashlib.sha256(old).hexdigest(),report_sha256=hashlib.sha256((k/'REPORT.md').read_bytes()).hexdigest(),physical_access=False),indent=2)+'\n')
