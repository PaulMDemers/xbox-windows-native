# Physical cycle013: preserved allocation corruption

The physical 300-case test finished its mapped/truncate and 32 MiB asynchronous
write phases, then crashed during its five-minute background pause. The user
reported `0xA (0x10, 0x2, 0x0, 0x82423167)`. The kernel load base for this boot
has not been established, so no function attribution is claimed. Test payloads
still match their expected patterns after reboot. This is a failed stability
trial, despite cycle012's earlier bounded pass and complete binary audit.

FTP readback of `winnt/system32/drivers/xwnfatx.sys` returns 65536 bytes then
426; its first cluster contains UTF-16 WMI MOF text instead of an executable
header. A prefix matches the owned `cimwin32.mof` at byte454256, but the whole
cluster does not match that source slice. `CIM.REP` also reads short. The old
filesystem backup, current HAL and trace miniport retain their expected hashes.

## Read-only physical snapshot

The original nxdk tool in `main.c` opens Partition6 for read access only, verifies
its pinned start/size and FATX header, and reads the FAT plus bounded chains for
the Windows driver and WMI repository. Output uses new files beside the XBE on
E:. It does not repair FAT entries, reset WMI, or boot Windows. The result marker
means capture completed; it does not mean the captured filesystem is healthy.

Before physical use, emulator `fatx-forensics-002` verified every saved metadata
and cluster byte against the stopped disk. The run's top overlay has no F: data
extents. An earlier emulator attempt stopped at the partition-size guard because
the owned Xbox BIOS exposes only its LBA28 prefix; the tool now permits that
exact emulator prefix while using the pinned full-volume FAT geometry and
enforcing the actual read-handle bounds. Physical Partition6 reports the full
242055217152 bytes. Firmware and all raw files remain local and ignored.

XBE SHA256: `e87fb1840c812da2ca1287ceef0c5eb9134e18d192816824e1bda553b4ba0890`.
One physical launch at 2026-10-05 00:44:24 UTC returned to the dashboard. The
source F: volume was only read; outputs are `E:/Applications/XWNFatRO` and local
`artifacts/physical-013`. `physical-snapshot.json` records every file hash.

Captured metadata SHA256:
`c292ba76214ba2cb3a3475741fc6506348cde56fc7ee7f022285188b8a488bc1`.

- `xwnfatx.sys`: directory size167789, first cluster2154674, FAT entry zero
  (free). The saved cluster exactly matches the corrupt FTP prefix. Its absolute
  disk offset is149227560960 bytes, beyond LBA28.
- `CIM.REP`: directory size2686976, chain37 clusters/2424832 bytes: four clusters
  (262144 bytes) short. It ends at a valid end marker, rather than a read failure.
- `$WinMgmt.CFG`: size12, first cluster2160625 is also marked free.
- `xwnfatx.xwn-c11`: its original three-cluster chain remains valid.

`analyze-snapshot.py` inspects1374 entries in six captured directory clusters.
Those three entries are inconsistent; no chain overlaps are found among the
captured entries. This is not a whole-volume audit. It does not establish which
operation first freed or reused the affected clusters, and cannot rule out
cross-links involving uncaptured directories.

## Emulator comparison and next experiment

`nt5-physical-f-cache-soak-001` used the same production filesystem, helper and
cycle012 registry snapshots. It completed300 cases, pressure, five-minute soak
and normal restart; cold payload checks and3439 immutable binaries passed.
During a parallel attempt to create a full snapshot fixture, the host ran low
on disk space. That failed generated file was removed, the VM was paused/resumed,
and the final dashboard captured. No guest I/O error was recorded, but this
interruption prevents treating the run as a pristine qualification. Subsequent
fixtures use small overlays. The physical corruption was not reproduced.

The original emulator places Windows low on F:, whereas the physical install
is above LBA28. `prepare-high-allocation.py` creates a separate experiment with
the driver and WMI repository on fragmented high clusters, and marks otherwise
free lower clusters unavailable so new allocations occur in that region. It
preserves source hashes and verifies relocated file contents. It is a synthetic
allocator/layout test, not a clone of the physical disk or a hardware fix.

