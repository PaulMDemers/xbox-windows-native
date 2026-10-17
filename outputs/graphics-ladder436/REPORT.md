# 436: initial graphics sample ladder

User requested small samples to build graphics capabilities before using games
as diagnostics. Public source and instructions are now under
`src/samples/graphics-ladder` and `docs/graphics-samples.md`.

## Implemented scope

- 00: two owned GDI DIBs, an offset rectangle copy, flush, exact source/destination
  capture and cleanup. Optional GDI preview is separate from data verification.
- 01: default/HEL/HAL-only DirectDraw 7 object creation, normal cooperative level,
  hardware/HEL caps and current display-mode inventory. No surface rendering.
- 02: default/HEL system-memory RGB32 surfaces, explicit locks/unlocks, non-waiting
  rectangle blit, full logical-image readback. No primary/video-memory surface,
  DirectDraw window presentation, D3D, mode switch or GPU-ownership claim.

Each pixel control verifies 10,752 RGB pixels / 43,008 canonical capture bytes.
The independent Python implementation verifies the source and untouched
destination border as well as the copied rectangle. X bytes are normalized;
surface pitch padding and allocation guards are outside this capture scope.

## Builds and retained failures

Private capsules are `E:/xwn436/build001` through `build004`. Compiler is the
reviewed RosBE i686 GCC, SHA-256
`8ab0685d97b322aad3c37fd362b26fa5b9408ff6dd55a536c0a2d48de1c22b18`.
Shared SDK/driver sources were not modified. Builds held the host build lease
and checked the 20 GiB projected reserve on E and the WSL backing volume.

1. Build001 failed compilation: local helper `boolean` collided with an SDK
   typedef. Source, log and receipt retained; never executed.
2. Build002 renamed that helper, compiled with no warnings, and added header
   dependency hashes. Original sample included the HAL-only system-memory path.
3. Build003 added an early argument refusal for that unqualified path. It was
   compiled, but never executed.
4. Build004 has byte-identical native source to build003; the builder additionally
   copies and hashes the batch runner. This is the current executable:
   `E:/xwn436/build004/ladder.exe`, 23,985 bytes, SHA-256
   `09d355d8e55081433b62f94a2203cfa56bb23c4e6181f07f9b5087c7b6f3d050`.

The current build has no warnings, PE32/i386 console subsystem 5.0, no CRT or
static DirectDraw dependency. All 43 imports match actual exports in three
pinned owned NT5 DLLs retained by 425. The build records 151 header hashes.
This checks imports, not actual NT5 execution or every runtime dependency.

The local rename script initially asserted the wrong occurrence count (13
instead of the observed 10); it refused before editing. A first import-tool
lookup used the default Python path without pefile; the existing private package
path was then used. Neither caused a build or runtime claim.

## Actual host observations

These are Windows 11 development-PC controls with hidden windows and a 30-second
external process watchdog. `GetVersionEx` reports the compatibility version 6.2;
the controller records the actual host platform separately. No timeout occurred.

Host001, build002:

- GDI pixel control, all three DirectDraw inventories, and default/HEL pixel
  controls completed and passed independent checking.
- Rung 02 HAL-only exited `0xC0000005`. The last returned operation was display
  mode query; the first `CreateSurface` return was never logged. No pixels or
  completed terminal record were produced. This localizes the observed boundary,
  not the responsible module or root cause. No stack trace or NT5 reproduction.
- The original checker rejected the incomplete report. `oracle001.py` reconstructs
  its exact executed bytes and matches the hash in `host001.json`. Failure intact.

Host002, build004:

- All six allowed cases completed: 00/default, 01/default/HEL/HAL, 02/default/HEL.
- All three pixel cases independently match all 43,008 captured bytes each.
- 02/HAL is rejected with exit 2 before report creation or DirectDraw loading.
  This is an explicit excluded combination, not a corrected HAL rendering pass.
- The actual batch runner was exercised separately in controls001; it recorded
  the exit and captures, and refused reuse without changing any existing result.

All owned processes exited. No NT5 guest was prepared/launched, no Xbox accessed,
no display mode/driver/startup change, no firmware or system DLL copied.

## Verification and next step

Five public verifier tests pass, including missing/duplicate/truncated records,
API failures, external crash exits, pitch/layout refusals, capture corruption,
copy boundaries and untouched pixels. Separately, 287 mutations of actual host
evidence were rejected in controls001. Historical HAL-only failure remains
rejected by the exact old checker. Original captures are unchanged and rehashed.

Next: fresh owned Windows 2000 PC runtime control of these exact samples, then
an independently recorded Xbox run. Rung 03 will add primary-surface/clipper
presentation with GDI coexistence checks. Later palette/sprite, lifecycle and
D3D rungs are documented plans, not implemented successes. 1080i remains paused;
the existing 720p installation and all old failures remain untouched.
