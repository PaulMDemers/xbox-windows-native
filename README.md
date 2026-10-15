# Native Windows 2000 on the original Xbox

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
- [Component origins and Windows dependencies](docs/provenance.md)
- [Windows disc hashes and media validation](docs/windows-media.md)
- [Validated results and remaining release work](docs/validation.md)

## Current capabilities

| Area | Current result | Limits |
|---|---|---|
| Boot | Dashboard → Xromwell → Windows | Matched boot chain required |
| Storage | Native FATX; file creation, copy, move and readback tested | Keep backups; strict event failures remain |
| Graphics | Software desktop and HD framebuffer | No acceleration or live resolution switching |
| Display | 720p text and full-window dragging confirmed clean | 1080i defects; other encoders need qualification |
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