### High-allocation run001 failed in WMI rename

The new fixture SHA256 is
`18a72152df86ef61608836698758b0153ac365729518a89ed39ae93863d7d95c`.
Run `nt5-physical-f-high-allocation-001` launched at00:50:26 UTC, completed300
mapped cases and pressure, and crashed during the background soak. The screen
shows `0x1E (0xC0000005, 0x824C7A22, 0x1, 0x006FFFC8)`. Registers,60MiB of
physical RAM and the stopped disk overlay are preserved locally. This is an
emulator failure with a different stop code, not proof of the same corrupting
operation as physical013. The harness is closed and no VM remains running.

Page-table/PE analysis establishes kernel base`823dd000`. Matching kernel
symbols and instruction boundaries place the original fault at
`RtlUnicodeToOemN+0x5a`, writing to`006fffc8`. Both a saved CONTEXT and trap-frame
candidate agree on these registers. Caller frames lead through
`RtlUnicodeStringToOemString` to the filesystem's `vfatRenameEntry`, RVA`7cd6`
at loaded driver base`fe43b000`; matching COFF disassembly confirms that call.
The input name is`$WinMgmt.CFG.BAK`. Post-fault locals contain directory pointer
`006fffc6`, OEM output pointer`006fffc8`, and cache context`fe66ae08`.

The rename source ignores the Boolean result of `CcPinRead` before using its
output, and converts directly into the counted directory field. The captured
state does not record that Boolean result: a failed pin and corrupted cache
mapping must be distinguished at a breakpoint before selecting a fix. A later
fault occurred while rendering the bugcheck; the halt registers are not the
original rename registers. `analyze-crash.py` retains that distinction and stops
frame interpretation at trap transitions instead of treating pool links as
call frames.

Cold inspection finds the report ends at the same soak-start marker as physical013.
The preexisting relocated driver and CIM.REP chains are still valid, unlike
physical013. The newly allocated `$WinMgmt.CFG` points to a free FAT entry;
new test files are absent from the persisted root directory. Unflushed metadata
after a crash can account for some of these differences, so these are not proof
of the same corruption. The strict cold audit fails at that CFG chain after
475 files/197 immutable binaries; no full-audit pass is claimed.

Next: repeat this exact emulator fixture with a breakpoint at the rename
`CcPinRead` return, capture its result/output pointers and BCB/VACB state, then
test a targeted repair against both low and high allocation cases. Preserve the
bad physical install while establishing whether the cache pin failed or its
mapping was already corrupt. Host C: has about1.1GiB free; use bounded deltas and
one temporary raw conversion at a time.

Keep the physical install unlaunched until the corrupting operation is understood
and restoration can be verified. Cycle014 Paint testing remains gated off.
Do not overwrite the damaged driver or reset WMI merely to obtain another boot.

## Rename integration and deleted-directory regression, October 5

High-allocation run002 with the original `f686...` driver completed the 300-case,
32 MiB and five-minute soak and restarted normally. Cold payload checks and the
bounded driver/WMI chains pass; no whole-volume audit is claimed for that run.
The exploratory rename-pin trace recorded no hits. Its cleanup encountered an
asynchronous GDB stop packet where it expected an acknowledgement; the owned VM
was subsequently terminated by the harness. This was a host trace failure, not
an observed cache-pin result. The cleanup code now accepts the pending stop
packet and records cleanup failures. That trace cleanup change has not yet been
exercised against a new debugger session. The intermittent failure remains open.

Source history inspection confirmed that experimental rename patches0060-0062
were excluded from the production0079 chain after their earlier delayed-write
failure. `patch-check-0080.json` integrates them after0079, producing tree
`423635deed2cbad9e2f88a642ab1849fccac6c08` and driver
`4112cc4c15bf3aaa97bd5450c8cdfde3bba01a412e8ec2b53c529be7d25abe6c`.
All127 native imports resolve. This preserves the original rename name/index
repairs while adding the intervening paging fixes; it is not a new claim that
the original physical corruption is explained.

