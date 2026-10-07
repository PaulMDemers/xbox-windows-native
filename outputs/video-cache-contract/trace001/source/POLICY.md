# Coordinated cache policy proposal and decision gates

Objective: improve CPU framebuffer writes without conflicting aliases, exposing
reserved pages to MM, losing boot/error/shutdown display or changing GPU MMIO.

Current owners are the early loader/HAL display aliases, retained bootvid direct
RAM including its hidden backbuffer, and the desktop GPU aperture. Bootvid cannot
simply drop its mapping when the desktop starts: late shutdown may lose aperture
access. Both its visible pixels and hidden indexed buffer have read/write users.

The preferred first candidate to investigate is a fixed boot-time policy using
the same reserved-RAM physical range for bootvid and desktop, with one consistent
cache type across the full4MiB. Keeping both mappings UC is the control. WC is
only a candidate if the installed NT5 APIs can actually establish it and the
earlier loader/HAL aliases are either consistently typed or retired before the
first WC access. No desktop-only P6CACHE edit, WB framebuffer mapping, live PTE
rewrite or ad hoc PAT/MTRR reprogramming is proposed.

## Required decisions before a speed build

1. Establish actual NT5 mapping calls/arguments and effective policy, including
   MTRR treatment of RAM versus aperture. Current diagnostic covers baseline
   requests only. It cannot prove that a future MmWriteCombined request succeeds.
2. Resolve the early handoff: identify when loader/HAL aliases stop being used
   and are removed, relative to bootvid's first map. Static disappearance by the
   desktop is insufficient. If consistent early WC requires changing PAT while
   other mappings are live, reject that implementation and choose a different
   contract; do not make an unreviewed global cache transition.
3. Specify how NT5 cache attribute tracking treats reserved physical RAM and
   multiple MmMapIoSpace views. Reject silent UC fallback as proof of WC. New
   mapping failures must retain a known safe boot path; no partially converted
   policy followed by creation of a conflicting UC alias.
4. Define ordering at the producer/consumer boundary. CPU stores, readback,
   software-pointer/overlap reads and device scanout are separate consumers.
   A miniport flag cannot insert fences into Microsoft's unmodified drawing
   engine. Inspect actual engine/API ordering before accepting that path. Do not
   infer that return from REP MOVSD drains WC buffers. Bootvid also needs explicit
   ordering at completion of its drawing operations if its mapping changes.
5. Preserve4MiB permanent reservation, hidden bootvid backbuffer, mode/pitch,
   aperture-loss shutdown path, consumer quiescence and mapping references.
   The0096 ownership helper is a bounded prototype, not proven generic PnP stop,
   surprise removal and restart support.

If these gates cannot be met cleanly, a project-owned display driver with a
cached shadow surface and explicitly ordered dirty copies is the alternative.
It costs RAM and requires all raster, clipping, cursor, readback and overlap
operations plus independent scanout validation. GPU acceleration remains a
separate ownership/synchronization project. None is justified by flag changes
alone or by xemu speed measurements.

Any implementation gets fresh matched UC control/candidate builds and source
review, bounded map/unmap/lifetime checks, ordinary54-case/162-stage drawing,
independent scanout captures, clean normal shutdown and cold/event gates. Keep
the physical0093 rollback and known working mode. Hardware cache correctness
and real dragging performance require a later separately staged physical test.

References: Intel system programming manual cache/PAT/MTRR and ordering rules
(https://www.intel.com/content/dam/support/us/en/documents/processors/pentium4/sb/25366821.pdf);
Microsoft VideoPortMapMemory and MmMapIoSpace contracts. Current API behavior
must be established against the installed owned NT5 binaries, not modern or
ReactOS implementations.
