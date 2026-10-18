# Depth/order control design, before any runtime

New original MIT NT5 sample. No driver/SDK/physical-baseline changes.
Actual EnumDevices must identify exactly one RGB software GUID. Enumerate up to
64 depth formats using that GUID, retain every format and select the first
16/24/32-bit depth-only format. Create owned 64x64 SYSTEMMEMORY ZBUFFER, verify
actual descriptor and attachment pointer, then create device on the owned RGB32
SYSTEMMEMORY target. Explicit LESS, writes enabled, no texture/blend/stencil.

Five independent RGB/Z clears and readbacks: blank clear; far then near; near
then far; near then far with Z disabled; near then far after Z=0 clear with Z
re-enabled. Same projected triangle (8,8),(56,8),(8,56), depths .25/.75 and
colors 40c080/c04080, background102030. Expected near/near/far/blank respectively.
Fixed oracle checks 561 safe interior and2199 exterior pixels per capture;
1336 edge-zone pixels may be only expected foreground/background. X byte ignored.
No runtime-derived expected pixels, exact raster-edge or precision claim.

Explicit scene/attachment/device/depth/target teardown; raw HRESULTs, formats,
vertices, state transitions and bounded live module snapshot. Process exit only
means captures complete. Independent decoder and cold readers establish scope.

Fresh404 reusable PC seed, unique480 child/controller/floppy; no prior runtime
parent/relaunch. Read-only FAT12 preflight, ordinary restart, five-hive/event/
protected-binary audit, independent NTFS-3G extraction, module hash/PE closure.
Only PC-qualified identical binary may proceed to a distinct physical attempt.

API reference: https://learn.microsoft.com/en-us/windows/win32/api/ddraw/nf-ddraw-idirectdrawsurface7-addattachedsurface
Pinned RosBE headers define the actual D3D7 interfaces and flags used.