Run `nt5-physical-f-high-allocation-rename-001` completed the same cache soak and
normal restart. All3439 immutable binaries, allocation ownership, test payloads
and registry checks pass after shutdown. One brief RAM snapshot and framebuffer
captures paused/resumed the guest; there were no execution breakpoints or guest
data patches. The cold auditor now explicitly verifies the pinned fixture's
synthetic bad-cluster reservations remain unchanged and unclaimed, rather than
treating them as orphaned allocations. Other unclaimed allocations still fail.
Its first attempt used an unsuitable qemu-img dd range; that host failure is
preserved in the run directory. The corrected bounded raw view passes.

The unchanged13666-byte rename probe was then staged before the soak. It tests
case-only42-byte rename, same-directory rename to42 bytes, cross-directory move,
reopen/data comparison and deletion. Run `nt5-physical-f-high-allocation-r2`
reports zero API failures and passes the cache soak and full cold audit, BUT
visibly reports delayed writes for `xwnfstest\sub`. Current-boot event records40
and44 confirm warnings for both deleted test directories; records42/43 are
Ftdisk50. Consequently this candidate FAILS the regression despite its cold
checks. Screenshots, stopped disk and complete event logs are retained locally.
The preceding longer run name failed before boot because Windows could not open
the deep backing path; it supplies no runtime evidence. Short run IDs avoid it.

The cleanup code uninitializes an internal directory stream with a NULL truncate
size, then zeroes the FCB sizes and frees the allocation. Patch0081 moves those
size changes before uninitialization and supplies the zero truncate size to the
internal stream too. This requests cache invalidation before its backing clusters
are released; it does not turn failed writes into success. The API contract is
documented by [Microsoft](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/ntifs/nf-ntifs-ccuninitializecachemap).
The new tree is `3c98ddea1f3bfa3d1bfccce9e24644724d7bf2bc`; the separately saved
driver is `00c3330225ff48843e9626c1c51228f5d06d587aa78d7535033c2c45dafec98c`.
Build and all127 import checks pass. Runtime qualification is recorded below
after the identical rename-plus-soak experiment completes.

Run `nt5-physical-f-high-allocation-r3` with0081 also FAILS: the same deleted
directory popup is visible. The complete rename API log,300-case soak, restart,
3439 binaries, allocation and registry audit still pass. Therefore the zero
truncate change is insufficient and is not promoted. Its separate image remains
available for comparison; the verified physical artifacts have not changed.

Patch0082 adds a bounded in-memory failure ring to the failed0081 driver. It
records status, IRQL, IRP/FCB flags, write range, file/allocation sizes, cluster,
directory indices and path when VfatWrite returns failure. It leaves the original
status intact and does no disk logging. This is a diagnostic build, not a fix.
`read-write-trace.py` reads the ring from an owned emulator RAM snapshot and
resumes the guest, deleting the temporary raw dump after saving decoded records.
The source tree is`b28c040505d60a19debd1700dc2e34a598623110`; the driver hash is
`91860fede1e2432a7d84e4fb34196d2c0a02b821341a5729318fab2c396c9fcd`.

### Captured failure and narrow candidate0083

Exploratory runr4 records four failed writes, two each for`\xwnfstest\sub` and
`\xwnfstest`. Every record has status`C000000D` (invalid parameter), IRQL0,
IRP flags`43`, FCB flags`2` (delete pending), zero open handles, zero file size,
zero valid-data length and zero allocation size. The writes are4096 bytes at
offset0, while the stale first-cluster fields remain2144206 and2144202. Thus
the write path is rejecting obsolete cached pages for deleted directory streams.
`deleted-directory-write-trace.json` preserves the decoded evidence. The VM was
closed intentionally after capturing the trace; this diagnostic run is not a
completed soak or a cold-consistency qualification.

Patch0083 branches from0080, excluding both the unsuccessful0081 cleanup change
and0082 instrumentation. Under the paging resource, it discards paging writes
only for a directory that is delete-pending, has zero open handles, and has zero
file size and allocation. Volume/FAT streams and live-directory writes retain
their original checks. This avoids attempting I/O through the obsolete cluster
field; it does not mask errors on live data. The source tree is
`f0faab3070de3d8980bc7cf04f6407f9d1978fe1`, with driver
`4aa035e6faa6b23ab7bfe78c6da10875eb8d789854c593983e0275c9141e2396`.
All127 native imports resolve. Runr5 uses the same rename probe and long soak.

