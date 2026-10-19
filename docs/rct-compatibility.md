# RollerCoaster Tycoon compatibility tests

All three supplied disc images installed and reached a rendered Forest Frontiers
park on separate Windows 2000 PC controls on October 19, 2026. Deluxe and the
later Atari disc also saved and reloaded a park in the same session. These are
**PC control results**. A subsequent watched native Xbox Deluxe run also reached
the title/menu and rendered Forest Frontiers in a window, as reported by the
user. Its runner exited the game without forced termination, restored the game
registry settings and requested Restart. Cold readback confirms consistent
hives and one new normal-shutdown event. The existing Ftdisk 49 event remains.

| Disc | Installation | Startup and rendering | Save/load |
|---|---|---|---|
| Hasbro 1999 | Full, English American, `C:\RCT99` | Title menu and Forest Frontiers; displayed version 1.08.187 | Save file exists. Game returned to the desktop during the save/load sequence; reload unresolved |
| Later Atari disc, non-Deluxe | Full, `C:\RCTLATER` | Title menu and Forest Frontiers; displayed version 1.08.187 | Save and same-session reload observed |
| Deluxe | Full, `C:\RCTDX` | Title menu, animated background and Forest Frontiers | Save and same-session reload observed |

The 1999 run has no screenshot between submitting Save and the subsequent
Load-menu clicks. It therefore cannot distinguish an application failure from
input timing. No new application error event or crash-dump file was found, but
that does not establish a clean exit. This outcome remains recorded separately
from the later Atari success.

Both non-Deluxe editions display 1.08.187, but their installed `rct.exe` files
have different sizes and SHA-256 hashes. They remain separate test candidates;
matching displayed version numbers do not establish binary equivalence.

Deluxe's full installation still needs disc data. A separate transfer control
removed the original ISO, after selecting the game's built-in Window display
mode. The game requested its Loopy Landscapes CD. Pointing that normal dialog
at the installed folder produced “Missing or inaccessible data file.” It then
returned process exit code zero, so exit status alone cannot qualify startup.
The supplied ISO has 20 Data files absent from the full installation. A fresh
PC control copied those unmodified files, retained the game's Window setting,
and temporarily pointed the `Path` and `SetupPath` registry values at the local
game folder. With the optical drive empty, Deluxe reached its title menu and
rendered Forest Frontiers in a window. This tests the combined configuration;
it does not establish which change alone resolves the dependency.

The game executable remains unchanged. The resulting private installation was
copied to the Xbox and launched through the ordinary Windows path at 720p. The
user confirmed the requested title/menu and New Game → Forest Frontiers sequence,
followed by a restart. In a follow-up, the user confirmed building worked but
window-edge scrolling left the view completely still. The exact construction
action was not specified; arrow-key scrolling and right-button dragging remain
untested. Sound testing is deferred at the user's request. Save/reload, sustained
play and frame rate remain untested on Xbox. Rendering this game does not establish native GPU
acceleration or the graphics APIs used at runtime.

The supplied Deluxe manual describes edge scrolling specifically in fullscreen
mode (PDF page 29, printed pages 56–57). It documents right-button dragging and
arrow keys as other ways to move the landscape. The observed still view at a
window edge is therefore consistent with the documented behavior; it is not yet
evidence of an Xbox input defect. The next comparison retains both display
modes and all three controls. See the [manual review](../outputs/rct567/manual-review001.json).

A fresh PC comparison now supports that distinction, with the edge-scrolling
option visibly enabled in both modes:

| PC control568 | Right-edge dwell | Arrow keys | Right-button drag |
|---|---|---|---|
| Window, 640×480 client on an 800×600 desktop | View stayed still; checked viewport pixels identical | Landscape moved | Landscape moved |
| Full Screen640×480 | Landscape moved | Landscape moved | Landscape moved |

Only the right edge was tested, and arrow directions and drag trajectories
differed between modes. Window mode was restored before the helper's automatic
close and normal Restart. Registry restoration and cold hive/event checks passed.
These are PC results; the Xbox alternatives still need testing. The game loaded
`DDRAW.DLL`, but that module inventory is not an API call trace or acceleration
measurement. See the [fresh input comparison](../outputs/rct568/REPORT.md).

