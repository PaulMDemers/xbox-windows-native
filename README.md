# Native Windows on the original Xbox

Experimental native Windows 2000 bootloader/HAL and driver development for a
64 MiB original Xbox. Windows runs directly on the Xbox CPU; xemu is the
host-side test harness.

## Current evidence

- Physical console: Windows kernel entry, processor initialization, HAL base
  setup, RTC calibration, clock setup and partition-hook registration and BIOS page allocation passed.
- Latest physical checkpoint: **XWNL90**. Native mapped-page PFN initialization
  completed: 639 populated records and 64 color-list heads, followed by
  a successful native TLB flush. Free-page lists, storage drivers
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

The physical-tested **XWNU90** completes native nonpaged-pool initialization
and its expansion-PTE setup, then stops before PFN backing allocation.
Both display modes, the complete pool-write comparison and rejection tests
pass in xemu; the physical checkpoint is photo-confirmed. See the
[pool initialization report](outputs/native-windows-physical-poolinit/REPORT.txt).

The physical-tested **XWNE90** allocates and clears 90 PFN-database pages
and one color-table page, then stops before populating those structures.
Both display modes, allocation tracing and rejection checks pass in xemu;
the physical checkpoint is photo-confirmed. See the
[PFN backing report](outputs/native-windows-physical-pfn/REPORT.txt).

The physical-tested **XWNL90** initializes mapped-page PFN records and color
heads, then returns from the native TLB flush. It stops before free-page
list construction. Both display modes, the complete page-record model,
execution trace and rejection tests pass in xemu; the physical checkpoint is
photo-confirmed. See the [mapped PFN report](outputs/native-windows-physical-pfnmap/REPORT.txt).

The next candidate **XWNJ90** reconciles the native descriptor update on
our pinned memory layout, restoring 622 pages omitted by a repeated
subtraction. It validates mappings, page records and the original extent,
then halts before free-page lists. Emulator validation passed; physical
testing is pending. See the [descriptor accounting report](outputs/native-windows-physical-pfncommit/REPORT.txt).

See [hardware status](outputs/native-windows-nt5-kernel/HARDWARE-PREFLIGHT.md),
[latest diagnostic](outputs/native-windows-physical-pfncommit/REPORT.txt), and
[development plan](outputs/native-windows-development-plan.md).

## Source and reproduction

This repository stores our source changes as an ordered patch series against
ReactOS commit `afc0127e8f937ab68503d715d948844973756aa1`, plus build wrappers,
validation tools and reports. The full series and resulting source tree are
in [patch-check-0040.json](outputs/native-windows-physical-pfncommit/patch-check-0040.json).
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