Host space was recovered by losslessly compressing one closed790467338-byte
CPU trace to26753011 bytes. The uncompressed SHA256 was checked before and after
compression before removing the original; the compressed evidence remains in
its original run directory. See`retained-trace-compression.json`. No disk images,
physical snapshots or source artifacts were deleted.

### Candidate0083 validation result

Run `nt5-physical-f-high-allocation-r5` launched at02:16:32 UTC and returned
normally to the dashboard. It passes every required42-byte rename, case change,
cross-directory move, reopen/data comparison and deletion check. The300 mapped
cases,32 MiB asynchronous pressure and five-minute idle period also complete.
There are no observed delayed-write popups and no delayed-write/Ftdisk50 records
in the current boot; the event log records normal shutdown. Historic warnings
remain in the log and are not confused with this boot.

The stopped disk passes allocation/cross-link checks,3439 immutable binaries,
nine hive checks and exact test payloads. Synthetic reservations match the
original pinned high-allocation fixture and remain unclaimed. The qualifier in
`nt5-physical-f-high-allocation-r5-qualification.json` is PASS; the same tool
marks r2 and r3 FAIL despite their API/cold successes. No execution breakpoints
or guest data patches were used for r5; ordinary framebuffer captures briefly
pause/resume the emulator. Full ordered source replay, build,127 imports and
host script syntax checks pass. Whitespace checks cover host sources and applied
C source; literal patch context lines are not treated as source whitespace.

All owned guests are closed. Current WSL source is0083; the0080,0081,0082 driver
artifacts and all comparison fixtures are preserved. The original f686 physical
candidate is also preserved separately, while the actual physical driver remains
damaged. No hardware access, upload, restoration, WMI reset or Windows launch
was performed during these emulator experiments. The original physical013
corruption and intermittent WMI rename crash remain separate unresolved results.
Next validate repeated WMI-style replacement/rename and cluster reuse before
restoring the owned Windows installation and scheduling a new physical trial.

## Repeated rotation exposes a stale deleted-name lookup

The new emulator-only `rotate-probe.c` creates 130 persistent 65,537-byte guard
files, then performs 96 synthetic CFG backup/publish and cross-directory CIM
move/delete cycles. It checks file contents after each transition and uses
`FSCTL_GET_RETRIEVAL_POINTERS` to count cases where a newly allocated file starts
on the last cluster of a file just deleted. It never modifies the real WMI
repository. On subsequent boots it verifies the existing guards before doing
more work. The startup script stops on any failure, before the cache soak.

Run `nt5-physical-f-high-allocation-r6` with the unchanged0083 driver fails with
Win32 error183 on the second CIM move. The destination lists no files. The first
move and delete had succeeded; the test had not yet reached its16-cycle progress
marker. All130 guard files still match after normal UI-initiated restart, but
the rotation/soak qualification is FAIL. Diagnostic runs r7 and r8 reproduce it.

The0084 RAM ring was overwritten by unrelated background WMI renames. The0085
filter retains only lookups beneath `\xwnrotate`. Its five captured records show
the first destination absent, then the next lookup returning the previous FCB
with `FCB_DELETE_PENDING` set and the old first cluster2144474. The directory
entry has been removed, but its cached FCB is still discoverable by name. See
`stale-deleted-target-trace.json`. The diagnostic code changes no return status
and writes no trace data to the guest disk. Both diagnostic runs were closed
after normal UI restarts; neither is a passing soak test.

Patch0086 branches directly from0083, excluding0084 and0085. A true FATX unlink
marks the FCB `FCB_NAMESPACE_UNLINKED`; moves retain their live FCB. Name lookup
skips retired records while final reference release still removes and frees
them normally. Later metadata updates cannot overwrite the retired directory
slot, and a repeated delete cannot free its old cluster chain again. This is
distinct from delete-pending handles whose directory entry still exists.