The later [native input control573](../outputs/rct573/REPORT.md) reproduced
windowed arrow-key and right-button scrolling without host game input. Edge
scrolling remained stationary. Its fullscreen captures and one passive emulator
image were black, so that unattended fullscreen path remains unqualified.
Returning to Window mode and normal cleanup passed. This is a harness/display
investigation on the PC fixture, not a new Xbox result.

The [builtin Screenshot control574](../outputs/rct574/REPORT.md) rendered
fullscreen without GDI capture. Its game-produced PCX files match independently
sampled emulator display regions. Fullscreen edge scrolling and arrows moved
the park; the subsequent drag did not. A centered screenshot notification may
interfere with that drag, so it remains inconclusive pending a fresh settling
control. Normal restart and registry/hive checks passed; no Xbox claim is added.

The fresh [settling control575](../outputs/rct575/REPORT.md) added ten seconds
after each builtin screenshot. The same native drag now visibly moved the
fullscreen park. Arrows and dragging moved the landscape in both modes;
right-edge scrolling moved it only fullscreen. Game images matched independent
emulator display regions, and normal shutdown/registry/hive checks passed.
This qualifies the automated PC probe for a separate Xbox comparison. It
supports notification interference in574 without proving a unique cause.

The [unattended Xbox comparison576](../outputs/rct576/REPORT.md) reached Forest
Frontiers, but the Windows2000 Getting Started window covered the next click.
The occlusion guard stopped before any scrolling case or fullscreen switch.
Normal restart, hook removal and registry/hive checks passed. This leaves the
Xbox input comparison inconclusive; the Welcome window needs scoped handling
before another unattended test.

A [standalone PC control580](../outputs/rct580/REPORT.md) now qualifies an exact
Welcome-window normal close. A same-title/class lookalike in another process
survived, and the startup checkbox setting remained enabled. The preceding
[control579](../outputs/rct579/REPORT.md) refused a mistyped class and posted no
close; that failure is retained. Integrating this handling with the game and
checking late arrival remain separate steps before another Xbox comparison.

The [Save Game dialog inspection578](../outputs/rct578/REPORT.md) identified the
owned filename and Save/Cancel controls on a fresh PC fixture. Cancelling returned
to an unchanged park view, and normal restart and registry/hive checks passed.
This prepares the save/reload test; it did not create a save or establish Xbox
persistence across restart.

The next performance work uses a save reloaded across a normal restart, a
recorded fixed scene and an observed graphics-API path before choosing an
optimization. See the [measurement plan](rct-performance-plan.md) for the
workloads, clock checks and limits on interpreting presentation calls as FPS.

The transfer is about 508 MiB, before spare space for logs and saves. It contains
retail assets from the supplied disc and is not a public redistributable bundle.
The watched Xbox result applies to Deluxe only; the two non-Deluxe discs still
have PC-control results only.

## Test conditions

Each PC installation used a fresh child of the same Windows 2000 NTFS seed,
64 MiB RAM, a Pentium III CPU model and Cirrus VGA under QEMU TCG. The original
ISO was mounted read-only. No game patch, compatibility shim or executable edit
was applied. The fixtures had no network or emulated audio device. Optional
registration was skipped, and installers that checked DirectX accepted the
installed version without replacement.

The game screens were 640 by 480. The later Atari registration window required
an 800 by 600 Windows desktop to expose its Close control; the game switched to
640 by 480 when launched. Mouse menu interaction was observed, but broad input,
construction, frame rate, prolonged play and sound have not been qualified.
Save reload was within the same game session, not after rebooting Windows.

The Xbox check used the existing native Windows 2000 installation, its protected
720p configuration and the ordinary XWNEBoot launcher. The prepared Deluxe files
were copied to dashboard `E:\xwn565-kit\game`, visible to Windows as
`C:\xwn565-kit\game`. A temporary startup helper set three game registry values,
launched the unmodified executable, waited about three minutes, then requested
a graceful game close, restored the values and requested Windows Restart.
Rendering evidence for this run is the user's watched observation; the helper
records process and window state, not screenshots or graphics API calls.

