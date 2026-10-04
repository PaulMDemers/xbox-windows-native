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