Candidate source tree: `88a43630e6e20dba004a5f722819a3c071ac62ec`.
Driver: `artifacts/xwnfatx-unlinked.sys`, SHA-256
`f74b55b7f81c7ee4a983d91022c9132c22c683538fb996e5c21f8c7a290734bd`.
All77 ordered patches replay to that tree; the driver builds and resolves127
imports against the owned NT5 binaries. The unchanged rotation probe resolves15
imports. Run r9 passes all96 cycles,95 observed freed-cluster reuse cases,
130 guard comparisons,300 mapped/truncate cases,32 MiB asynchronous pressure,
the five-minute idle soak and normal automatic restart. Cold allocation checks,
3439 immutable binaries and nine hives pass. No delayed-write popup was observed
and no new delayed-write event was recorded. Its combined qualifier is PASS.

The first second-boot attempt, r10, deliberately halts in the existing one-shot
video logger: `E0580001(0D,4,C000003E,10)`. `XwnVideoTraceInit` requires all bytes
after the16-byte marker to be zero. Offset16 instead contains41, the previous
boot's record count. This is an omitted diagnostic reseed, not evidence of
another filesystem corruption. The screenshot, registers,60 MiB crash snapshot
and stopped disk are preserved; the stalled emulator was closed. That run is
not a passing repeat-boot test.

`prepare-rotate-reseed.py` preserves the original4096-byte trace, then creates a
new overlay changing exactly those4096 bytes back to the known seed. It verifies
readback and that the first-boot checkpoint is unchanged. It does not reinstall
Windows, reset WMI or alter the guard files, rotation state, driver or registry.
Run r11 uses this corrected second-boot fixture; its result is recorded below.

Run r11 is now closed and independently qualified PASS. Its unchanged probe
verifies the130 guards saved by r9, completes another96 rotations with96
observed freed-cluster reuse cases, then passes300 mapped/truncate cases,
32 MiB asynchronous pressure and the five-minute idle soak. Windows restarts
normally to the dashboard. Cold checks verify all130 guards, allocation
ownership,3439 immutable binaries and nine hives; no new delayed-write event
is present and no delayed-write warning was observed in the captures.
See `nt5-physical-f-high-allocation-r11-qualification.json` and its linked
rotation, payload, event and cold-audit reports. Together r9/r11 supply192
rotations,191 observed reuse cases and600 mapped cases across two boots.
The intervening diagnostic-seed stop r10 is excluded from passing results.
No debugger execution patches were used; framebuffer captures briefly pause
and resume the emulator. All emulator and audit processes are closed.

This supplies a concrete rename/deletion defect and a possible path to repeated
deletion of reused storage. It does **not** prove that the physical013 corruption
or earlier WMI cache-pin crash has this cause. No physical console access,
uploads, restoration or Windows launches were performed during this work.

### Gates recorded before the lifetime follow-up

- Exercise `MoveFileEx(..., MOVEFILE_REPLACE_EXISTING)` with a dirty cached
  destination, immediately reuse its released clusters for different contents,
  then apply memory pressure and idle before checking both files. The current
  rotation probe uses backup/rename/delete and does not cover this overwrite case.
- Verify that live open handles retain their sharing/delete-pending semantics;
  only fully unlinked records may disappear from name lookup. Include open
  mappings, close ordering, and propagation of real I/O failures.
- Repeat cold boots and longer persistence checks with the diagnostic seed
  lifecycle handled explicitly. Distinguish crash captures, diagnostic-only
  runs, reproducible candidates and physical tests in every result.
- Before physical restoration, retain the corrupt Windows/WMI evidence and
  audit the owned installation against verified source files. Restore only
  Windows-owned files, then qualify short writes, reuse and longer idle tests
  on hardware while preserving the dashboard, softmod and other partitions.


## Dirty replacement and paging lifetime (5 October 2026)

The new unchanged `lifetime-probe.c` closes the previously missing coverage:
replacement while a target has a non-sharing handle, delete-pending access
through surviving handles, mapping/file/view close ordering, and 32 replacements
of dirty cached destinations. Half also dirty a mapped view. Each replacement
immediately allocates different contents into released storage, with retrieval
pointers demonstrating reuse. Sixty-six deterministic files remain for pressure,
idle, cold-disk and subsequent-boot verification.

