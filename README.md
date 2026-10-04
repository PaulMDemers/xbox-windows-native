# Native Windows on the original Xbox

Experimental native Windows 2000 bootloader/HAL and driver development for a
64 MiB original Xbox. Windows runs directly on the Xbox CPU; xemu is the
host-side test harness.

## Current evidence

- Physical console: Windows kernel entry, processor initialization, HAL base
  setup, RTC calibration, clock setup and partition-hook registration and BIOS page allocation passed.
- Latest physical checkpoint: **XWNO90**. Windows mapped 504 initial
  nonpaged-pool pages at 0xfe4af000. Next candidate PFN is 0x374 with
  7660 pages remaining. Pool initialization, PFN setup, storage drivers
  and desktop remain beyond the physical-tested stop.
- Private emulator fixtures have reached a Windows 2000 desktop with NTFS,
  USB input, framebuffer, networking and experimental audio. Those results
  do not establish physical hardware compatibility.

The physical-tested **XWNI90** reserves the two BIOS phase-0 pages and
halts before HAL returns to Windows; see
[BIOS diagnostic](outputs/native-windows-physical-bios/REPORT.txt).

The physical-tested **XWNM90** returns HAL phase 0 and stops at the memory-
manager entry, restoring its temporary in-memory checkpoint. See the
[MM entry report](outputs/native-windows-physical-mm/REPORT.txt).

The physical-tested **XWND90** runs the original memory-manager prefix and
stops before MiInitMachineDependent changes page tables; see the [machine-init report](outputs/native-windows-physical-mi/REPORT.txt).

The physical-tested **XWNV90** moves diagnostic output into the high HAL,
executes native low-mapping removal and stops before RAM descriptor scanning.
Both display modes and the native trace pass in xemu; the physical
checkpoint is photo-confirmed. See the [mapping-transition report](outputs/native-windows-physical-map/REPORT.txt).

The physical-tested **XWNS90** completes the native RAM descriptor scan
and checks its counts and candidate spans before MM allocation or PFN setup.
Both display modes and a 45-checkpoint trace pass in xemu; the physical
checkpoint is photo-confirmed. See the [RAM scan report](outputs/native-windows-physical-scan/REPORT.txt).

The physical-tested **XWNQ90** completes native pool and page-table sizing
and stops before consuming descriptors or allocating page tables. Both
display modes and a 46-checkpoint trace pass in xemu; the physical checkpoint
is photo-confirmed. See the [memory sizing report](outputs/native-windows-physical-size/REPORT.txt).

The physical-tested **XWNA90** permits the first 28 native page-table
allocations, with checks before and after the loop. Emulator validation
includes each page write and refusal to use a mapped candidate; the physical
checkpoint is photo-confirmed. See the [page-table report](outputs/native-windows-physical-pt/REPORT.txt)
and [boot-screen milestones](outputs/native-windows-physical-pt/BOOT-PROGRESS.txt).

The physical-tested **XWNO90** maps 504 initial nonpaged-pool pages, then
halts before pool initialization and PFN setup. Both display modes and
an instruction trace pass in xemu; the physical checkpoint is photo-confirmed. See the
[pool mapping report](outputs/native-windows-physical-pool/REPORT.txt).

See [hardware status](outputs/native-windows-nt5-kernel/HARDWARE-PREFLIGHT.md),
[latest diagnostic](outputs/native-windows-physical-pool/REPORT.txt), and
[development plan](outputs/native-windows-development-plan.md).

## Source and reproduction

This repository stores our source changes as an ordered patch series against
ReactOS commit `afc0127e8f937ab68503d715d948844973756aa1`, plus build wrappers,
validation tools and reports. The full series and resulting source tree are
in [patch-check-0036.json](outputs/native-windows-physical-pool/patch-check-0036.json).
Use `python tools/apply-series.py --source PATH --manifest MANIFEST` on a clean
checkout at that exact upstream commit. The script checks the clean baseline,
applies the ordered patches and verifies the resulting Git tree.

Existing build scripts retain Paul's local Windows/WSL paths and pinned
RosBE 2.2.1 compiler. They require local toolchains and user-supplied Windows,
Xbox firmware, dashboard and test media. These are not a self-contained SDK.
Most diagnostic packages also require the preceding preserved binaries.

## Repository contents

Windows binaries, ISOs, registry hives, console firmware/EEPROM, dashboard
archives, disk images, packet captures, raw memory and local scratch data are
excluded. Photos and detailed run dumps remain local; summarized validation
records are tracked. Physical FTP passwords are supplied through the process
environment. Local emulator scripts use the fixture's default credentials.

Preserve the working softmod and dashboard. Hardware probes are manually
launched and photographed; current probes do not automatically return to the
dashboard. Do not write emulator disk images onto the physical Xbox drive.
No native Windows FATX mount or physical Windows boot volume is proven yet.

Paul restarts to the dashboard after each diagnostic photo. Treat receipt
of a photo as restart confirmation; only raise dashboard availability if
FTP remains unavailable after a retry. Physical launches remain manual.
