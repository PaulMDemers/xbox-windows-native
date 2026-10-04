# Native Windows on the original Xbox

Experimental native Windows 2000 bootloader/HAL and driver development for a
64 MiB original Xbox. Windows runs directly on the Xbox CPU; xemu is the
host-side test harness.

## Current evidence

- The isolated physical F launcher now passes an ordinary emulator desktop,
  native read/write probe and normal restart, with a clean cold disk audit.
  All 6,493 installation files are staged and readback-verified on the physical
  console. The user observed Windows followed by a reboot to UnleashX, but no
  native probe result was saved. The second physical test reveals STOP B4:
  Windows cannot initialize graphics. The startup report remains untouched.
  An emulator-validated video diagnostic has now been launched on hardware.
  Physical desktop and the bounded native storage probe have not passed. See the
  [physical F deployment](outputs/native-windows-physical-f/README.md).
- Extended F emulator milestone: native Windows desktop on a 250 GB FATX disk,
  verified reads/writes beyond LBA28, and two normal restart cycles with clean
  cold allocation, binary and registry audits. The actual console's F geometry
  is confirmed by an automated metadata probe; physical Windows storage remains
  untested. See [extended F results](outputs/native-windows-extended-storage/REPORT.md).
- Physical console: Windows kernel entry, processor initialization, HAL base
  setup, RTC calibration, clock setup and partition-hook registration and BIOS page allocation passed.
- Preserved physical baseline: **XWN390**. Windows 2000 draws its original
  boot graphic on the console after MM/executive phase zero and HAL phase one.
  The photo confirms the intended stop before native storage initialization.
  The later F installation reaches a graphics-initialization failure; a working
  physical desktop remains unverified.
- Private emulator fixtures have reached a Windows 2000 desktop with NTFS,
  USB input, framebuffer, networking and experimental audio. Those results
  do not establish physical hardware compatibility.

As of 4 October 2026, emulator-only work also reaches the interactive desktop
with Windows installed directly on the existing **FATX E volume**. It uses the
research FATX filesystem driver, not a virtual filesystem or a mounted NTFS
image. Paging-file translation and native image-read alignment fixes restored
storage integrity and USB driver loading. Repeated boots pass bounded disk,
memory and GUI checks; cold audits verify 3,452 immutable Windows files.
See the [FATX paging](outputs/native-windows-fatx-paging/REPORT.txt),
[USB image-read](outputs/native-windows-fatx-image-read/REPORT.txt) and
[volume-flush](outputs/native-windows-fatx-flush/REPORT.txt) evidence.
The emulator now completes a normal UI shutdown and displays Windows' genuine
"It is now safe to turn off your computer" screen. The final HAL halt has no
bugcheck; automatic electrical power-off is not implemented. See the
[boot-video ABI](outputs/native-windows-bootvid-nt5/REPORT.txt) and
[shutdown display](outputs/native-windows-bootvid-framebuffer/REPORT.txt) fixes.
The 40 MiB paging-pressure probe passes eight complete retention checks on a
fragmented pagefile. A separate debugger trace observes native pagefile read
submissions. FATX name-boundary, shrink/regrow, rename and deletion checks also
pass after fixing the 42-byte name conversion. See the
[paging-pressure report](outputs/native-windows-paging-pressure/REPORT.txt) and
[filename repair](outputs/native-windows-fatx-name-boundary/REPORT.txt).
FATX's 42-byte component limit remains an application-compatibility constraint;
general non-ASCII filename behavior remains unverified. The updated HAL and
boot-video path also pass an independent
[NTFS desktop/shutdown regression](outputs/native-windows-ntfs-shutdown/REPORT.txt).
File and registry counters survive a full FATX shutdown and cold restart in
the 1024x576 layout, with matching offline values and clean integrity checks:
[persistence evidence](outputs/native-windows-fatx-persistence/REPORT.txt).
Further same-directory rename tests expose a crash and then a delayed-write
failure. Patches 0060-0062 are **experimental**, with failed trials preserved;
they do not replace the verified 0059 persistence baseline. See the
[rename investigation](outputs/native-windows-fatx-rename-boundary/REPORT.txt).

The next bounded hardware candidate has reached a genuine Windows boot bitmap
in both tested emulator display layouts, stopping before storage. After
hardware access resumed, **XWN390** was uploaded and all 33 files read back.
The supplied photo now confirms its native boot graphic and XWN390 halt.
See the [boot-video candidate](outputs/native-windows-physical-bootvideo/REPORT.txt).
The user selected **F:** on the upgraded physical drive for Windows. A
[storage inventory](outputs/native-windows-physical-storage-preflight/REPORT.txt)
passed physically: 250 GB disk, F: with 94.65 GiB free and 64 KiB clusters.
The extended loader/HAL now validate the partition table and expose F, with
large-LBA native I/O tested in xemu. The file-only physical installation is
staged in new F paths, preserving the existing games and partitions.

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

The physical-tested **XWNJ90** reconciles the native descriptor update on
our pinned memory layout, restoring 622 pages omitted by a repeated
subtraction. It validates mappings, page records and the original extent,
then halts before free-page lists. Emulator validation passed; the physical
checkpoint is photo-confirmed. See the [descriptor accounting report](outputs/native-windows-physical-pfncommit/REPORT.txt).

The physical-tested **XWNG90** runs the complete native descriptor walk to
build free-page lists and mark reserved pages in use. It checks every PFN
and color-list word, preserves all 20 loaded images and stops before the
remaining MM initialization. Emulator validation passed; the physical checkpoint
is photo-confirmed. See the [free-page list report](outputs/native-windows-physical-freelist/REPORT.txt).

