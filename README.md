# Native Windows on the original Xbox

Experimental native Windows 2000 bootloader/HAL and driver development for a
64 MiB original Xbox. Windows runs directly on the Xbox CPU; xemu is the
host-side test harness.

## Current milestone: 0.1.0

For post-release installed state and remaining work, see the
[current overall status](outputs/engineering-notes/STATUS.md) and
[continuation note](outputs/engineering-notes/CONTINUATION.md). The October11
physical preview combines FATX0101 with tested RAM-backed software video118/
shared158 and genuinely installed ACI207 audio build004. Immutable0.1.0 remains
unchanged with0088. See [combined physical results](outputs/demo-physical253/REPORT.md)
and [unchanged-driver repeat](outputs/demo-audition255/REPORT.md).

The six audio API phases and five GDI samples passed bounded physical checks.
The first combined boot changed six inactive ACI registry values; its original
binding-equality failure is preserved with a narrow raw-hive review. The next
boot passed exact binding equality. Both retained clean allocation and protected
file/hive checks. The user heard the login sound and subsequently confirmed the louder left/right/both
tone sequence in diagnostic256. The quiet sequence was unheard; exact speaker
routing remains unconfirmed. Ftdisk49 remains a strict
whole-boot failure, so this preview is not a newly qualified release.

A [private overlay package](outputs/demo-package254/README.md) assembles twice to
identical hashes with readback verification. It is not a complete Windows installer
or a full source rebuild. No speculative PCI/USB prototype is installed. The
UnleashX root Windows entry is present. Known unsupported-device wizards remain.

Software video reduces redundant text uploads in the measured cases; this is
not GPU acceleration or a desktop-frame-rate claim. Native GPU work continues
through [matched emulator texture release/reuse](outputs/release-pair282/REPORT.md)
and the [next cache-disposal integration](outputs/disposal-boundary287/NEXT.md). These
owned emulator experiments do not grant native Windows GPU ownership.
1080i and other new video modes remain unqualified.

The native physical desktop now passes bounded storage soaks and two actual
Paint saves/reopens, with independent post-reboot bitmap, allocation, binary
and registry-hive checks. The user confirms ping works. Window dragging is
visibly slow; display performance and additional modes are the next priorities.
One earlier Paint freeze remains unexplained and has not repeated in the later
manual session. This is an experimental usable milestone, not general stability.

See the [0.1.0 release and recovery bundles](outputs/release-0.1.0/README.md),
[FATX/platform handoff notes](outputs/engineering-notes/README.md), and
[video development plan](outputs/video-next/PLAN.md). The exact qualified
filesystem is candidate0088, with the dimensions/trace miniport and physical HAL.
The chronology below includes superseded candidates and their failures.

Post-release engineering: [fresh component builds](outputs/reproducible-build/README.md),
[public repository preparation](outputs/public-release/PLAN.md),
[xemu upstream inventory](outputs/upstream-xemu/README.md), and
[reusable Xbox development skill](outputs/developer-skills/README.md).
The repository remains private. Fresh builds now produce seven native components
and the Cromwell launcher; their eight-file overlay packages identically on
repeat assembly. Complete bootable-system creation, broad runtime qualification
and byte-identical compiler outputs remain open work.

The rebuilt overlay has now passed its [first emulator boot and GDI workload](outputs/rebuilt-overlay-validation/README.md).
Broader runtime and physical qualification remain open.

Post-release repeat-boot maintenance now passes [two physical boots](outputs/video-trace-reuse-settled/README.md)
without resetting the diagnostic trace between them. Candidate0093 is installed;
the trace file remains required. Normal startup is restored. The original0.1.0
recovery/tag and qualified FATX remain unchanged; this is not a video speedup.

Post-release video investigation now [records actual uncached framebuffer mappings](outputs/video-mapping-audit/README.md)
on hardware. An [owned direct-RAM prototype](outputs/video-direct-map/README.md)
failed the strict shutdown-popup audit in two synchronous-startup runs. A
[detached startup experiment](outputs/video-startup-detached/README.md) now passes
one ordinary strict emulator audit with the same driver and no popup waiver.
This supports a launcher timing hypothesis, not a confirmed root cause. The
[new display replacement](outputs/video-surface-lifecycle/README.md) separately
tests surface cleanup in pinned ReactOS source; the installed display DLL is
Microsoft's implementation. Its graphics checks pass, but the shutdown popups
recur. A [resolved shutdown trace](outputs/video-shutdown-resolved-targets/README.md)
identifies an unfinished audio-device installer as a lead to investigate.
Further [ordinary isolation tests](outputs/video-installer-isolation/README.md)
advance that queue to the GPU, whose boot service works but whose matching PnP
installation is incomplete. Popup behavior remains intermittent.
Neither experiment has been deployed to hardware.
Candidate0093 is restored and hash-verified. No rendering speedup is claimed.

## Development evidence and history

- **Physical Windows 2000 desktop confirmed:** keyboard, mouse, drive browsing,
  Notepad and Calculator work on the Xbox. Cycle009 passed a bounded native
  FATX write/flush/reopen test with independent FTP payload verification.
