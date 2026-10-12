# Review a narrow admission contract, not a count exception

276emu001 CLOSED. Read REPORT, source-review and inventory-analysis first.
Do not repeat the solved callback identification run or old275/272 cases.
No narrow release or full four-generation unchanged reuse control has passed.

The zero-count contract is too restrictive for this standalone active GL
workload, but do NOT simply remove it or allow count4. All actual callbacks
have renderer surface owners; two also have captured native allocation owners,
two unbound dirty surfaces do not. Unknown native ownership remains explicit.

Before implementation review a NEW opt-in contract for ONLY four-texture
observation/narrow-unit work, retaining every existing surface/callback. It
must establish a complete bijection between the acknowledged CPU inventory
and locked surface graph: callback identity, relative/absolute range, region,
function, opaque, SurfaceBinding identity and actual allocation bounds. Reject
duplicates, unknown functions/regions/owners, missing callbacks or extra graph
edges, overflow, pending work and any overlap with the four attested owned
texture ranges. Require two acknowledged CPU boundaries at each transaction,
stable complete tuples/owner epochs and actual context/fence acknowledgments.
Do not dereference saved callback pointers or infer queued completion from
empty work lists. Keep dirty surfaces and their registered callbacks intact;
no downloads, disposal, refcount assignment, pending-bit clearing or global
finalizer/switch/reset. Model ABA and lifetime mutations, not just count changes.

Determine whether the unbound dirty surfaces can safely remain outside this
narrow transaction. If proving guest allocation provenance is required, capture
actual pb_FrameBuffersAddr/count/pitch, pb_FBAddr array and pb_EXAddr/size from
pinned loaded SDK instructions in a NEW explicit observation; do not infer
ownership from addresses or label them firmware without evidence. No repeated
boot for luck. This must never become a whole-backend/native GPU grant.

Only after a reviewed tested contract may a NEW exact276 child run the actual
unchanged four-generation no-release control with independent source/key/RGBA/
framebuffer bytes, complete273 accounting and initial/end owner graphs. Keep
every old zero-count refusal and strict disk failure unchanged. Only qualifying
control supports later separate matched268 release. Native Windows PTE/cache
aliases/deferred release remain separate before a16x8 copy.

Use bounded atomic writer and preserve per-page manifests. Current compiled
renderer E:/Codex-archive/xbox-windows-native/callback276-build003/xemu-callback276.exe
SHA7a19d5c3c3125b522cd7ca8699b1b6a78356f6b6976732a2c00de01be40de502.
All processes closed including builds59297/93288/39349 and runtime40686.
Physical demo unchanged.20GiB guard remains; new portable/scratch onE.
