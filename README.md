# Native Windows 2000 on the original Xbox

This project adapts open-source bootloaders, a hardware abstraction layer (HAL),
and device drivers so Windows 2000 can run directly on the original Xbox's CPU.
It combines FATX storage, software-rendered graphics, AC'97 audio and desktop
input. xemu is a separate development/test environment; the physical console
runs Windows natively.

Fixed 720p packages reached the Windows desktop on the tested Xbox 1.0 and 1.6
consoles. Text and full-window dragging were confirmed clean on the original
Conexant test display. The historical 1080i path boots, but its text and motion
defects remain unresolved. Graphics are software-rendered, without native GPU
acceleration. Profile-specific evidence and remaining limits are recorded below.

## Start here

For a new development machine, follow [fresh environment setup](docs/ENVIRONMENT-SETUP.md).
No WSL image or copied toolchain is required.

- **[Move development to a new machine](docs/MIGRATION.md)** — source setup, private packages, pinned tools and WSL transfer
- **[Current status and guide map](docs/current-status.md)** — capabilities, remaining work and latest engineering handoff
- **[External tester quick start](docs/testers.md)** — hardware report, installation checklist and results
- [How it works and what we changed](docs/architecture.md)
- [Find and edit the source](src/README.md)
- [Build the components](docs/building.md)
- **[After building: prepare Windows, package, copy and boot](docs/build-to-boot.md)**
- **[Build the hardware-info and private Windows ZIPs](docs/build-test-kits.md)**
- [Installation and first boot](docs/installation.md)
- [Resolution and desktop settings](docs/display-configuration.md)
- [Windows Media Player demo](docs/media-player-demo.md)
- [Troubleshooting](docs/troubleshooting.md) and [recovery](docs/recovery-guide.md)
- [Development](docs/development.md) and [licensing](docs/licensing.md)
- [Component origins and Windows dependencies](docs/provenance.md)
- [Windows disc hashes and media validation](docs/windows-media.md)
- [Validated results and remaining release work](docs/validation.md)
- [Next milestone: classic games and Direct3D](docs/graphics-roadmap.md)
- [Graphics sample ladder: build and run](docs/graphics-samples.md)
- [RollerCoaster Tycoon installation and compatibility tests](docs/rct-compatibility.md)

## Current capabilities

| Area | Current result | Limits |
|---|---|---|
| Boot | Dashboard → Xromwell → Windows | Matched boot chain required; intermittent failed launches remain |
| Storage | Native FATX; file creation, copy, move and readback tested | Keep backups; strict event failures remain |
| Graphics | Software desktop and HD framebuffer | No acceleration or live resolution switching |
| Display | Fixed 720p packages on Xbox 1.0 and 1.6; historical 720×480 drawing/input/persistence results | Current 1.0 480p package held; 1080i defects remain; no live switching |
| Audio | Login sound and louder tones heard | Exact stereo routing unconfirmed |
| Input | Standard mouse/keyboard | Device prompts and boot-time USB issues remain |
| Network | Native networking; exact bidirectional TCP transfer on the fresh emulator assembly | Broad compatibility not established |
| Installation | Clean customized-disc assembly and fresh component builds booted in xemu; prepared E restore tested separately | Portable fresh-console installer, strict qualification and physical recovery remain incomplete |

## Repository layout

```text
src/        Maintained source files, grouped by component
upstream/   Base commits, source hashes and build profiles
tools/      Build, configuration and validation commands
docs/       User and developer guides
LICENSES/   Preserved upstream license texts
outputs/    Historical experiments and engineering evidence
```

Start with `src/` and the guides. Each component retains its independently tested
upstream tree; these profiles are not one unified OS build. The current complete
component inventory distinguishes project source from user-supplied Windows
files; see [provenance](docs/provenance.md) for source and binary correspondence.

## Next milestone

The next graphics target is playable original **RollerCoaster Tycoon and The
Sims**, including input, sound and save/reload on a 64 MiB Xbox. Deluxe now reaches
its title menu and renders Forest Frontiers in a watched native Xbox test.
Building, repeated manual save/load, arrow keys and right-button scrolling worked.
Window-edge scrolling left the view still. Sound is deferred; fullscreen,
sustained play and Xbox game FPS remain unqualified. Three supplied
RCT editions also install and render a park in Windows 2000 PC controls; two
pass a short same-session save/reload check. The Sims has not been tested.
See the [RCT results and limitations](docs/rct-compatibility.md).
The [graphics roadmap](docs/graphics-roadmap.md) starts with exact
game editions and DirectDraw/API probes, then the required legacy Direct3D work.
Game compatibility, software rendering and native GPU acceleration are separate
results. 720p remains the baseline; the 1080i investigation is paused.

The current delivery work covers separate fixed video profiles. The packaged
Xbox 1.6 720p build reached the Windows desktop with working mouse input in test
845. The packaged Xbox 1.0 720p build reached the desktop and Start menu in test
846, followed by a reported return to UnleashX after Windows Restart. The 1.0
480p package is held after a retrace-status timeout, 1080i retains text and motion
defects, and the current 1024x576 E package has emulator-only evidence. See
[current status](docs/current-status.md) and the package inventory in the
[migration guide](docs/MIGRATION.md) for the exact qualification limits.

In parallel, installation needs a portable Windows registry conversion and a
lossless solution for FATX's long-name limitation. The [build-to-boot guide](docs/build-to-boot.md)
shows the artifact layout, preparation requirements and verified copying procedure,
including where the current clean-install workflow must stop.

## Release status

The source repository is public. It is an experimental project, not a Windows
distribution or a finished fresh-install kit. The [tester kit](docs/tester-bundles.md)
provides a standalone hardware-report XBE and host verification tools. A portable
Windows package still needs the clean-install and physical-validation gates in
[release readiness](docs/PUBLIC-RELEASE.md). A ZIP checksum is not a compatibility claim.

Windows media, product keys, firmware, EEPROMs, dashboards, user data and private
recovery archives are excluded from project downloads. Historical `outputs/`
records contain development-machine paths; use the parameterized `tools/` commands
and current `docs/`, rather than running an old experiment script.

The current demo is newer than the preserved historical tags. Do not mix older
F-partition boot profiles with the current E installation. Dashboard partition
names differ from Windows drive letters; consult the installation guide before
copying anything. Dashboard C is not an installation target.

Physical, emulator and human observations remain distinct. A working desktop
does not waive the retained Ftdisk 49 event failure. Experimental GPU and device
prototypes are excluded from the demo.

Original project work is MIT-licensed where no upstream terms apply. Derived
components retain their licenses; see [NOTICE.md](NOTICE.md).
