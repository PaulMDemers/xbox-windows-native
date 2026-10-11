#247 implementation and failed runtime

247 adds a bounded, worker-owned checkpoint behind the verified246 UI gate.
The actual worker snapshots current surface flags, drops FIFO/PG/renderer locks,
selects existing render/display contexts and fences each for at most100ms. It
parks using20ms condition waits that release FIFO, with a five-second request
deadline, then restores original admission on explicit release or expiry.
No caches, surfaces, callbacks, GL buffers/programs/contexts or save-thread
handles are disposed. NativeGPU ownership remains refused.

Build004 is the compiled implementation.001 failed opening root-owned WSL source
before first write;002 selected a nonexistent parent manifest before writes;
003 compiled but failed on a wrong renderer enum and restored every borrowed
source. Its capsule and build001.log are retained.004 uses the actual parent's
CONFIG_DISPLAY_RENDERER_OPENGL and restored all13 borrowed sources. The same
binary is used by the fresh248 host-corrected child; no native driver changed.

Actual compiled worker adapters atO0/O2 with ASan/UBSan each passed3072 paths,
23296 checks. They test lock-busy, BQL, dirty/pending, fence null/timeout/error,
release during capture, lost UI closure and deadline expiry. Every fence adapter
asserts zero actor locks held; successful park releases FIFO and deadline mode
requires25020ms waits. No production state reset/retry exists. These are host
adapters, not actual GL completion. Adapter001 signed-clock mismatch and002
incorrect successful-mode expectation remain failed. Parser proof001 contained
an unmatched negative timestamp replacement; corrected002 passed14 guards.

The sole247/preserve001 runtime CLOSED FAILED. Worker park/two fences succeeded,
but the host reused its reply variable and compared the saved UI report with a
worker report. Bounded cleanup released worker, acknowledged UI reopening and
resumed Windows. Normal shutdown/dashboard/host exit and offline integrity
passed; strict Ftdisk49 remained. The omitted final loader marker prevents full
causal lifecycle qualification: analyze-failed.py preserved that refusal.

worker-partial002.json uses explicitly limited event-only decoding, with no
invented final marker, to qualify the actual worker span: zero current surfaces,
twoGL_CONDITION_SATISFIED fences,251460700ns park. It leaves overallpassedFALSE.
Its UI result is abort-cleanup acknowledgment, not ordinary successful protocol.
Never replay/recollect this closed child or rewrite its trace/audit/matrix.

Natural flush instrumentation records range/buffer/latest flags only for that
existing flush path. It observed zero such surface disposals in this interval;
other invalidation paths remain uninstrumented. This does not preserve latest
dirty GPU bytes at later invalidation. Earlier227 readback is a separate scope.

See248 REPORT for the fresh successful host protocol and final closed audits.
Physical0101/video0093,0088rollback,immutable0.1.0, peer work and actual224/219/211
device policy remain unchanged. No hardwareFTP/deployment/testing occurred.
