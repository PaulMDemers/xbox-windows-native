# Open-primitive eviction regression reproduced and fixed

The first guarded CPU-write eviction candidate (build002) dropped an entire
64x64 drawn rectangle when a CPU store occurred after GPU BEGIN. The same app on
the matched control produced the correct image. Build003 preserves bindings while
a primitive is open and passes the matched draw cases. This is an emulator cache
lifetime fix; no Windows driver or physical-console change was made.

The new native 145 app uses a pinned two-instruction passthrough vertex shader and
constant-magenta triangles covering x=128..191, y=96..159. Its independent oracle
checks the whole 640×480, 32-bit surface. Four cases issue no CPU store, a store before
BEGIN, a store after BEGIN, or a store after queued DRAW_ARRAYS but before END.
The single volatile CPU store writes the existing background value at (3,5), outside
the drawn rectangle. This avoids racing changes to pixels the GPU writes. Bounded
pb_busy checks confirm submitted commands have been consumed; guest logs record
the ordering and normal reboot. The expected image was frozen before any launch.

|Attempt|Control|Eviction candidate|Interpretation|
|---|---|---|---|
|145|Four exact images, strictFAIL|Never prepared/launched|Broad method trace exceeded unchanged 16 MiB bound; runner stopped before observed dashboard return|
|146,build002|Four exact images, coldPASS|Cases 0/1 exact; cases 2/3 each missing 4,096 pixels, coldFAIL|Reproduced binding-lifetime regression; protocol and disk integrity checks still passed|
|147,build003|Four exact images, coldPASS|Four exact images, coldPASS|Corrected lifetime; normal return and exact lifecycle sequence verified|
|148,build003,native144app|16 exact color/depth images|16 exact color/depth images|Earlier unread-GPU/CPU-store coherence regression retained, with eviction still exercised|

In the failing candidate, CPU-write eviction frees/unbinds the current cached GL
surface. draw_begin previously called surface_update, but draw_end later flushes
queued primitives against the existing bindings. Removing that binding between
the two makes the draw disappear. The native test's normal command sequence and
readbacks discriminate this failure; no debugger changes or forced completion
were used. The failed 146 candidate remains unqualified despite its clean disk.

Build003 changes only surface.c relative to build002's candidate. It checks
PRIM_TYPE_INVALID under PGRAPH at request time, and checks it again in the renderer
worker before invalidation. BEGIN could occur between these points. The worker
consumes/clears the pending eviction flag and falls back to the original
upload/download path if a primitive is active. It does not retain a stale eviction
request to run later. Deferred CPU-watch removal, renderer-owned GL deletion and
the vCPU-only restriction remain unchanged. Shared SDK and borrowed xemu sources
were restored/verified. Full manifests and generated patch are in
../xemu-cpu-surface-evict/build003.

147's exact trace sequence contains one CPU-write eviction before BEGIN and no
eviction for the two open-primitive stores. All four outputs contain exactly 4,096
magenta pixels and the expected background everywhere else. Eleven recorded trace
mutations are rejected; pixel/protocol tests reject missing, short, changed-inside,
changed-outside and missing-rectangle output. 148 reuses the prior unchanged native
app/oracle:16 files, 19,660,800 bytes and 120,292 stores per run. Its exact transfer
sequence still includes two color and three depth CPU-write evictions.

All completed pairs return normally and have clean E allocation, exact newly
created output files, unchanged existing E files/chains, and no top-overlay data
anywhere in F. These native tests do not boot Windows. The first 145 trace-overflow
failure and146’s lost-draw images remain immutable evidence. Full command trace
was removed in fresh 146+, not allowed a larger limit or reclassified as passing.
The sparse trace and guest completion record establish these tested sequences;
the very short request-to-worker BEGIN race is reviewed but not forcibly scheduled.

Remaining qualification: overlapping surface ranges, explicit emulator reset,
Z16/swizzled surfaces, broader drawing patterns and matched ordinary Windows
correctness/performance. The optimization is experimental and no speed gain or
physical suitability is claimed. Host no-default-audio-device and existing SDK
compiler warnings remain recorded; no zero-warning build claim is made.