The earlier 0086 candidate fails this stronger test in r12. All handle tests and
32 reuse observations complete, but final verification fails; the stopped disk
confirms corruption of `reuse07.bin` and `reuse21.bin`. A delayed-write popup
names `target00.bin`, and 39 current-boot lost-write events are retained.

Diagnostic 0087 in r13 records 515 failing paging writes. The final 16 retained
records target `target26.bin`, with STATUS_C0000102, zero open handles and the
fully-unlinked FCB flag 0200. These writes still followed the retired first
cluster. r13 happens to pass its API and retained-file checks, but has a visible
warning and 36 current-boot lost-write events: **overall FAIL**. Both controls
were stopped through normal UI shutdown to the safe-to-power-off screen and
closed. Neither is a successful automatic-restart soak. See
`lifetime-failed-controls.json` and `lifetime-write-trace.json`.

Production candidate 0088 branches directly from 0086 and excludes 0087's trace.
True FATX unlink now holds the paging resource exclusively through chain
retirement. This waits for writes already holding that resource. Later paging
writes to fully unlinked ordinary files with no open handles complete without
following the obsolete chain. Merely delete-pending files with surviving
handles retain normal I/O; live file, volume and FAT checks remain in place.
The resource releases on the normal completion path. This is a targeted repair
for a reproduced storage-corruption mechanism, not general error suppression.

- Source tree: `adf9b3d166ef84630a48d7393fcc9fe3ce78f104`.
- Driver: `artifacts/xwnfatx-retired-write.sys`.
- SHA-256: `0ec6b5fdae65a1f85cba8c15021ba8095601d4462565b331329884526ff81336`.
- All 78 patches replay to that tree; build and 127 NT5 imports pass.
- Unchanged lifetime executable: `37b4f041bdb4e6f0090757fdb52bf28f1f3ddf1c9077e6d740fb9eeb0036af33`.

Run r14 qualifies PASS with 0088:32 dirty replacements and 32 observed reuse
cases; all handle/mapping checks; 66 retained files verified cold; 96 rotation
cycles with 95 reuse cases and 130 guards; 300 mapped/truncate cases; 32 MiB async
pressure; five-minute idle; normal automatic dashboard restart. Cold allocation,
3439 immutable binaries and nine hives pass. No delayed-write warning was
observed and no current-boot delayed-write event exists.

The r15 fixture retains r14's Windows/WMI/registry, driver, rotation state and
all persistent test files. It changes the test helpers/startup and resets only
the 4096-byte one-shot video trace, preserving the original trace separately.
Its new verifier checks the 66 previous files before the unchanged cache workload
and a fifteen-minute idle. r15 is now closed and qualifies PASS. The prior66
files match both during the second boot and in the final cold audit. Rotation
state2 contains96 additional cycles and96 reuse observations, with all130 guard
files intact. The second300-case mapped/truncate workload,32 MiB async pressure,
fifteen-minute idle and automatic dashboard restart complete. Allocation,3439
immutable binaries and nine hives pass; zero new delayed-write events and no
warning observed. No debugger execution patch was applied.

Together r14/r15 supply32 dirty replacements with32 reuse observations whose
results persist across reboot;192 rotation cycles with191 reuse observations;
600 mapped/truncate cases;64 MiB async writes; five- and fifteen-minute soaks.
The lifetime replacement loop ran once in r14; r15 verifies its persistent
results rather than counting them as32 additional replacements. Both complete
normal restart and cold audit. See the two `*-qualification.json` records.
The emulator and all owned build/audit processes have been closed.

### Hardware preparation and remaining limits

The next hardware experiment is the [read-only full-F metadata preflight](../native-windows-fatx-preflight/README.md).
It captures the whole FAT and live directory records through a read-only
Partition6 handle, with outputs on E beside its XBE. Emulator validation compares
6797 entries and 309 directory clusters against the stopped disk, independently
checks coverage, and confirms no F write extents. Analyzer tests detect a free
file chain, a crosslink and incomplete evidence. A complete capture alone does
not mean a healthy filesystem.

