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
