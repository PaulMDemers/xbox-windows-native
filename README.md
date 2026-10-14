# Native Windows on the original Xbox

Experimental native Windows 2000 bootloader, HAL and drivers for the original
64 MiB Xbox. Windows runs on the Xbox CPU; xemu is a separate test environment.

The current private demo combines native FATX storage, software-rendered HD
video, AC'97 audio and standard USB keyboard/mouse support on the tested
Conexant console. It is usable for desktop applications. It is not a general
Windows installer or a GPU-accelerated desktop.

## Start here

- [Use the integrated demo](docs/DEMO.md)
- [Configure resolution and dragging](docs/DISPLAY.md)
- [Recovery and partition mapping](docs/RECOVERY.md)
- [Build and provenance](docs/BUILD.md)
- [First public source release](docs/PUBLIC-RELEASE.md)
- [Contributing](CONTRIBUTING.md)

## Current scope

| Component | Included | Limits |
|---|---|---|
| Storage | FATX0101, E installation, original F rollback | Experimental; preserve backups |
| Video | Software display303 and HD boot chain | No native GPU acceleration or live mode switching |
| HD modes | E demo now selects720p; user reports clean text | 1080i has an unresolved visible text problem; full E720p qualification is separate |
| Audio | ACI207 build004 | Login/louder tones heard; exact stereo routing unconfirmed |
| Input | Standard keyboard/mouse | Keep Razer keyboard unplugged through Xromwell |
| Network | Native networking, user-confirmed ping | Limited legacy software environment |
| Other devices | Existing policy retained | Unqualified PCI/gamepad prototypes excluded; prompts may remain |

Outline dragging avoids repainting window contents during movement. Recent
matched software-copy/stretch experiments showed no material gain. Further
framebuffer and GPU work proceeds separately from the demo.

## Evidence and release status

The current E installation is a later private preview. Immutable 0.1.0 and
0.2.0 remain unchanged. The older 0.2.0 HD selector targets F; do not apply it to
E. See [current status](outputs/engineering-notes/STATUS.md) and
[continuation notes](outputs/engineering-notes/CONTINUATION.md) for exact results.
Physical tests, emulator tests and human observations remain distinct. Ftdisk49
and the physical capacity warning remain failed event gates.

The repository stays private while a focused public source export is prepared.
Windows files, firmware, EEPROMs, dashboards, hives, user data and private
recovery archives are excluded from public assets. Each derived component
retains its own license; no blanket project license is asserted.

The [previous chronological README](docs/archive/README-before-demo-20261013.md)
is preserved as history. Its historical status statements do not override the
current guides.
