# Optimize surface watches without losing CPU/GPU coherence

The runtime evidence now identifies a retained prelaunch depth surface, not a
different Windows copy routine. Its GPU data was downloaded during handoff, but
the CPU-access watch remained. The lower selected copy enters that watch once per
four-byte store. No GPU transfer occurs during those selected uploads. This is a
specific optimization target, not a qualified patch or a hardware performance fix.

## Existing contracts to preserve

Pinned OpenGL surface.c registers a watch when it creates a surface and removes
it on invalidation. Its CPU callback locks PGRAPH, walks cached surfaces, downloads
dirty GPU data when necessary, and marks CPU writes as pending GPU uploads.
The memory callback layer installs/removes watches asynchronously on the CPU and
flushes translated page entries. These are synchronization operations, not merely
list edits. A callback can already be in progress when removal is requested.

Surface ageing occurs during GPU surface updates. A CPU-rendered desktop does not
necessarily advance this lifecycle. Retention therefore does not by itself prove
that Windows failed to issue a required hardware reset. No reset-write capture was
performed in this run.

The source already has a non-TCG dirty-bitmap path in update_surface_part and an
eager-download fallback after GPU writes. It must not simply be selected for TCG:
that would alter GPU synchronization and may move the cost to every rendered frame.
DIRTY_MEMORY_NV2A is also consumed by vertex-buffer code, so reusing that client
for a new surface coherency policy requires proof against competing consumers.

## Candidate policy to investigate

Distinguish GPU-newer, synchronized, and CPU-newer contents. GPU-newer data requires
a read/write watch so CPU access obtains the correct bytes. Synchronized data
requires tracking the first CPU write. Once CPU data is authoritative and the
surface is already pending upload, repeated stores should not require the same
full callback work until the GPU next consumes or modifies the surface.

Do not implement that policy with an unchecked early return, immediate watch free,
or a global callback disable. First design the CPU-thread removal/rearm handshake,
PGRAPH lock ownership and in-flight callback lifetime. Re-arm before the next GPU
operation requires it. Preserve overlapping ranges, failed/zero-size surfaces,
invalidation, renderer reset and normal shutdown. A deferred eviction alternative
must preserve dirty contents and rebuild bound surfaces correctly; OpenGL deletion
cannot simply be called on the CPU thread without the renderer context.

## Required discriminator and validation

Use a small owned GPU/CPU synchronization workload in a fresh fixture before a
performance candidate: GPU writes then CPU reads; partial CPU writes preserving
other GPU-written pixels; repeated CPU stores; GPU reuse of those CPU changes;
another GPU write followed by another CPU read; invalidation/reset and shutdown.
Compare exact bytes, not only the visible frame. Exercise color and depth surfaces
and the asynchronous watch lifecycle. Keep data/control paths identical between
matched baseline and candidate, with ordinary cold NT5 regression afterward.

Only a candidate that preserves those transitions should enter the existing
ordinary position/transfer and window-movement benchmarks under exclusive leases.
Instrumentation timings remain excluded. Physical Windows speed needs its own
hardware validation after emulator measurement artifacts are understood.