The launcher pins the qualified binaries, requires the ownership marker and
unchanged disabled Windows startup, and refuses blind relaunch. No hardware
access, upload, restoration or Windows launch occurred during this work.
Physical013's corrupt driver/WMI evidence remains preserved. Its original
STOP0xA and earlier cache-pin crash are not conclusively attributed to this bug.
The synthetic emulator disk is not a clone of the console's actual filesystem.

Before Windows boots again, use the new metadata evidence to identify all
allocation conflicts, review recovery scope and restore only Windows-owned
content from verified sources. Preserve unrelated files, partitions, dashboard
and softmod. Then test short writes first with the established physical HAL and
trace miniport, followed by replacement/reuse and longer idle tests. Hardware
I/O error propagation, power-loss recovery and extended uptime remain unqualified;
this work does not establish production filesystem reliability.

The lifetime probes use the documented file deletion and replacement contracts:
[DeleteFile](https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-deletefile)
and [moving/replacing files](https://learn.microsoft.com/en-us/windows/win32/fileio/moving-and-replacing-files).
The actual qualification evidence is from the owned NT5 emulator runs above.


### Reproduction and evidence boundaries

Use `patch-check-0088.json` with `tools/apply-series.py` on the pinned upstream
checkout. `Build-Rename.ps1 -Variant retired-write` builds the production
candidate. `Build-Lifetime.ps1`, `Build-LifetimeReboot.ps1` and `Build-LongSoak.ps1`
build the guest probes; the three import-audit reports pin their NT5 ABI checks.
The original0086 and diagnostic0087 drivers remain separate retained artifacts.

`prepare-lifetime.py --retired` constructs the first candidate fixture from the
owned high-allocation baseline. `prepare-lifetime-long.py` creates the subsequent
boot from the closed r14 disk, preserving all persistent state except the
explicit diagnostic reseed and updated test helpers. Each refuses to overwrite
existing fixture targets. The fixture manifests record source and result hashes.
These scripts require the locally owned media, toolchains and earlier fixtures;
the source repository intentionally does not distribute those binary payloads.

After the emulator closes normally, run `audit-lifetime.py --run RUN --expected
pass` (add `--reboot` for r15), `Audit-RotateRun.ps1 -RunId RUN -Boots N
-FilesystemDriver xwnfatx-retired-write.sys`, and `qualify-regression.py --run RUN
--events EVENTS --visual no-warning-observed --expected pass --rotation-boots N
--lifetime`. Supply the visual outcome from actual captures. A data-only pass
must never override an observed lost-write warning. Preserve failing run reports.
The qualifier requires the complete cold audit, current-boot event evidence and
normal EventLog shutdown together with the probe results.


## Full-F physical preflight (5 October 2026)

The separately authorized read-only preflight launched through dashboard FTP at
04:38:11 UTC and returned automatically. Collection completed at04:40:41 UTC.
No Windows launch or F repair occurred. All output was written beside the new
preflight app on E:. The capture includes6058 directory clusters and128098 live
entries, reconstructing6053 directories and122046 files.

The full FAT is byte-identical by SHA-256 to the earlier physical013 capture:
`c292ba76214ba2cb3a3475741fc6506348cde56fc7ee7f022285188b8a488bc1`.
There are777 error records across six distinct files:773 crosslink observations
represent387 unique shared clusters between the prior pressure-test file,
MMC3.tmp and System Information.lnk. The remaining records concern the known
filesystem driver and WMI chain damage. One cluster,2156751,is allocated without
a live owner. No allocation conflicts were found outside Windows/test files;
this is not a payload-integrity audit of unrelated content.

See `../native-windows-fatx-preflight/recovery-scope.json` for exact entry
locations, logical sizes, chains and the next repair steps. Ordinary deletion
is unsafe for the shared chains. Preserve raw affected contents, rehearse
entry detachment and ownership repair offline, then restore from verified
Windows sources and repeat full allocation/binary checks before a driver trial.
The physical install remains held. This result confirms the automated launch,
read-only capture and dashboard-return loop works for this preflight.
