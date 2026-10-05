# Deferred writes: emulator improvement, physical boot still failing

Patch0076 pins the caller's write buffer before handing an IRP to
CcDeferWrite. The callback can execute in another process; VfatGetUserBuffer
must then use the MDL's system mapping instead of the original user address.
If locking fails, VfatWrite returns the failure without transferring ownership
or queuing the deferred callback. This fixes a demonstrated defect, but has
not been established as the cause of the physical corruption or STOP 0xA.

The candidate filesystem is SHA256
`f8c1f66a4460034d6c78cdd186ac2c3471383362aaa2b69d2865ba803d1d7154`.
The preceding driver is
`a10cfaac19a526f48e0a85ebab961140130ba4e7e4a3660dad2f56fa2841d183`.
Build with Build-DeferredBuffer.ps1 after applying the series through 0076;
patch-check-0076.json records clean replay and reverse verification.

## Evidence

| Test | Old driver | Candidate |
|---|---|---|
| Compiled deferred branch with modeled process switch | Queues an unlocked buffer; reads unrelated bytes | Pins first; retains original bytes |
| Lock failure in compiled branch | Not applicable | Returns C000009A without queuing or transferring context |
| Ordinary xemu, cached append and 30 mapped/truncated files | Passed in initial light run | Passed in stress run |
| Ordinary xemu, identical 32 MiB asynchronous pressure workload | Mapped flush error87; asynchronous completion error998; stopped at 9 MiB | All writes, flush and readback passed |
| Candidate cold audit | Not claimed | 6,497 files, 3,439 immutable binaries; allocation ownership and registry checks passed |
| Physical cycle011 | Earlier cycle010 reached desktop, then delayed writes and STOP0A | STOP0A during boot, before startup stress program |

The full emulator runs used the isolated xemu `128-plus-extra` PCI resource
model, HALa3 and the exact trace413 miniport. No debugger execution changes
were used. Baseline and candidate stress runs used the same helper binary
`833a5756b19db7771b9d96a3e3534781bc848bc440546e8e1acf0197be2a46e3`.
The candidate's 32 MiB payload survived normal reboot with SHA256
`3955a4afd023ec9fd7462c7e29db23c18f5a55aef399eadaf045f61a47ede16a`.
The 131,073-byte append payload also matched independently after reboot.
See the paired `nt5-physical-f-cache-stress-*-001-audit.json` reports and
the extended-storage cold-audit report.

A separate emulator-only diagnostic build ran 300 mapped/truncation cases
and another 32 MiB pressure test successfully. Its checkpoint on invalid
write alignment/allocation range never fired. Therefore the exact origin
of the baseline mapped-flush error87 remains unproven. Do not deploy
`xwnfatx-invalid-write.sys` to hardware: it deliberately bugchecks on the
selected error paths. The overlay patch is not part of the production series
and was removed from the source tree after building.

## Physical cycle011

At 22:24:04 UTC on 4 October 2026, one FTP launch was accepted. Only the FATX
driver and bounded startup helper changed; HALa3 and trace413 were verified
unchanged. Previous driver, startup and cycle009 passing report were backed
up first. Paul photographed a boot-time IRQL_NOT_LESS_OR_EQUAL blue screen.

Readback after dashboard return found the untouched 4096-byte pending report
and no append, mapped or pressure test files. Thus there is **no physical
stress-test pass**, and no evidence the helper reached its first write.
All 41 video trace records were recovered. The system event records are
unchanged from cycle010, so their existing delayed-write events cannot be
attributed to cycle011. The downloaded kernel exactly matches the supplied
Windows kernel (SHA256 84172dbd...); no on-disk kernel corruption was found.

Paul corrected the address to 823E2D9B and reported the base as 023D0000.
Using the high kernel alias 823D0000 gives RVA 12D9B, which matches
`CcGetVirtualAddress+0xA5` in the exact native kernel: `mov [edx], ecx`.
Immediately preceding instructions load EDX from VACB+0x14 and ECX from VACB+0x10.
The exact PDB identifies VACB.LruList at +0x10. The reported write to zero at
IRQL 2 is therefore consistent with a NULL backward link during removal from
the cache-manager LRU list. This interpretation explicitly uses the high
alias; there is no crash dump, call stack or identified corrupting writer.
It does not prove a Windows kernel defect or establish which driver caused it.

`collect-cache-physical.py` disabled automatic startup/restart, preserved
the pending report as F:/xwn-cache-report-011.txt, and restored the original
cycle009 report to its canonical path. The candidate filesystem remains
installed; the old driver remains at
F:/winnt/system32/drivers/xwnfatx.xwn-c10. No second launch was sent.
The trace must be preserved and freshly seeded before any future traced boot.

`audit-physical-binaries.py` reads installed Windows binaries against the
deployment manifest with explicit filesystem/video overrides. It also saves
the five current registry hives locally. This is a file-content audit, not
a raw FAT allocation-chain or hardware-memory test. Consult its JSON for
completion and mismatches before interpreting the outcome.

