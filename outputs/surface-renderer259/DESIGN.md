#259 renderer protocol — implementation in progress, no guest launch

The physical audio004/video118/shared158/FATX0101 demo and its verified256
file-level recovery snapshot stay unchanged. This kit targets a NEW sacrificial
emulator child of the **pre-execution258 source**, not its used disk. No child
has been prepared or launched. Closed257/258 runs must not be repeated.

The unchanged258 demand driver holds one16KiB allocation and its FileObject
until reboot. New259 probe uses its existing IOCTLs and cannot free the arena.
The compiled native probe deliberately fails without the renderer intervention;
do not run it as an ordinary baseline. It writes a new C:\xwnpat259\result.log,
creates the absent XwnPattern258 service, and refuses a stale service/result.

## Five stopped checkpoints

At each actual exported X259Checkpoint entry, the stack holds cdecl stage,
Reply pointer and file HANDLE. The preferred image base is only a lead. Pin
actual mapped PE/code/process before accepting a breakpoint. Resolve actual
loaded driver state and owning FileObject/generation; independently translate
all four pages. Never reuse258's old physical address. The admission core's
booleans and completeness bits are NOT substitutes for this runtime evidence.

1. Prove seed0 in the arena and full reference disjointness. Create only the
   diagnostic13x11 BGRA8/pitch64 surface at arena+4096, upload pattern0 into GL
   without writing guest RAM, and age only that surface by five frames. Refuse
   if any other surface is old enough to be evicted. Call actual
   surface_evict_old; prove common deletion and actual callback removal/free.
   Resume for a real driver read and exact16KiB check.
2. Create a fresh dirty surface with pattern1. Observe actual CPU callback
   insertion before executing the next guest read. Release the worker park
   before resuming: that worker must be able to service the blocked read.
   Require a CPU-thread callback while dirty, actual download and exact bytes.
3. Validate the same surface, callback generation and now-clean flags. Upload
   pattern2 to that texture and mark dirty, without writing guest RAM. Resume
   the actual driver CPU store of seed1. Require dirty download/eviction while
   the store is blocked, followed by the resumed CPU store winning.
4. Require actual callback unlink/free and no remaining arena references.
   Check the full CPU seed1 buffer, then resume a second guest read to detect
   any late stale download. No host memcpy can satisfy a callback gate.
5. Check final four reads/one write, complete teardown and normal closure. The
   driver still holds the allocation until reboot; the probe quarantines it.

Do not read an arena through a debugger access path while a dirty test surface
is waiting for the guest: a host-origin access must not consume the dirty
download and masquerade as CPU coverage. Attribute callbacks to the actual CPU
thread and pair them with stages/generation/range and guest results.

## Source-derived bridge requirements

Sixteen files are copied byte-exact from the compiled257 source closure. Both
the original snapshot and runtime bridge still need a complete reference audit:

- Surface list, texture and palette ranges, vertex-cache ranges, scanout and
  overlay, plus the actual CPU callback list. Unknown owners/ranges refuse.
- Vertex upload's gl_memory_buffer is a GL COPY of RAM, not a host pointer
  alias. Its presence alone is not full-range guest ownership; however the
  collector must still establish no active vertex fetch and account for vertex
  bindings/cache. Do not simply exclude the entire family as harmless.
- Report queue, active primitive, producer state, frontend loans, both context
  fences, pending downloads and CPU work must be checked in a coherent epoch.
- An empty CPU work_list is NOT a barrier: process_queued_cpu_work removes an
  item before executing it. The callback inventory must be captured by an
  acknowledged CPU-exclusive job, with late enqueue/epoch rules, not a host
  peek under work_mutex. Pending insertion/removal is distinct from completion.

The reviewed247 worker and246 frontend admissions are one-shot. The probe needs
multiple worker epochs while the frontend stays closed. Do not reset their
state structures opportunistically or reuse a previous ready flag. A new,
bounded sequenced bridge must acknowledge each CPU/worker epoch, restore
producer admission, and quarantine the sacrificial process after any uncertain
teardown. No QOM command or PFIFO caller is installed by the current build.

## Internal renderer implementation

renderer-stage.c implements four internal stages against the actual257 surface
functions. It is deliberately unreachable until the bridge above is implemented
and reviewed. The age case uses a private FBO so temporary attachments cannot
modify the guest FBO. It saves/restores and rereads texture/FBO/PBO and pixel
store bindings, clears pack/unpack offsets for the diagnostic, and uses actual
surface callbacks/download/invalidation. It never advances global frame time.
Any partial publication failure requires process quarantine; it does not free a
published surface speculatively. Return0 alone does NOT prove callback teardown.

admission.c rejects missing coverage, count disagreement, unknown/duplicate
identities, invalid/wrapping/overlapping ranges, noncontiguous pages and another
surface's eligible age. This is pure checked logic; its synthetic tests are not
live ownership evidence. The caller owns locks and supplies non-null internal
objects; the future command bridge must validate inputs before this C API.

The independent guest expectations cover65536 bytes across four full readbacks,
including each572-byte pixel region and15812 padding/guard bytes. Pattern0 and
post-store expectations exactly match258's separate Python oracle. Ten negative
controls reject missing intervention, stale texture/store, padding/guard damage,
wrong pixels, pitch, row direction and red/blue swap. These are host controls,
not executed GL preservation results.

Require unique frozen fixture, bounded host/guest stages, full callback/GL
teardown, cold allocation/hives/protected hashes and strict event review after
runtime integration. Retain the inherited Ft49 strict failure. No native GPU,
speedup, physical test or new video-mode claim follows from compilation.
