# Crash-dump usage notification reaches an unsupported HAL root PDO

2026-10-07. Two new owned emulator diagnostics; both closed and cold-audited.
No physical access, driver change, service disabling or configuration workaround.

`dispatch002/trace.json` captures 39 events, 13 paired dispatches, four IRPs and
43 replay-verified resident code windows. The initial usage request is PnP
major 0x1b/minor 0x16, InPath=1, DeviceUsageTypeDumpFile=3. Its route is:

1. XwnFatx -> Ftdisk -> Disk/Classpnp -> Diskperf -> PartMgr -> Disk/Classpnp -> atapi.
2. A nested matching request: atapi -> PCIIde.
3. Another nested matching request: PCIIde -> PCI.
4. Another nested matching request: PCI -> PCI_HAL.

All four requests have matching parameters and FileObject in this capture,
with nested dispatch/return ordering on the same thread. Allocation-parent
links were not separately instrumented; the trace does not claim an observed
IRP allocation relationship or an asynchronous transition that did not occur.

The first completion is called from HAL runtime address 0x825843d8, RVA 0x83d8
in the exact owned HAL SHA256
`a3a84368d59936dfa6bbcdc6d5839d57b886342211142d305e9dde941e4d1648`.
At entry and completion the IRP status is already STATUS_NOT_SUPPORTED. The
HAL completes with that inherited value. Subsequent completions propagate the
same status upward; FATX/Ftdisk dispatch returns STATUS_PENDING, while the
paired final IopSynchronousCall returns STATUS_NOT_SUPPORTED. Completion and
free snapshots precede freeing; return snapshots never dereference freed IRPs.
All breakpoints were removed and the guest resumed. No dispatch remains unpaired.

`hal-source-audit.json` pins the actual HAL's paging-only selector at RVA
0x8493. Type 3 branches to the inherited-status path at 0x8400 and common
completion at 0x83cb. The existing 0055 HAL patch explicitly advertises paging
only, excluding dump/hibernate. Source and exact binary behavior agree. This
is a missing crash-dump root-bus capability, not evidence that Ftdisk itself
originated the rejection, nor a FATX retrieval-pointer failure. As established
by the previous kit, retrieval-pointer initialization has not yet been reached.
The source inspection is not a fresh full source-to-binary rebuild attestation.

`dispatch001` is retained as a failed trace: it stopped at the first unpinned
Diskperf call, safely removed breakpoints and resumed. Its four unmatched calls
are a capture boundary, not a claimed guest leak. Read-only cold extraction of
11 additional storage/bus/HAL binaries enabled a new, independently pinned
dispatch002 child. Neither case may be relaunched or recollected.

Both debugger workloads completed 792 appends, 32 queried allocation decreases,
132 reopens and 11 exact cold files. Both normally shut down and returned to
dashboard. Full allocation: 323 directories, 6765 files, 324 directory clusters,
zero errors/orphans. Five hives parse; protected binaries, startup and payload
hashes match. HidServ remains running 4/0/0 and SCM7000 is absent. Strict overall
qualification remains **false**, solely for Ftdisk49. No gate is waived.
Debugger execution is distinct from the earlier ordinary regressions.

`verify-traces.py` replays all resident windows against SHA-pinned source
binaries with actual load bases and HIGHLOW relocations, checks exact dispatch
order, stack/thread return pairing and completion-before-free. The first replay
incorrectly compared unrounded old PE SizeOfImage with the loader's page-rounded
reservation; it was corrected to exact 4 KiB rounding. Binary SHA and resident
code checks were unchanged. `verify-evidence.py` checks frozen scripts, fixture
parents, closed disks, raw workload bytes, allocation and configuration records.

Crash-dump support is a separate feature requiring real residency, power and
PnP handling, not unconditional successful completion. Microsoft's
[usage-notification contract](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/irp-mn-device-usage-notification)
requires balanced special-file accounting, resident I/O/power paths, retention
of D0 for dump paths, and protection against stop/remove. Passing this root
notification would not by itself qualify actual dump creation or retrieval.

Physical FATX0101/video0093, original0088 rollback and immutable0.1.0 remain
unchanged. The original physical 111 non-ASCII damaged prefix and first restart
method remain unresolved. The intentional 111-zero/109-correct interrupted
writeback mechanism remains separate. Inherited emulator-only synthetic
null-device/unsupported-device policy remains explicit and unchanged.