## Next investigation

The address and physical registry replay are now documented below. Continue
with safe partial-sector paging writes and cache-list lifetime diagnostics; the emulator's
clean installation state differs from the installation that suffered the
physical delayed writes. Keep the demonstrated deferred-buffer fix separate
from the unresolved boot crash. A controlled rollback comparison can help
isolate the new filesystem build, but another uninstrumented boot alone
would not establish causality. Paint's 0075 candidate is still emulator-only.

All emulator processes from these tests were closed and their overlays
retained. Preserve the complete `physical-cache-*` backing chain.

## Post-crash state replay

The read-only physical audit completed: all 3,439 binaries (465,488,828 bytes)
match their expected hashes. Five registry hives have matching sequence
numbers, valid checksums and readable complete reachable key/value trees.
These checks do not prove semantic correctness or exclude runtime corruption.

An owned overlay replaces only those five hives in the candidate emulator
fixture. Run `nt5-physical-f-hives-011-001` reached desktop and ran the stress
helper. A mapped flush failed with error87 at case 21, while all 32 MiB of
asynchronous writes/readback passed. Cold readback confirmed the report and
both payloads. Thus 0076 does not resolve the mapped-flush failure. The physical
boot crash was not reproduced. A later HMP RAM dump stalled; the owned harness
stopped xemu and preserved its overlay. Do not describe that host-monitor
failure as a guest crash or claim a confirmed normal restart for this run.

## Delayed-write checkpoint captured

Run `nt5-physical-f-hives-diagnostic-011-001` completed the helper with zero
failures and matching cold payloads, yet displayed a delayed-write popup for
`\Device\HarddiskVolume6\winnt\system32\wbem\repository\CIM.$EC`.
A passing bounded helper is therefore insufficient to establish background
write reliability. The popup was captured before stopping the emulator.

The broader emulator-only diagnostic (`diagnostic-invalid-write-all.patch`,
not a production patch) then stopped run `nt5-physical-f-hives-all-011-001`
with deliberate E058CA02(1,20000,3F8,FFB23568). Read-only debugger inspection
identified `\winnt\setupapi.log`, IRP flags 0x43 (paging, no-cache and synchronous
paging), offset 131072, length 1016, allocation 196608, file size/VDL 131949.
The rejection is the driver's sector-alignment check, before disk submission.
See `hives-011-invalid-write-checkpoint.json` for FCB bytes, request fields and
frame records. This diagnostic stop is not the physical STOP0A.

Native NT is issuing a paging write whose final length is not a multiple of
512 bytes. The driver currently rejects it. A future fix must safely handle
that final sector and serialize any read/modify/write against overlapping
writers. Do not merely round the caller's MDL length upward or remove the
alignment check: that could overread its buffer or clobber neighboring data.
The existing 0052 read-tail helper is a useful starting point, but write
ordering, truncation, allocation bounds, cleanup and failure propagation
need their own validation. No partial-sector write fix has been deployed.

All three physical-hive replay processes are now stopped, with overlays and
screenshots retained. Physical startup remains disabled and no launch after
cycle011 has been attempted. The installed filesystem is still 0076/f8c1f66a;
HALa3 and video trace413 are unchanged. Both deliberate-stop filesystem
variants remain emulator-only. The production source is restored through 0076.


## Partial-sector paging writes and writes after truncation

Patch0077 adds a private-sector read/modify/write for a short paging-write tail.
The caller MDL stays bounded, and a per-file mutex serializes data writes so
another writer cannot change the sector between its read and write. The driver
checks the rounded allocation range under the paging resource. Sixteen compiled
VfatWrite cases verify sector boundaries, neighboring bytes, allocation limits,
allocation/I/O failures and cleanup. Deferred-buffer regression cases still pass.

Run `nt5-physical-f-cache-write-tail-001` passed the 30 mapped cases, 131073-byte
append and 32 MiB asynchronous pressure helper. Its stopped overlay has exact
payload hashes, all 3439 expected immutable binaries and clean allocation/hive
audits. However, a WMI CIM.$EC delayed-write popup remained. This build therefore
did not qualify for hardware deployment.

A separate emulator-only E058CA03 diagnostic captured C000000D for CIM.$EC:
paging write flags43, offset1572864, length65536, with file size, valid data length
and allocation all zero. See `write-tail-failure-checkpoint.json`. This is an
obsolete paging write after truncation, distinct from the short-tail rejection
and from the physical cache-list STOP0A. The checkpoint is deliberately inserted;
it is not a spontaneous guest crash.