Each successful guest session ended through Windows Restart. Offline disk or
dashboard readback checks verify registry hive consistency, shutdown events and
unchanged protected OS executables. Game binaries, screenshots, saves and disc images remain private.
Only hashes, metadata, tooling and observations are published.

## Disc identities

Filenames identify the supplied files; they do not establish authenticity or
equivalence to any other retail pressing. These are SHA-256 hashes of the full
ISO files actually used:

| Filename | Bytes | SHA-256 |
|---|---:|---|
| `Roller_Coaster_Tycoon_Hasbro_Interactive_1999.iso` | 186191872 | `dd27bc2b69bbb967de172c4ec2b47ca9262ef4933ae730df117f483be2a99e06` |
| `Rollercoaster Tycoon.iso` | 168894464 | `e5aa622a680f7a61383d3456e8ee3cd16c3e31f5955a9035b799b3fe1f941539` |
| `RollerCoaster Tycoon Deluxe.iso` | 526432256 | `7910b1440239f7026821507180e6dfdbc5a119147baaf77c4e542182c1ad9052` |

## Reproducing the initial check

1. Start with a separate, backed-up Windows 2000 installation for each edition.
2. Mount your own matching disc, run `D:\setup.exe` and select a full installation.
3. Use a short installation path as listed above, retain an adequate existing
   DirectX installation and skip optional online registration.
4. Launch the installed game, choose New Game, then Forest Frontiers. Record
   the exact game version, errors and whether the park and menus render.
5. Save under a unique name, observe the return to the park, then load that
   file and observe rendering again. Keep each step separately evidenced.
6. Quit the game and restart Windows normally before inspecting persisted files.

Do not treat these steps as an Xbox installer. The exploratory Deluxe transfer
uses matching registry paths, local disc data and a bounded test runner. Broader
Xbox input, save persistence, audio and repeatability checks are still needed.
An installed filename-length check alone does not qualify the whole FATX layout.
Static executable imports are not a trace of the graphics APIs used at runtime.
Game compatibility and native GPU acceleration remain separate milestones.

## Evidence

- [Media inventory and test design](../outputs/rct559/DESIGN.md)
- [1999 installation and unresolved reload](../outputs/rct561/REPORT.md)
- [Later Atari installation](../outputs/rct562/REPORT.md)
- [Deluxe installation and reload](../outputs/rct563/REPORT.md)
- [Initial host socket failure, before guest boot](../outputs/rct560/REPORT.md)
- [Deluxe full-install disc-data failure](../outputs/rct564/REPORT.md)
- [Deluxe local-data and windowed control](../outputs/rct566/REPORT.md)
- [Watched native Xbox Deluxe result](../outputs/rct565/REPORT.md)
- [Xbox transfer tooling and preserved FTP failures](../outputs/rct565/TRANSPORT.md)

The [integrated PC581 control](../outputs/rct581/REPORT.md) qualified reconstruction
of502 local assets using the original CD plus a small supplemental CD, with both
drives empty before launch. The exact Welcome process closed normally, but an
Explorer Start-button guidance balloon blocked the first title capture. The
strict exposure check stopped the sequence; no scrolling or late-popup result
was obtained. Normal shutdown, registry restoration and cold checks passed.

The subsequent [PC584 control](../outputs/rct584/REPORT.md) used the same tested
helper on a1024x768 desktop, leaving that shell balloon outside the640x480 game
window. All15 captures completed: window-edge scrolling remained still, arrows
and right-drag moved the camera, and all three worked in Full Screen mode. Early
and deliberately reopened late Welcome windows closed normally; startup
preferences, registry restoration and shutdown checks passed. This is PC control
evidence, separate from the Xbox result.

The matching [Xbox583 attempt](../outputs/rct583/REPORT.md) accepted one launch
request and returned to the dashboard without creating the runner's output.
Checked files and event logs were unchanged, with no new normal-shutdown event.
Its test hook was removed and the baseline preserved. It supplies no additional
physical scrolling or fullscreen result; the boot-stage cause is unresolved.
