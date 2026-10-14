from pathlib import Path
files = {
'README.md': '''# Native Windows 2000 on the original Xbox

This project adapts open-source bootloaders, a hardware abstraction layer (HAL),
and device drivers so Windows 2000 can run directly on the original Xbox's CPU.
It combines FATX storage, software-rendered graphics, AC'97 audio and desktop
input. xemu is a separate development/test environment; the physical console
runs Windows natively.

The integrated demo is usable for desktop applications on the tested 64 MiB,
Conexant-equipped Xbox. **720p is recommended:** text and full-window dragging
were confirmed clean on the test display. The 1080i path boots, but its text and
motion defects remain unresolved. Graphics are software-rendered, without
native GPU acceleration.

## Start here

- [How it works and what we changed](docs/architecture.md)
- [Find and edit the source](src/README.md)
- [Build the components](docs/building.md)
- [Installation and first boot](docs/installation.md)
- [Resolution and desktop settings](docs/display-configuration.md)
- [Troubleshooting](docs/troubleshooting.md) and [recovery](docs/recovery-guide.md)
- [Development](docs/development.md) and [licensing](docs/licensing.md)

## Current capabilities

| Area | Current result | Limits |
|---|---|---|
| Boot | Dashboard → Xromwell → Windows | Matched boot chain required |
| Storage | Native FATX; file creation, copy, move and readback tested | Keep backups; strict event failures remain |
| Graphics | Software desktop and HD framebuffer | No acceleration or live resolution switching |
| Display | 720p text and full-window dragging confirmed clean | 1080i defects; other encoders need qualification |
| Audio | Login sound and louder tones heard | Exact stereo routing unconfirmed |
| Input | Standard mouse/keyboard | Device prompts and boot-time USB issues remain |
| Network | Native networking and reported ping success | Broad compatibility not established |
| Installation | Working E-partition demo | Fresh-console installer and full restore test incomplete |

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
HAL/network/input binary-to-source inventory still needs release review.

## Release status

This checkout is being prepared for a first public source release. It is not a
Windows distribution or finished fresh-install kit. Windows media, product keys,
firmware, EEPROMs, dashboards, user data and private recovery archives are not
public assets. The private Git history is not suitable for publication wholesale.

The current demo is newer than the preserved historical tags. Do not mix older
F-partition boot profiles with the current E installation. Dashboard partition
names differ from Windows drive letters; consult the installation guide before
copying anything. Dashboard C is not an installation target.

Physical, emulator and human observations remain distinct. A working desktop
does not waive the retained Ftdisk 49 event failure. Experimental GPU and device
prototypes are excluded from the demo.

Original project work is MIT-licensed where no upstream terms apply. Derived
components retain their licenses; see [NOTICE.md](NOTICE.md).
''',
'src/README.md': '''# Source map

These are actual source files. Each component contains the files changed from
its pinned upstream base, at their upstream-relative paths. The build tool
supplies unchanged upstream files in a fresh checkout and verifies its complete
Git tree identity.

| Profile | Source | Purpose |
|---|---|---|
| `fatx` | [FATX](drivers/fatx/drivers/filesystems/vfatfs) | Files, directories, allocation, cache and paging |
| `framebuffer` | [Miniport](drivers/video/framebuffer/win32ss/drivers/miniport/xboxvmp/nt5), [boot video](drivers/video/framebuffer/drivers/base/bootvid) | Physical display handoff and boot drawing |
| `loader` | [FreeLdr](boot/loader/boot/freeldr) | Windows boot adaptations |
| `display` | [Software display](drivers/video/display/win32ss/drivers/displays/framebuf) | GDI drawing and framebuffer updates |
| `launcher` | [Xromwell](boot/xromwell) | Dashboard boot entry and video timing |
| `audio` | [AC'97](drivers/audio/drivers/wdm/audio/drivers/ac97) | Audio controller support |
| utility | [Settings](utilities/display-settings/settings.c) | Dragging and font preferences |

Overlays also include supporting HAL, header and build-system changes. Their
presence does not mean every target in that tree is the installed version.
Only the explicit targets in [components.json](../upstream/components.json)
are selected. Complete HAL/network/input release provenance remains unfinished.

Profiles contain different versions of some upstream paths. Keep them separate:
merging them without new builds and regression checks would discard tested
configurations. Unification is development work, not a file-move operation.

Edit files here, then follow [development](../docs/development.md). New files,
deletions and executable modes require explicit manifest updates. Existing
file edits can be built with `--allow-modified`, which records their new identity
instead of claiming the tested baseline. Original license headers are preserved.
''',
'upstream/README.md': '''# Upstream profiles

[components.json](components.json) records base commits, complete reviewed trees,
overlays, file modes/hashes, build definitions, targets and output names. The
recorded repository URLs are provenance references; anonymous access has not
been qualified. Supply a Git cache containing the exact base commit.

`tools/xwn.py source` creates a detached checkout, applies `src/` and compares the
complete tree. It also verifies recorded checkout-byte rules, including the
AC'97 INF's CRLF conversion. Outputs borrow Git objects read-only through
alternates: retain the cache while using them. They are build workspaces, not
standalone source exports.

The framebuffer target is `xboxbvidnt5`; its installation filename is
`xboxbvid.dll`. The earlier historical review bundle incorrectly called the
target `xboxbvid`. This manifest corrects the recipe without rewriting evidence.

Compiler hashes pin recorded tools. A successful build establishes compilation,
not historical binary reproducibility or hardware qualification.
''',
'NOTICE.md': '''# License scope and provenance

The root [MIT license](LICENSE) applies to original project work, including new
documentation and original tooling, except where a file's notice or upstream
derivation requires other terms. It does not relicense upstream components.

- ReactOS-derived files retain their copyright and license notices. See
  [LICENSES/reactos](LICENSES/reactos). HAL, loader and driver modifications
  retain applicable upstream terms and corresponding-source requirements.
- Cromwell/Xromwell retains its notices and [license](LICENSES/cromwell/COPYING).
- The AC'97 sample has [Microsoft's MIT notice](LICENSES/audio-ac97.txt).
  Linked ReactOS support code can have different terms: the whole driver is
  not declared MIT merely because the sample is.
- The original settings utility retains its [MIT notice](LICENSES/utility-MIT.txt).
- Historical nxdk-derived experiments retain their own notices. The historical
  `outputs/` tree is not a curated public release.

[upstream/components.json](upstream/components.json) identifies the maintained
profiles and bases. No ownership of upstream work is asserted. Windows files,
keys, firmware, EEPROMs, proprietary dashboards and user data are not licensed
by this project and are excluded from public assets. See [licensing](docs/licensing.md).
''',
'docs/architecture.md': '''# How the project works

The original Xbox is an x86 computer whose hardware and boot conventions differ
from a PC. This project supplies adaptations that let Windows 2000 use that
hardware; it does not replace the Windows kernel.

## Boot path

```mermaid
flowchart LR
  A[UnleashX dashboard] --> B[Xromwell launcher]
  B --> C[FreeLdr and rosload]
  C --> D[Windows 2000 kernel]
  D --> E[Xbox HAL and drivers]
  E --> F[Desktop applications]
```

The dashboard starts an XBE. The Cromwell-derived launcher sets up the selected
video timing and boot environment. The ReactOS-derived loader locates Windows
and supplies its handoff. Xbox HAL and driver changes handle the platform.

Launcher, loader, HAL, boot video, miniport and display driver must agree on the
framebuffer reservation, address, dimensions, stride and cache behavior. A mode
is therefore a matched boot profile, not just a desktop setting.

## Storage and display

The FATX driver implements Windows file, directory, allocation, cache and paging
operations on Xbox partitions. Recent work fixes duplicate directory results
and CMD copy/move behavior. Tests compare saved contents and allocation state
after shutdown, rather than relying on successful API returns. This does not
format the disk as NTFS. See [partition mapping](installation.md).

The display driver draws with the CPU and updates the framebuffer. Software
copy, text, bounds and transfer paths have been investigated. At 720p, the user
confirmed clean text and full-window dragging. 1080i presentation remains open.
The working demo contains no experimental GPU ownership or acceleration code.

AC'97 integration provides audible login sounds and test tones. Exact stereo
routing and broad audio compatibility remain unconfirmed.

## Project contributions

- Xbox boot/Windows handoff adaptations, partition selection and coordinated HD
  framebuffer reservation.
- FATX compatibility and persistence fixes validated with file readback.
- Software display and handoff changes, desktop preferences and mode configuration.
- Audio integration and an assembled desktop demo.
- Source/build identification, emulator diagnostics, hardware records, cold
  filesystem checks and private recovery packaging.

The [source map](../src/README.md) shows maintained files. The
[development guide](development.md) distinguishes test scopes and remaining work.
''',
'docs/building.md': '''# Build the components

The build command reconstructs one reviewed component tree from an upstream Git
cache plus `src/`, then builds its selected binaries. It does not create Windows
media, configure a registry, install drivers, flash firmware or contact a console.

## Requirements

- Linux or WSL, Python 3.10+, Git, Make and normal build utilities.
- An upstream Git cache containing the exact manifest base commit. Linked Git
  worktrees are supported.
- Recorded RosBE 2.2.1 for ReactOS profiles, or recorded GCC 12 for Xromwell.
  Tool hashes are checked against [components.json](../upstream/components.json).
- At least 20 GiB free on the output filesystem and WSL's Windows backing volume.
  This reserve is checked; it is not a build-size estimate.
- A fresh output directory outside the repository, cache and toolchain. Prefer
  WSL's Linux filesystem for compilation speed.

This guide assumes the pinned source and toolchains are already available. A
verified anonymous dependency-download/bootstrap path remains release work.
Recorded URLs are provenance references; do not substitute arbitrary latest
revisions when reproducing the baseline.

## Commands

From the repository root:

```sh
python3 tools/xwn.py list
python3 tools/xwn.py verify
```

Choose your own paths. `CACHE` is a Git repository with the required ReactOS
base; `ROSBE` is the extracted toolchain directory:

```sh
CACHE="$HOME/upstream/reactos"
ROSBE="$HOME/toolchains/RosBE-2.2.1"
OUT="$HOME/build/xwn-fatx-001"
python3 tools/xwn.py build --profile fatx --cache "$CACHE" --rosbe "$ROSBE" --output "$OUT"
```

For source reconstruction only, use `source` instead of `build` and omit
`--rosbe`. The full Git tree must match. Keep the source cache while using the
output because the workspace borrows its objects read-only.

Repeat with **fresh output directories** for `framebuffer`, `loader`, `display`
and `audio`. They are independent trees; do not combine their build directories
or build every component from one profile. For Xromwell:

```sh
python3 tools/xwn.py build --profile launcher --cache "$HOME/upstream/cromwell" --gcc12 /usr/bin/gcc-12 --output "$HOME/build/xwn-launcher-001"
```

This launcher selects E-partition 720p. Other resolutions need matched profiles
and validation, not a single changed compiler flag.

## Results

| File/directory | Meaning |
|---|---|
| `source/` | Detached base checkout with maintained overlay |
| `source.json` | Base/tree identity and explicit development edits |
| `build-command.json` | Command, tool pins and capacity checks |
| `build.log` | Compiler output, including warnings |
| `artifacts/` | Selected binaries under installation filenames |
| `build.json` | Artifact sizes/hashes and source/tool identities |

Failed attempts remain for inspection; use a new directory next time. Successful
compilation is not historical binary identity or hardware qualification. Follow
[development](development.md) and [installation](installation.md) before deployment.

`--allow-modified` permits edits to listed source files and records their new
identity. New paths/deletions/modes need manifest review. On shared machines,
wrap builds in the machine's build lease/scheduler; this portable command does
not acquire a machine-specific lock or alter the shared SDK.

## Display-preference utility

[settings.c](../src/utilities/display-settings/settings.c) is independent of the
six overlays. With RosBE's i686 compiler on PATH, its recorded command is:

```sh
i686-w64-mingw32-gcc -Os -Wall -Wextra -Werror -nostdlib -fno-stack-protector -fno-builtin -Wno-misleading-indentation -Wl,--entry,_mainCRTStartup@0 -Wl,--subsystem,console:5.0 -o display-settings.exe src/utilities/display-settings/settings.c -lkernel32 -luser32 -ladvapi32
```

The indentation-warning exemption is inherited from this utility's recorded
build; it is not a general suppression policy.
'''
}
mit = Path('LICENSES/utility-MIT.txt').read_text()
# Root license is the standard grant, with explicit project attribution.
start = mit.find('Permission is hereby granted')
assert start >= 0
files['LICENSE'] = 'MIT License\n\nCopyright (c) 2026 Paul Demers and contributors\n\n' + mit[start:]
for name, text in files.items():
    p = Path(name); p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding='utf-8', newline='\n')
