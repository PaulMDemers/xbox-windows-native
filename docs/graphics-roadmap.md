# Next milestone: classic Windows games and Direct3D

The next graphics goal is to run the **original RollerCoaster Tycoon and The
Sims** on native Windows 2000 on a 64 MiB Xbox: playable sessions with working
input, sound and persistent saves. These are compatibility targets, not current
support claims. Begin at the working 720p desktop configuration; the separate
[1080i investigation](1080i-investigation.md) remains paused.

The starting assumption is RollerCoaster Tycoon (1999) and The Sims (2000), not
their sequels, remasters or modern reissues. Record the user's exact disc edition,
patch, language and expansion set before testing. EA's modern Sims Legacy
Collection has different Windows and graphics requirements and is not the target.
See [EA's requirements](https://help.ea.com/en/articles/the-sims/the-sims-legacy-collection/the-sims-legacy-minimum-requirements/).

## Where the project stands

The desktop uses CPU-rendered GDI and a private RAM primary surface copied to
the framebuffer. The maintained display driver's
[DrvEnableDirectDraw](../src/drivers/video/display/win32ss/drivers/displays/framebuf/enable.c)
clears its DirectDraw callback tables and returns `FALSE`: its comment explicitly
prohibits direct access that bypasses the private primary. There is no installed
native GPU acceleration or qualified Direct3D driver. The first actual Xbox
samples pass default/HEL DirectDraw 7 system-memory blits and independent pixel
readbacks with this driver unchanged. Primary-surface presentation and D3D
rendering remain untested; see the [sample results](graphics-samples.md).

DirectX is a family of APIs. A game's DirectX requirement does not by itself mean
it requires accelerated Direct3D. Chris Sawyer's own FAQ identifies DirectX 5
and specifically DirectInput as an original RollerCoaster Tycoon dependency,
and notes Windows 2000 compatibility may require the official patch. Identify
the actual graphics calls before choosing the driver work.
[Compatibility FAQ](https://www.chrissawyergames.com/faq1.htm),
[development tools](https://www.chrissawyergames.com/faq3.htm).

Windows 2000 uses the NT5 display-driver interfaces. Microsoft's documented
DirectDraw/Direct3D 7 path goes through GDI to the display driver; Direct3D 8
has a different kernel interaction. A modern WDDM driver is not the implementation
target. Pick the API version from the selected software and tested runtime,
rather than declaring all Direct3D versions supported.
[Microsoft's legacy graphics interface overview](https://learn.microsoft.com/en-us/windows/win32/devnotes/-dxgkernel-low-level-client-support).

## Work in order

Implementation starts with the [graphics sample ladder](graphics-samples.md):
small owned programs with explicit results, progressing from GDI and DirectDraw
surfaces to D3D triangles, textures and game-like scenes. Rungs 00–02 now have
passing scoped controls on the modern host, Windows 2000 PC and physical Xbox.
Rung 03 adds windowed presentation and coexistence with GDI before later D3D work.

| Stage | Work | Evidence needed to advance |
|---|---|---|
| 1. Establish game baselines | Inspect exact executable/import identities and supplied requirements; install and play each owned edition on a disposable Windows 2000 PC control | Recorded game/patch/runtime versions, settings, APIs observed and a save/reload control |
| 2. Measure the Xbox compatibility gap | Run small owned DirectDraw, input and audio probes, then the same game editions on a private Xbox test installation | Actual device/capability enumeration, API failures and timings; software emulation and hardware paths reported separately |
| 3. Make the required 2D path correct | Implement only missing surface, palette, clipping, color-key, blit, lock and presentation behavior that the probes/games require | Independent pixel checks, correct GDI interaction, repeated lost-surface recovery and no save/filesystem regressions |
| 4. Add the selected legacy Direct3D interface | Choose a required version and renderer strategy; build context, texture, depth, blend and presentation tests before game deployment | Truthful capabilities, reference images, bounded failures, resource lifetime/memory checks and a real application using the interface |
| 5. Qualify the games | Exercise realistic park/household play, input, sound, dialogs, saving and normal shutdown/reload on physical hardware | Repeatable sessions meeting the acceptance checklist below, with hardware and performance limits documented |

Stages 1–3 may make the requested games playable without native 3D acceleration.
That would meet their compatibility target; it would not qualify a Direct3D
driver. Conversely, creating a Direct3D device or drawing one triangle does not
meet the game milestone. Keep both results visible.

### First probes and implementation boundaries

Start with windowed operation, then test full screen only in modes the matched
boot profile actually supports. Enumerate DirectDraw's default, emulated and
hardware behavior separately. Test 8-bit palettes and 16/32-bit surfaces where
supported, including pitch, clipping, locks, color keys, copies, window movement,
activation and restore. Compare the resulting pixels against an independent
oracle. Unsupported modes and operations must return honest failures.

The first source review should trace GDI's private primary and presentation path
alongside DirectDraw surface ownership. Changing `DrvEnableDirectDraw` to return
`TRUE`, or exposing the framebuffer without a coherent surface model, is not a
fix. Any new direct surface access must remain consistent with GDI drawing and
window moves. Microsoft's [DirectDraw API reference](https://learn.microsoft.com/en-us/windows/win32/api/_directdraw/)
defines the application-facing operations to probe.

Keep the Windows kernel, DirectX runtime, display driver and game patches pinned
for each comparison. Test runtime changes separately; do not replace arbitrary
system DLLs until a game starts. Keep original installation media and rollback
private. No game assets, Windows runtime binaries or preinstalled user hives
belong in the public source or utilities package.

### Native GPU acceleration is a separate engineering gate

If the selected D3D path needs native NV2A acceleration, establish Windows-owned
channels/objects, safe memory and cache mappings, command submission, completion,
resource retirement and bounded fault recovery first. Preserve the CPU desktop
and storage/input operation. Standalone nxdk initialization and xemu's host
OpenGL ownership experiments do not grant GPU ownership to the Windows driver.

Do not use firmware-owned channels, a global renderer reset or fabricated
completion as shortcuts. Start with an owned offscreen operation and independent
readback before display integration. Track memory use on the 64 MiB machine;
software compatibility and hardware acceleration need distinct measurements.

## Game acceptance checklist

Proposed first acceptance target for **each exact game edition**:

- Install and launch normally, with recorded prerequisites and no silent file
  exclusions or unsupported capability claims.
- At least 30 minutes of representative park or household play, with usable
  menus, scrolling, building/placement and mouse/keyboard controls.
- Correct visible rendering and audible game sound; report stalls, corruption
  and timing measurements alongside the human assessment. Set a frame-time
  target after measuring the PC control and the first Xbox baseline.
- Save a new game, exit, restart Windows normally, reload it and continue play.
  Verify the save contents and report new event/filesystem failures separately.
- Repeat on the original 64 MiB test console before expanding to other revisions.

| Target | Current status | Next evidence |
|---|---|---|
| Original RollerCoaster Tycoon | Not tested by this milestone | Exact edition/patch, Windows 2000 PC control and actual API dependencies |
| Original The Sims | Not tested by this milestone | Exact edition/expansions, Windows 2000 PC control and actual API dependencies |
| Legacy Direct3D support | Planned; no qualified native implementation | Selected API/runtime, owned probes and reviewed driver design |
| Native NV2A acceleration | Unimplemented in the working demo | Windows ownership, submission, synchronization and lifetime proof |

## Installation work remains part of this goal

The [build-to-boot guide](build-to-boot.md) makes the current preparation and copy
steps explicit. A portable registry converter, lossless storage for Windows'
long names, and physical install/restore qualification still need implementation.
The current FATX RSA/DPAPI failures cannot be waved away because a game reaches
its title screen. Use private disposable test installations, preserve failures,
and keep game compatibility separate from the general clean-install release gate.
