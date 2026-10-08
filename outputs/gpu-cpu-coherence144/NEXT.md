# Design safe watch detachment/rearming, then validate a candidate

Read REPORT.md, closure.json, control001/audit.json, lifecycle-verification.json,
recorded-lifecycle-tests.json, and ../video-surface-history/OPTIMIZATION-DESIGN.md.
All142/143/144 attempts are closed. Never relaunch or recollect them. No next
fixture or xemu candidate exists.

The existing baseline now passes exact read-first and write-first color/Z24S8
coherence tests.144's first CPU store must download unread GPU data before partial
overwrite. Subsequent GPU use must upload the CPU data and reestablish protection
before another GPU write/read cycle. Those are concrete candidate correctness gates.

Next inspect and specify ownership around memory_access_callback_remove/add,
async_safe_run_on_cpu, synchronized TLB flushes, the PGRAPH mutex and renderer
context. Account for a callback already executing, queued removals, invalidation
before removal completes, and a GPU operation arriving before rearm completes.
Do not immediately free a SurfaceBinding from a CPU callback or wait on a CPU job
while holding a lock the CPU callback needs. DIRTY_MEMORY_NV2A has vertex consumers;
do not silently repurpose it as an exclusive surface bitmap.

Before accepting a patch, add focused explicit-reset and overlapping-range/reuse
coverage as warranted by the actual state-machine design. These native runs use
linear32-bit surfaces; they do not qualify Z16, swizzled formats or all reset paths.
Use fresh cases and preserve143/144 as immutable controls. The observed pbkit
reinitialization retained surfaces; it must not be relabeled as an emulator reset.

Only then measure a matched ordinary candidate using the existing Windows45-case
correctness/cold audit and exclusive position/transfer/window benchmarks. No
debugger or sparse-trace timing qualifies as a speedup. Do not change guest paging
flags, force a GPU reset, disable callbacks globally or relocate framebuffers for
a favorable result. Physical Windows performance remains separately untested.

Preserve physical0101/video0093,0088rollback, immutable0.1.0 and all failed evidence.
No physical FTP/deployment/testing is authorized by this emulator continuation.
C free remains above the unchanged20GiB guard; offload20261008c retained verified
closed standalone runs at their original paths through directory junctions.
