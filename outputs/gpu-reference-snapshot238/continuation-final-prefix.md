# Current:238 CLOSED; Xromwell dirty ranges observable, FreeLoader sync pending

Read outputs/gpu-reference-snapshot238/REPORT.md/DESIGN.md/SCHEMA.md/NEXT.md,
review001.json/reference-analysis001.json/directory-delta001.json and actual
case records. Parent91b6656. Preparation38560 CLOSED0, matrix97215 CLOSED0
2026-10-11T01:53:05.939400+00:00. All three runs closed/cold audited once;
never relaunch/recollect dashboard001/xbe001/freeldr001 or235/236/237.
Root guest work complete; no root guest queued. Confirm process-closure001.

New compiled238 exe6fbc96315b3f4dd7ee5bd159f0a059ed2983920025dfe1c4a48537c5d928b52c,
only nv2a.c/nv2a_int.h/GL renderer.c changed relative234; borrowed sources
restored. Native224/build002/219/211 captured-core policy/no synthetic null
bindings unchanged.502 frozen pins unchanged. Host compiled O0/O2 ASan/UBSan
actual atomics/FIFO/worker PASS (20k timeout races+2k publication races each,
0..129 surface bounds/renderer lock refusal). Sampler65/guards72/connection12/
closure25/classification180/directory parser5 PASS; host wrapper path/header
regex/guard input failures preserved before launch. Frozen review generic
current-FIFO scope wording is stale; actual current-FIFO=true records and
SCHEMA/REPORT correct it without changing frozen source/runtime evidence.

Independent samples: dashboard FIFO GET66743708/PUT66744836, PG pending100000/
wait2NOP, framebuffer-in-use1,3 dirty surfaces3072000 bytes/3 callbacks.
Xromwell executing11100: FIFO GET=PUT=0/parser0/PG waits0, framebuffer0,
3 dirty surfaces3072000 bytes/3 callbacks, no flush/sync pending.
FreeLoader executing200a20: FIFO GET=PUT=0/parser0/PG waits0, no surface
bindings/callbacks in bounded list, sync_pending1. Renderer try-lock succeeded
all3; no truncation, invalid ranges or overlap. FIFO and PG times differ;
CPU stop is not GPU stop; separate boots do not prove a transition/disposal
producer. Compiled flush_surfaces can discard dirty cached surfaces, but its
runtime causality and hardware pixel loss are NOT proved. Retained2D/DMA
context values remain at both entries; texture/shader/display refs unobserved.
Both loader32byte pins exact in all3; FreeLoader magic2badb002/IF0. No GDB
register/memory writes, both breakpoints removed, guests resumed. One accepted
immutable238 request per guest; no producer halt, fence/readback or ownership.

All3 CPU65 alloc/releases/exposure refusals,3194880 bytes/four joins PASS;
8 retirement rounds retain UNMODELED_BUSY/NO_OWNERSHIP. Normal6006=1 and
dashboard return each. Full clean320dirs/321dirclusters, files6724/6724/6725,
0 errors/orphans;5 hives/protected/startup/policy/history PASS. Extra FreeLoader
file is wbem/logs/wmiadap.log from existing directory capture; no baseline path
absent. Path existence is not byte durability. Application deltas empty; SOLE
Ftdisk49 type1 each, strict/ordinary/physical/backend preservation FALSE.
New stop/quit host closures all exit0/no Kill, exact process verification;
expected monitor reset only after quit preserved. Older forced-close images
unchanged; this is selected-content/full-allocation scope, not all-file or
power-loss/repeated-boot qualification. Private artifacts/disk hashes retained.

Next NEW matched control/preservation at pinned Xromwell entry, genuinely close
producer admission, independently recheck queue/parser/wait/frontend conditions,
fence and bounded exact readback of the3 observed non-overlapping dirty ranges.
Keep callbacks/all other refs retained until separately reviewed retirement;
never force waits/discard aliases/claim ownership or retry an accepted failed
request. If needed trace actual download/invalidation/sync to identify disposal,
not independent phase inference. Use unique fresh owned fixtures/leases and
20GiB guard. No physical access or peer integration; preserve0101/video0093,
0088rollback,immutable0.1.0/all failures. Peer USB eb64acc assisted normal restart
and cold PASS, strict49 FALSE; PCI sharing violation through HID and retained
CSRSS handles traced, no fix established; audio stereo mapping still unverified.

