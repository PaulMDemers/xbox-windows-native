# CPU-write surface eviction: native pair passes, broader qualification pending

The guarded experimental xemu candidate preserved every expected byte in the
native GPU144 workload. Fresh matched control002 and candidate002 each produced
16 exact full-surface readbacks (19,660,800 bytes), 120,292 volatile CPU stores,
two pbkit lifetimes and a normal reboot to dashboard. Cold E allocation was clean,
all existing E file contents/chains were unchanged, exactly18 expected files were
added, and the complete inherited F partition was unchanged. No Windows or
physical Xbox run occurred.

The sparse lifecycle trace proves the candidate's intended behavior, rather than
only showing that the app returned. During the measured epochs, color was evicted
twice on CPU writes and recreated; depth was evicted three times, including pbkit's
depth initialization between epochs. Both surface types downloaded unread GPU
contents before the first CPU store, then uploaded CPU-modified RAM before the
next GPU partial clear. The full transfer order and geometry are verified by
verify-pair.py. The control retains its cached objects across those epochs.

|Measured surface|Control creates/uploads/downloads|Candidate creates/uploads/downloads|Candidate CPU-write evictions|
|---|---|---|---|
|Color A8R8G8B8|1 / 3 / 8|3 / 3 / 8|2|
|Depth Z24S8|1 / 4 / 8|4 / 4 / 8|3|

These counts end at the post-workload invalidation. Dashboard handoff creates
additional surfaces and is not counted as another application epoch. CPU callback
frequency and timing were not measured. Extra object allocation may impose costs
on workloads that alternate CPU/GPU ownership; no speed improvement is claimed.

Build002 changes only surface.c and renderer.h between complete tracked-source
manifests. It uses the same pinned xemu source, toolchain and pre-existing resource
model patch in both builds. Control SHA256 starts4009c65249dee341; candidate starts
f2dcf1934cf25a076. Full identities are in build002/build.json and the actual runner
instances. Borrowed source files were restored and rehashed after compilation.

The candidate queues eviction only on the vCPU thread. DMA/debugger callback
callers retain their prior behavior. The renderer downloads dirty data and frees
the GL surface; CPU watch removal and TLB flush use the existing deferred exclusive
CPU work. No inline callback-node free, synchronous CPU wait or shared dirty-map
shortcut was introduced. See DESIGN.md and the retained generated patch.

The first build failed Git ownership checks before compilation. The first
successful, unguarded candidate was preserved but never launched after source
review found non-vCPU callback callers. Its control001 fixture was prepared and
never launched. New build002/control002/candidate002 names preserve those facts.
No case was retried or overwritten.

Control launched2026-10-08 16:12:12UTC and returned16:12:39; candidate launched
16:13:48 and returned16:14:11. All runners, observers and cold auditors are closed.
The native pixel/protocol oracle passes its corruption checks;16 recorded-trace
mutations fail as required. Both host stderr logs retain the same unavailable
default audio-device warning; this is not a zero-host-warning claim.

Limits: these are GPU clears, CPU stores/readbacks and partial clears in linear
32-bit surfaces. They do not establish draw-batch, explicit emulator reset,
simultaneous overlapping-watch, Z16 or swizzled coherence. Static review also
requires attention to pending work between draw_begin and draw_end: surface_update
is in draw_begin, while draw_end flushes primitives against existing bindings.
The clear workload does not settle whether eviction may interrupt that interval.
This is a validation target, not a reproduced failure or justification for a
speculative additional patch. The candidate is not ready for upstream submission
or deployment until these contracts and ordinary Windows correctness are tested.

Preserve physical FATX0101/video0093,0088rollback,immutable0.1.0 and all failed
evidence. This work neither resolves nor reclassifies historical physical
corruption or crash-dump issues.