Patch0078 makes ordinary paging writes respect the current EOF: a wholly obsolete
range completes with zero bytes; a crossing range is clipped. The shrink path
holds the paging resource exclusively while updating sizes and releasing clusters.
Twenty-one compiled cases include the captured zero-size request and EOF crossing.
The rule matches Microsoft's [FastFAT write path](https://github.com/microsoft/Windows-driver-samples/blob/main/filesys/fastfat/write.c).
The first combined-candidate run (`nt5-physical-f-cache-paging-eof-001`) failed
its first mapped readback at offset0 after truncating to2577 bytes. It restarted
normally, but the report is FAIL and no pressure payload was produced. The cold
file begins with the expected pattern; the immediate cached read remains under
investigation. A first-write diagnostic sees offset0/length4096 with EOF/VDL2577
and allocation65536, confirming the new clipping branch is exercised. A detailed
readback repeat is in progress. Neither new patch
has been uploaded to the physical Xbox. The physical cache-list crash remains
unresolved and is not claimed fixed by these changes.


## Completion-event reuse regression isolated

The detailed repeat failed at byte2560, exactly the start of the short sector,
with actual0x58 versus expected0x3b. The first-write and tail-copy diagnostic
builds are emulator-only, and their deliberate stops are retained separately.
The E058CA05 inspection shows the correct mapped source PFN, source bytes and
17 copied bytes in the private sector before submission. No guest code or
return value was altered through the debugger.

The data-write helper had assumed one write batch per IRP context. A preceding
read can leave its notification event signaled. The new RMW path then submitted
a second write, observed the stale signal and freed its sector before the disk
request completed. Patch0079 resets the event before each data-write batch.
`test-completion-event.py` executes the compiled helper with pending lower I/O:
both regular-file and FAT branches return prematurely in the old build; both
wait for completion in the corrected build. `test-write-tail.py --completion`
passes21 boundary/error cases and the deferred-buffer regression still passes.
The earlier helper-only tests modeled synchronous I/O and did not cover this
stale-event condition; the new test specifically closes that gap.

Use patches0077-0079 together. Builds through0077 or0078 remain failed research
artifacts, not deployment candidates. Apply the ordered manifest in
`patch-check-0079.json` to the pinned base before running
`Build-PagingCompletion.ps1`. Diagnostic patches require their matching source
stage and `XWN_VFAT_WRITE_DIAGNOSTIC`; remove them before a production build.
All binaries, firmware, full disk overlays and raw logs remain local and ignored.


The final `nt5-physical-f-cache-paging-completion-001` run passes all30 mapped
cases and the32MiB pressure test, restarts to the dashboard, and passes the cold
allocation/registry/3439-binary audit. Both payloads match exact expected hashes.
Current-boot event records36-42 contain no Ftdisk50 or delayed-write popup; the
older baseline records remain. EventLog6006 records shutdown. DHCP, HID service,
Ftdisk49 and shutdown rundll32 events remain and are not described as fixed.
`paging-completion-validation.json` qualifies driver f686b0a1 for one controlled
physical trial; it does not resolve the separate physical cache-list STOP0A.

## Physical cycle012: paging fixes pass the bounded hardware trial

At 2026-10-04 23:51:34 UTC the dashboard accepted one FTP launch with filesystem
`f686b0a11395510176a60a23b90415f79c20e5a26dd4217130f27f32915b1884`.
HAL a3 and trace miniport413 were unchanged; the previous0076 driver remains
backed up as `F:/winnt/system32/drivers/xwnfatx.xwn-c11`. The prior cycle009
report remains separately named `xwn-report-v2.pass009`.

The new report starts `XWN-CACHE-START`, completes all30 mapped/truncate cases,
131073-byte cached append and32MiB asynchronous pressure, reports zero failures,
and ends `XWN-CACHE-PASS`. The user observed Windows shutting down and rebooting.
Dashboard FTP then returned; independent reads of all three test payloads match
exact expected data, including the mapped file truncated to zero. Collection
restored the startup command to its prior no-op and verified driver/HAL hashes.
See `physical-cycle-012.json` and `collect-paging-completion-physical.py`.

System event records51-55 belong to this boot: EventLog start/stop, Ftdisk49 and
network link. No new Ftdisk50 or delayed-write popup is recorded. Old failure
records49-50 remain as historical evidence. Application events4-5 contain new
WinMgmt27/60 (0x80041001); WMI health remains unresolved. Historical Paint
crashes remain records2-3; its display-dimensions fix was not installed here.

This establishes one passing physical stress/restart/readback cycle. It does
not identify the corrupting writer behind cycle011's null VACB list link or
prove sustained stability. Preserve this candidate and evidence before longer
soak testing or a separate Paint/display change. Do not rerun the one-shot
launcher: its cycle record prevents duplicate launch.

Post-cycle012 read-only audit: all3439 expected Windows binaries (465493310bytes)
match the package plus explicit driver overrides. An initial dashboard PASV502
interrupted the scan at1384 files; the original partial record is retained and
`--resume` finished with shorter FTP sessions. Five collected registry hives
have matching sequences, valid checksums and readable reachable key/value trees.
This FTP audit does not inspect physical FAT allocation chains or establish
registry semantic health. Reports: `physical-012-binary-audit.json` and
`physical-012-hive-audit.json`. No build, emulator or FTP process remains active.
