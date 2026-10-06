# Native Xbox Windows 2000 status — 6 October 2026

The project has reached a usable native desktop milestone. It is still an
experimental system with incomplete device setup and bounded, rather than
general, stability qualification. Windows runs on the Xbox CPU and stores its
ordinary files on FATX; xemu is the separate development/test environment.

## Established physical capabilities

- Boot screen and desktop; keyboard, mouse and drive browsing.
- User-observed Notepad, Calculator, Solitaire, Command Prompt and Paint use.
  Later Paint saves/reopens were independently checked. The earlier isolated
  save freeze has no demonstrated root cause and must remain in the history.
- User-reported ping, Pinball and the OpenGL Pipes application. These are not
  bulk-network qualification or evidence of hardware-accelerated OpenGL.
- A root-level Windows entry in UnleashX. Video0093 subsequently passed two
  physical boots without resetting its diagnostic trace between them.
- Current recorded installed combination: FATX0098/video0093, normal startup.
  Original0088 rollback and the immutable v0.1.0 release remain preserved.

## Storage and stability

The v0.1.0 snapshot preserves the earlier qualified0088 milestone. Post-release
FATX0098 fixes leakage of allocation slack beyond EOF in paging reads, including
the demonstrated odd-length driver-image checksum failure. The focused physical
trial passed. The completed third fifteen-minute0098 soak passed527 checks,
16 synthetic BMP API cases,50 exact final files,34 absent intermediate files,
full allocation consistency,3,439 binary hashes and nine structural hives.

That soak's strict overall result remains **FAIL**: one shutdown-time rundll32
popup and three Srv2013 low-space warnings were recorded. The warnings map to
small Xbox system/cache partitions, not the large Windows boot volume. They are
retained as failures under the existing gate; no silent waiver or new
PASS-gated recovery capture has occurred.

Emulator tracing reproduced the popup and located its hard-error call in
win32k during late device installation. Other traces observe a PnP token
close/use race and late creation failing with invalid handle. Clean controls
do not establish a popup fix, and the failing emulator device identity cannot
be assigned to the physical console without physical evidence.

The latest [GPU package experiment](../shutdown-device-install/README.md)
completed a normal installation using unchanged physical-baseline binaries.
Its first run still recorded the popup and missed dashboard return. Three independent
replays of the installed state retained registration and
passed bounded workload/shutdown checks without a popup. Full F: allocation
checks on the input and two latest replays were clean, with reserved marks
unchanged. These are independent replays, not consecutive reboots or proof of a
fix. The first-install failure still prevents promoting a hardware package.

## Graphics and device support

The current physical display path retains the inherited framebuffer mode.
Window dragging is visibly slow. There is no qualified rendering acceleration,
Windows mode switching,720p or1080i implementation. Mapping and display-driver
prototypes have useful emulator results but are not promoted to hardware.
Device installation, repeat boot and display lifetime handling must pass before
performance changes are judged in a matched hardware test.

Audio, bulk TCP transfers, long mixed-application sessions and electrical
power-off still need development or qualification. Running a program is not
equivalent to qualifying every subsystem it can use.

## Release, documentation and reconstruction

- v0.1.0 is tagged and has private, readback-verified system/boot/source recovery
  bundles. A full restoration of those archives has not been tested.
- FATX/platform findings and Linux-oriented notes are written in this directory.
  They include post-release EOF findings. No external project has been contacted.
- Reusable Xbox development skills are installed and versioned in the project.
- Fresh reconstruction builds seven native components plus the Cromwell launcher.
  Repeated assembly produces identical overlay packages, and a rebuilt overlay
  passed an emulator boot/GDI workload. Complete bootable-system reconstruction,
  toolchain portability and deterministic compiler outputs remain open.
- The repository is private. Public-export/provenance/data review is underway;
  Windows binaries, firmware and personal recovery material are not public assets.
- xemu changes are inventoried. Networking changes and synthetic diagnostic
  resource changes are distinguished; no upstream issue or PR has been submitted.

## Next gates

Complete and validate real device installation in disposable emulator fixtures,
including a subsequent boot, then retest the shutdown workload without error
suppression. Preserve controls and distinguish emulator-specific devices from
physical support. After an eligible candidate exists, run a bounded hardware
trial and restore/reverify the baseline as appropriate. Graphics speed/modes,
network/audio qualification and a sanitized reproducible public release remain
separate work streams.

Latest experiment details and actual running-process state are maintained in
[CONTINUATION.md](CONTINUATION.md). The evidence index is [README.md](README.md).