- **Not stable yet:** cycle010 produced repeated delayed writes, corrupted
  appended setupapi.log data, and STOP 0xA. Its trace miniport remains the
  physical baseline; the normal miniport still fails with B4 on hardware.
  Paint's separate divide-by-zero display fix now also passes user-observed
  physical startup, but a subsequent Save attempt froze Paint and the system.
  The save hang is under investigation; startup success is not application stability.
  A deferred-write buffer fix improves emulator stress; replaying the physical
  registry exposed short paging writes and writes after truncation. A new
  filesystem candidate now passes mapped/async stress, restart and cold audits
  without new delayed-write events in that emulator run. Physical cycle011
  crashed during boot before its test started. **Cycle012 now passes on hardware:**
  cached append, 30 mapped/truncate cases and 32 MiB asynchronous writes, with
  exact payload readback after normal restart and no new delayed-write events.
  This is one bounded passing run, not proof that the earlier cache-list crash
  is resolved. **Cycle013 failed during the longer background soak** with
  STOP 0xA and subsequent on-disk corruption of the filesystem driver and WMI
  repository. A separate read-only Xbox snapshot confirms invalid FAT chains.
  That damaged install was held with automatic test startup disabled until the
  scoped recovery described below. The equivalent low-allocation emulator soak passed, with a recorded
  host-space interruption. A new high-allocation emulator run now fails during
  WMI rename; its crash dump is preserved for cache-mapping diagnosis. It has
  not yet been shown to share the physical crash's root cause.
  An isolated rename/deletion regression now identifies obsolete cached writes
  to deleted directories. The new0083 candidate passes that previously failing
  emulator regression, the300-case storage soak, normal restart,3439 immutable
  binary checks and nine registry hives, with no new delayed-write events.
  A subsequent rotation test exposed a deleted file still discoverable through
  its cached file record. Candidate0086 now excludes fully unlinked records
  from lookup and prevents stale metadata updates or repeated chain deletion.
  Two qualified emulator boots pass192 rotation cycles,191 observed cluster
  reuse cases, persistent130-file guards,600 mapped/truncate cases and two
  five-minute soaks, with clean cold audits and no new delayed-write events.
  A stronger dirty-replacement test then reproduced corruption of reused storage.
  Candidate0088 serializes chain retirement with paging I/O and prevents late
  cached writes from following freed chains. Its unchanged regression passes
  32 dirty replacements, handle/mapping lifetime and 66 cold-verified files.
  The persisted second boot also passes:66 retained files, another96 rotations,
  300 mapped/truncate cases and a fifteen-minute soak, with clean cold audits
  and zero new delayed-write events. All owned emulator processes are closed.
  The read-only full-F hardware capture now completed with automatic dashboard
  return. Its allocation audit isolates six affected Windows/test files and one
  orphan cluster; the full FAT matches the earlier crash snapshot. Scoped
  metadata repair and Windows restoration then passed on the physical console.
  The repair changed five exact directory sectors without changing the FAT or
  freeing data clusters. Independent full-volume rescans match the rehearsal;
  the restored install passes 3,439 binary checks and nine registry hive audits.
  Candidate0088 then passed a short physical cache trial:30 mapped/truncate
  cases,32 MiB asynchronous pressure,normal restart and exact payload readback.
  Post-reboot binaries,hives and the full allocation map remain clean, with no
  new delayed-write events. The subsequent300-case/five-minute hardware soak
  also passed with normal restart, intact new and archived payloads,3439 binary
  checks,nine registry hives and a clean full allocation map. A later15-minute
  physical run also passed300 cases,prior-file persistence,normal restart and
  the same full audits with zero new delayed-write events. The user also confirmed
  repeated Notepad,Calculator,Solitaire and Command Prompt use, two file saves
  and graceful shutdown. Those manual files have not been independently read
  back after reboot. Ftdisk49 and
  volume-space warnings remain. This is bounded evidence, not general stability;
  automatic startup is disabled on the dashboard.
  See the
  [hardware preflight kit](outputs/native-windows-fatx-preflight/README.md).
  See the [scoped recovery and hardware trial](outputs/native-windows-fatx-recovery/README.md)
  for the recovery evidence and latest physical test outcome.
  See [allocation evidence](outputs/native-windows-fatx-forensics/REPORT.md).
  See [desktop stability evidence](outputs/native-windows-physical-f/DESKTOP-STABILITY.md)
  and [cache test results](outputs/native-windows-physical-f/CACHE-STABILITY.md).
- Extended F emulator milestone: desktop on a 250 GB native FATX disk, writes
  beyond LBA28, and normal restart cycles with clean cold audits. These bounded
  tests do not establish general physical storage reliability. See
  [extended F results](outputs/native-windows-extended-storage/REPORT.md).
- Physical console: Windows kernel entry, processor initialization, HAL base
  setup, RTC calibration, clock setup and partition-hook registration and BIOS page allocation passed.
- Preserved physical baseline: **XWN390**. Windows 2000 draws its original
  boot graphic on the console after MM/executive phase zero and HAL phase one.
  The photo confirms the intended stop before native storage initialization.
  This original boot-video checkpoint remains preserved alongside the later
  physical F desktop milestone.
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

Preserve the working softmod and dashboard. Early hardware probes required
manual launch and photographs; later bounded tests support authorized FTP launch
and automatic dashboard return. Do not write emulator disk images onto the physical Xbox drive.
Native Windows FATX mounting and bounded file/mapping tests now work in the
emulator. Full FATX system-volume boot now passes a bounded desktop/endurance test;
long-term stability remains unproven. Physical F desktop boot is confirmed above.

Paul restarts to the dashboard after each diagnostic photo. Treat receipt
of a photo as restart confirmation; only raise dashboard availability if
FTP remains unavailable after a retry. Later FTP launches are explicitly authorized;
never launch the currently damaged Windows installation before recovery.

The full FATX desktop also passes in the firmware 1024x576 display layout,
including USB input and cold binary checks: [wide-mode evidence](outputs/native-windows-fatx-wide/REPORT.txt).
The [power-path investigation](outputs/native-windows-power-isolation/REPORT.txt)
records the earlier shutdown wait. The subsequent
[HAL repair](outputs/native-windows-hal-paging/REPORT.txt) and
[boot-video repair](outputs/native-windows-bootvid-framebuffer/REPORT.txt)
resolve that tested path through the final manual power-off screen.