The physical-tested **XWNY90** finalizes PFN flags, restores the loader's
original descriptor extent and initializes system-PTE caches. It stops
before executive-pool initialization and process-page allocation. Emulator
validation passed; the physical checkpoint is photo-confirmed. See the [system-PTE report](outputs/native-windows-physical-sysptes/REPORT.txt).

The physical-tested **XWNZ90** initializes executive-pool descriptors and
allocates/zeros the first process page table and working-set page. It stops
before working-set publication and process initialization. Emulator checks
passed; the physical checkpoint is photo-confirmed.

The physical-tested **XWNW90** lets native process address-space initialization
return, then verifies the process/thread state, working-set and hash pages,
and all PFN records. It stops before further MM initialization and storage.
Emulator checks passed; the physical checkpoint is photo-confirmed.

See [hardware status](outputs/native-windows-nt5-kernel/HARDWARE-PREFLIGHT.md),
[latest diagnostic](outputs/native-windows-physical-processinit/REPORT.txt), and
[development plan](outputs/native-windows-development-plan.md).

## Source and reproduction

This repository stores our source changes as an ordered patch series against
ReactOS commit `afc0127e8f937ab68503d715d948844973756aa1`, plus build wrappers,
validation tools and reports. The full series and resulting source tree are
in [patch-check-0059.json](outputs/native-windows-fatx-name-boundary/patch-check-0059.json).
The bounded physical candidate retains its separate patch-0046 manifest.
The later experimental rename series is recorded separately in
[patch-check-0062.json](outputs/native-windows-fatx-rename-boundary/patch-check-0062.json).
Use `python tools/apply-series.py --source PATH --manifest MANIFEST` on a clean
checkout at that exact upstream commit. The script checks the clean baseline,
applies the ordered patches and verifies the resulting Git tree.

Existing build scripts retain Paul's local Windows/WSL paths and pinned
RosBE 2.2.1 compiler. They require local toolchains and user-supplied Windows,
Xbox firmware, dashboard and test media. These are not a self-contained SDK.
Most diagnostic packages also require the preceding preserved binaries.

The emulator-only **XWN290** candidate completes MM phase zero without
debugger assistance. Both display modes, 1388 import bindings, code audits,
free/color-list checks and five injected errors pass. Physical testing is
pending; no hardware upload occurred during the emulator-only session. See
[MM completion report](outputs/native-windows-physical-mmcomplete/REPORT.txt).

The emulator-only **XWN390** reaches Windows' original graphical boot screen
through the FATX loader path without debugger assistance, in both display
modes. It completes executive phase zero and HAL phase one, then halts before
storage initialization. The physical result remains XWNW90; this new candidate
has not been uploaded. See [boot-video report](outputs/native-windows-physical-bootvideo/REPORT.txt).

Native FATX runtime work uses a separate research filesystem driver alongside
Microsoft's Fastfat. The loader's Xbox ARC identity fix reaches graphical logon
on a private FATX system volume. The paging-file offset repair now passes a
full desktop/endurance run: 4 MiB disk verification, 8 MiB memory retention and GUI
response, with a clean cold filesystem audit and 3,452 unchanged system binaries.
The fragmented paging-file test also passes across 384 disk regions, with an
intact interleaved guard file. Repeat boot and USB keyboard/mouse input also
pass after the image-paging tail fix. Later volume-flush, HAL paging-notification
and boot-video repairs complete shutdown to the manual power-off screen;
all of these results are emulator-only. See the
[image-paging report](outputs/native-windows-fatx-image-read/REPORT.txt). See the [paging repair](outputs/native-windows-fatx-paging/REPORT.txt)
and its [source manifest](outputs/native-windows-fatx-paging/patch-check-0051.json).
The original NTFS emulator desktop fixture is preserved. The focused mapped-file extension test now passes, including rejection
of mapped-file truncation. See the [FATX boot report](outputs/native-windows-fatx-boot/REPORT.txt)
and [section-growth results](outputs/native-windows-fatx-cachefix/REPORT.txt).

## Repository contents

Windows binaries, ISOs, registry hives, console firmware/EEPROM, dashboard
archives, disk images, packet captures, raw memory and local scratch data are
excluded. Photos and detailed run dumps remain local; summarized validation
records are tracked. Physical FTP passwords are supplied through the process
environment. Local emulator scripts use the fixture's default credentials.

Preserve the working softmod and dashboard. Hardware probes are manually
launched and photographed; current probes do not automatically return to the
dashboard. Do not write emulator disk images onto the physical Xbox drive.
Native Windows FATX mounting and bounded file/mapping tests now work in the
emulator. Full FATX system-volume boot now passes a bounded desktop/endurance test;
long-term stability and a physical Windows boot volume remain unproven.

Paul restarts to the dashboard after each diagnostic photo. Treat receipt
of a photo as restart confirmation; only raise dashboard availability if
FTP remains unavailable after a retry. Physical launches remain manual.

The full FATX desktop also passes in the firmware 1024x576 display layout,
including USB input and cold binary checks: [wide-mode evidence](outputs/native-windows-fatx-wide/REPORT.txt).
The [power-path investigation](outputs/native-windows-power-isolation/REPORT.txt)
records the earlier shutdown wait. The subsequent
[HAL repair](outputs/native-windows-hal-paging/REPORT.txt) and
[boot-video repair](outputs/native-windows-bootvid-framebuffer/REPORT.txt)
resolve that tested path through the final manual power-off screen.
