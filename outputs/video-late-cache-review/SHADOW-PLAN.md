# Next prototype: RAM drawing surface, unchanged scanout

This plan is not an implemented driver or a speed claim. Keep Microsoft framebuf
as the existing rollback. Preserve shared0106 bootvid/miniport, FATX0103,
HAL0102, NVNet0104, ATAPI0105, mode1024x576x32 and all event/cold gates.
No physical deployment belongs to this step.

## First isolate display-driver compatibility

Start a NEW unique kit and fresh reconstructed source tree from the pinned
framebuf source lead in `shadow-contract.json`; do not mutate the prior build.
The ReactOS reconstruction is index tree53e9aedc58152d03116c00579185000483379837
over upstream HEADafc0127e8f937ab68503d715d948844973756aa1, not a committed
checkout of that tree. Pin the exact tree/files and full source diff.

Build a renamed display DLL with its own explicit NT5 import review. Validate
the simple direct-framebuffer path against the current Microsoft framebuf
control in a fresh fixture before adding shadow behavior. Check allocation
failure unwind, mapped address release, mode assert/disable, pointer handling,
caps and32-bit masks. The source's early failure paths after mapping need review;
do not treat upstream source as already qualified for this provider.

This separates new-DDI compatibility failures from shadow coherence failures.
Changing a test fixture's display-driver selection is part of this isolated
experiment; keep service/device policy otherwise fixed and preserve its parent.
32 required Eng exports and all source-referenced Eng names exist in the pinned
NT5 win32k. That is necessary but not proof of ABI or semantics.

## Surface ownership

Use a driver-managed primary surface and a private engine bitmap in ordinary
RAM. At the current mode the pixel storage is2,359,296 bytes (2.25MiB), before
object/allocation overhead. Require complete allocation before publishing the
surface, overflow/stride bounds and reverse-order failure cleanup. If allocation
fails, use an explicitly designed direct path or fail creation cleanly; do not
publish a half-initialized surface or silently mix modes after creation.

The private bitmap is authoritative while desktop rendering is active. Replace
primary source/destination surface arguments with the corresponding private
bitmap for software rendering, preserving source/destination identity for
overlap. Other application bitmaps remain unchanged. Successful destination
operations synchronously upload their affected visible region through the
permanent UC pointer. Readback uses the authoritative bitmap and must not
recursively reenter the display hook.

An ordinary engine bitmap as the *primary* surface is insufficient: unhooked
engine writes could bypass upload. A managed surface supplies an explicit
boundary, but actual NT5 fallback behavior still needs runtime validation.
[EngCreateDeviceSurface](https://learn.microsoft.com/en-us/windows/win32/api/winddi/nf-winddi-engcreatedevicesurface),
[EngAssociateSurface](https://learn.microsoft.com/en-us/windows/win32/api/winddi/nf-winddi-engassociatesurface).

## Coverage that must exist before promotion

- CopyBits and BitBlt: both directions of overlap, primary as source, primary
  as destination, complex clipping, masks, translations, non-copy ROPs and
  destination bounds. Do not dereference optional inputs unused by the ROP.
  Use engine fallback on exposed private bitmaps with valid surface lifetimes.
  [DrvBitBlt](https://learn.microsoft.com/en-us/windows/win32/api/winddi/nf-winddi-drvbitblt).
- Text, line, paint, stroke/fill paths, stretched/transformed copies, alpha,
  gradient and transparency: implement hooks or prove the exact engine fallback
  routes through a covered upload path. Count actual callbacks; export presence
  alone does not establish coverage. Conservative full-visible upload can be a
  correctness fallback when dirty bounds are uncertain, not a speed result.
- Pointer hide/show/move and screen capture: validate software cursor exclusion
  and that any engine cursor rendering reaches the upload boundary. Avoid
  holding a nonrecursive drawing lock across an engine call that can reenter
  a hooked callback. Pin the actual call behavior before choosing exclusion.
- Mode assert/re-enable, disable and screen saves: define when the shadow is
  initialized, preserved or discarded; do not upload stale desktop contents
  after bootvid reclaims the display. Crash rendering must depend only on the
  permanent UC mapping, never a pageable bitmap, semaphore or successful upload.
- DirectDraw, OpenGL and optional DDI paths: do not inherit claims or advertise
  direct framebuffer access that bypasses shadow coherence. The user's earlier
  Pinball/OpenGL observations concern the old driver. New behavior needs tests.

DrvSynchronize is a before-access synchronization callback, not an assumed
after-render upload notification. Do not use that alone to declare coherence.
[DrvSynchronize](https://learn.microsoft.com/en-us/windows/win32/api/winddi/nf-winddi-drvsynchronize).

## Measurements and gates

Retain the54-case/162-stage pixel workload and normal restart/full allocation/
five-hive/protected-hash/configuration/pagefile/strict-event checks. Extend the
probe for the paths above; actual callback counts must demonstrate they ran.
Compare the shadow and real mapped scanout independently after synchronization:
GDI readback from the shadow alone cannot prove visible pixels are correct.
Also capture the rendered screen, and preserve every failed case.

Use matched direct/shadow builds, rotated measurements and reported uploaded
bytes/rectangles. A full-frame upload per call can be correct but slow. The old
emulator RAM-overlap-plus-upload measurements were not a convincing speed win;
do not promise physical improvement from xemu timings. Hold cache type, mode,
physical reservation, device policy and storage/network binaries fixed.

Require ordinary correctness before a new bounded alias/coherence diagnostic,
then a sacrificial crash-render/dump test. Physical measurements come later as
a separately authorized and reversible trial. Do not build if actual C: free
space fails the unchanged20GiB guard. No previous guest/crash child may be reused.
