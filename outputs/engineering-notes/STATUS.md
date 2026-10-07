# Native Xbox Windows 2000 status — 6 October 2026

Early7October emulator follow-up: the ordinary fifteen-minute0098 workload
passed after supported GPU setup and an emulator-only null-device INF. New
concurrency tests then proved two separate FATX deadlocks: regular-file cleanup
versus volume flush, and rename's parent-directory cache flush versus volume
flush. Candidate0101 separates ordinary-file and directory-stream lock ordering.
Two independent five-worker500-round runs and the full fifteen-minute mapping/
BMP persistence soak passed all workload, normal-restart, event, exact-file,
five-hive and allocation gates. Candidate0101 is eligible for a controlled
hardware trial, not physically or release qualified. One controlled physical0101/video0093 concurrency trial launched at00:50:29UTC
on7October, with0098 rollback and startup preserved. Its result is pending. See
[continuation](CONTINUATION.md) for evidence and the hardware handoff.

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
- Current controlled trial: FATX0101/video0093, one-shot concurrency startup.
  Original0098 driver/startup saved locally and in /F/xwn101a; collection restores
  normal startup first. Hardware qualification is pending.
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

A subsequent [paired idle test](../shutdown-install-idle/README.md) removed the
explicit mapping/BMP workload. Both runs waited two minutes and restarted
normally. The unchanged control had no popup; the package installed correctly
but still emitted the shutdown popup. Both allocation audits were clean. This
narrows the reproduction to a first-install/shutdown scenario without requiring
the explicit storage workload; the ordinary pair alone does not identify the
failing process or establish a universal cause.

A subsequent [minimal trace](../shutdown-idle-trace/README.md) of the exact
package seed reproduced the same popup. Its owner is rundll32 running newdev
for emulator PCI1B36:0005. Matched win32k raises the hard error before winlogon
enters kernel shutdown. Cold installation, selected binary/hive checks and
full F: allocation pass, but the popup remains a strict failure. Creation,
resume and termination ordering were not captured; debugger timing and this
emulator device identity cannot be generalized to the physical console.

[Source research and a host event recorder](../native-event-recorder/README.md)
now identify that emulator device as the QEMU PCI test device used by xemu as a
memory-controller placeholder. The new recorder captures selected lifecycle
events without debugger stops. One disabled/enabled pair passed bounded cold
checks, and the enabled run captured 423 verified records. It observed a failed
late installer creation and termination during shutdown, without the popup.
The subsequent fixed reproduction batch captured the failing lifecycle too:
creation succeeds, the placeholder installer executes and raises the GUI
shutdown error, then terminates with0xc0000142 before PnP receives shutdown
control5. A separate unchanged run follows the clean invalid-handle path.
See [the captured sequence](../native-event-recorder/FAILING-LIFECYCLE.md).
The recorder still has no demonstrated zero-overhead guarantee, and no
synchronization fix is qualified.

The [window observer](../shutdown-installer-windows/README.md) answered the next
question: the GPU wizard waited at its successful Finish page. Completing it
exposes a restart question, then the next unsupported device. The
[completion experiments](../shutdown-installer-completion/README.md) confirm
that cancelling the next wizard only clears that boot; it returns on a later
boot. A pending-install guard correctly withholds restart in that state.
One earlier observer run also stalled during kernel volume flush; it remains
unresolved and is not explained away by the installer findings.

An [explicit emulator-only null package](../shutdown-null-placeholder/README.md)
now configures the unused QEMU test function without a function driver or
changed hardware identity. Normal setup and an ordinary subsequent boot pass:
the queue becomes idle, no installer recurs on the subsequent boot, normal
shutdown returns to dashboard, and cold event/hash/hive/allocation checks pass.
Both the original short workload and a full fifteen-minute workload passed527
checks and cold audits, including normal shutdown and dashboard return. The
emulator parent still contains the earlier01B0/01B4 FAILEDINSTALL flags; those
are absent on hardware. This configuration avoids outstanding setup; it does not repair the original Windows
shutdown synchronization race or establish physical device support.

A fresh [read-only physical snapshot](../physical-pnp-followup/README.md) verifies
the installed baseline is unchanged. Its latest SetupAPI records still name
the unsupported Xbox01B0 audio function, and GPU PnP registration is incomplete.
Historical emulator/PC entries also remain in the hive; registry presence alone
does not mean those devices are present on the console. No hardware package has
been deployed from these emulator experiments.

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
