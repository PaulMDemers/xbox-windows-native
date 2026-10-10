# SMBus ownership and resource review

The offline review found a concrete resource-preservation gap and narrowed the
remaining ownership problem to HAL takeover. The previous prototype pinned only
BAR1 at C000; its physical BAR2 alternative remained relocatable. The new pure
resource policy pins both observed physical ranges, preserves unrelated resources,
and distinguishes the emulator layout. It passed **5,432 ASan/UBSan test cases**.
The corrected NT5 helper and resource-only kernel derivative now compile, and
both pass import review against the pinned NT5 providers. A fresh user-mode
NT5 rehearsal also passed all5,432 cases with exit0 and cold integrity verified.
No physical console connection, driver installation or hardware I/O took place
during this review. The emulator runs only the pure user-mode policy tests. The completed hardware220 ticket remains closed.

## Pinned owners

| Component | Evidence reviewed | Ownership finding |
| --- | --- | --- |
| Physical HAL | Captured binary a3a84368d59936dfa6bbcdc6d5839d57b886342211142d305e9dde941e4d1648, exports and retained HalpXboxPowerAction disassembly | Direct C000/C002/C004/C006/C008 access for SMC power actions. Interrupts disabled; busy and completion waits are unbounded. No exported SMBus broker. |
| Installed video0093 | Captured binary 3e74a5c35b68d7fa0e047b4ba9cec25e7ec0ea5a94e796fc07508f667fcc85cf, pinned build source/CMake and imports | Retains firmware mode, uses NV2A MMIO. No direct port-I/O instructions found. Diagnostic PCI reads target the bridge/GPU, not the SMBus function. No SMBus transaction path found in this build. |
| Restored legacy audio | Audio owner's captured/restored ac97xnt5, SHA256 9cccf729317efb34b1350c12ca2cc9b285fa57a8746147b93632bb1cce177efa | Imports register-access helpers and PortCls, with no direct port-I/O instructions found. This is binary evidence, not a source reconstruction. Physical220 reported problem10 for this binding. |
| Audio004 candidate | All 33 source hashes verified against the audio owner's source-build004 manifest | Native build redirects READ/WRITE_PORT macros to MMIO register access. Its codec semaphore is the AC'97 semaphore in the ACI aperture, not an SMBus lock. This reviewed candidate is distinct from the restored legacy driver. |
| PCI telemetry prototype | Frozen driver004 source/package and the actual bounded transaction engine | FAST_MUTEX serializes this driver's requests only. It neither coordinates HAL access nor guarantees recovery from a stuck controller. |

These static findings are scoped to the pinned images. They are not exhaustive
runtime concurrency proofs or permission to mix future video/audio candidates.
Firmware encoder initialization occurs before this Windows driver could start;
future runtime encoder control would need explicit shared ownership. C200 is
preserved because it is observed firmware/Windows resource state; its hardware
role is not guessed or probed here. The separate modem function remains outside
this resource change, with no codec-presence claim.

## Resource change

inputs.json is a fresh read-only extraction from the physical220 returned SYSTEM
and emulator004 cold SYSTEM, with hive hashes verified against their manifests.
The original physical189 requirements and the newer physical220 layout agree.
vectors.h contains only four SMBus resource vectors generated from that evidence.

| Profile | Required boot ranges | Requirements policy |
| --- | --- | --- |
| Physical220 | C000-C00F and C200-C21F | Pin both preferred/alternative BAR1 and BAR2 descriptors; retain BAR0, interrupt, ordering and private tags. |
| Emulator004 | C000-C01F | Pin only its observed BAR1 pair; require the distinct three-descriptor layout. |

resources.h validates all alternatives before modifying any byte. It rejects
unknown layouts, mixed profiles, invalid pinned-resource alignment/size, truncated lists and
missing/duplicate/overlapping mandatory ranges. The start validator permits at
most one separate physical BAR0 allocation; it rejects unexpected memory resources.
The new xwnsmb-resource.c checks raw and translated start resources before passing
START to the bus driver. It is a derivative of the retained xwnsmb003.c; historical
qualified source and build bytes are unchanged. Telemetry returns
STATUS_NOT_SUPPORTED in the derivative, with the port-I/O callbacks removed.
No INF or installer is supplied for this resource-review derivative.

The policy deliberately supports the captured NT5/x86 layouts only. Actual PnP
requirements may take other valid forms; refusal of an unfamiliar layout is not
proof that Windows is wrong. This still requires a genuine driver/PnP integration
trial before promotion. Raw and translated bus-header/flag assumptions remain
explicit integration checks, not established by replaying BootConfig.

Microsoft documents filtering before allocation, retaining descriptor order and
unhandled private tags. This change follows those constraints without adding a
resource or changing list size. [IRP_MN_FILTER_RESOURCE_REQUIREMENTS](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/irp-mn-filter-resource-requirements)

## Tests and preserved failures

The host tests execute the actual header used by the derivative. They replay both
captured profiles, demonstrate the old unrestricted C200 alternative, check
idempotence and byte preservation, mutate every requirements bit, test every
truncation, reject a malformed second alternative without modifying the first,
and exercise omitted/moved/widened/duplicate C200 plus BAR0 overlap cases.
tests001.json records 5,432 passing cases with ASan/UBSan and no failure line.
This is compiled-function evidence, not allocator or hardware evidence.

The first two build attempts could not acquire the shared build lease and did
not compile. The eventual build001 passed the host tests but its NT5 helper link
failed on __chkstk_ms: three 4 KiB automatic test buffers needed a CRT stack probe
under -nostdlib. The original test header and source hashes remain in
resource-tests001-link-failure.h and build001-failure.json. The fresh build002
uses static buffers in this single-threaded test process; the resource algorithm
is unchanged. Build002 was initially refused before compilation by the 20 GiB projected C:
free-space guard. When space became available, the fresh build completed. Its
5,432 sanitizer tests passed again. The helper and kernel derivative both resolve
all imports against pinned NT5 providers and contain no direct port-I/O
instructions. compiler002.txt matches the pinned RosBE GCC8.4.0 compiler hash.

Build-002.ps1 and Prepare/Run-Emulator001.ps1 provide fresh, guarded continuation.
The guest workload runs only the pure resource tests and writes a fresh
log under C:\xwnpciown1; it does not install the kernel derivative. This tests
NT5 execution of the policy, not real PnP allocation. No fixture was prepared or
launched while the space guard was unmet. The fresh fixture passed its protected
file/hive and full allocation checks before one accepted launch.

## Required ownership contract before functional hardware use

Normal shutdown must close the request gate, drain the bounded in-flight transfer,
and hand off controller state before HAL power access. A private driver mutex alone
cannot provide that handoff. A controller reported stuck must remain quarantined,
and HAL must have a bounded recovery/takeover path instead of waiting indefinitely.

Fatal reboot is a separate case: HAL may preempt the current owner and cannot wait
for a lock held by the interrupted thread. The proposed shared service therefore
needs an explicit terminal takeover path, bounded status/abort handling, and a
defined result if the bus never becomes idle. Its implementation belongs in a
coordinated HAL/driver revision, not a spinlock added only to this function driver.
This report specifies the contract; it does not claim that aborting a transaction
is safe on the physical controller without further evidence.

Next: review and implement the coordinated HAL handoff and exercise lifecycle
tests before preparing a new serialized physical ticket. Hardware220's closed
ticket cannot be reused. Functional SMBus support, repeated normal restart and
whole-boot qualification remain unproven; inherited Ftdisk49 remains recorded.


## Completed NT5 rehearsal

One launch was accepted at2026-10-10T18:35:34.918654+00:00. The guest was closed
at its180-second host bound at18:38:35UTC; it will not be relaunched. Cold
resources.log contains CASES5432, FAILURE_LINE0 and PASS_NO_HARDWARE_IO;
result.txt contains RESOURCE_TEST_EXIT0. The kernel derivative was not staged.

All protected fixture files and source-disk hashes match. Five hives parse with
valid checksums/equal header sequences. SetupAPI and event histories are preserved.
Full allocation scan:319 directories,6717 files,320 directory clusters, zero
errors and zero orphans. The typed device/class delta exactly matches the previously
reviewed physical-seed-to-xemu resource/IDE transition; binding_state_unchanged
remains explicitly false. This narrow fixture match does not waive physical
restoration checks. Diagnostic_usable is true.

There was no normal guest restart; shutdown/persistence and actual PnP allocation
are unqualified. Inherited Ftdisk49 remains a strict whole-boot failure. These
limits are retained in emulator001/audit.json and closed.json. All owned build,
preparation, emulator and cold-reader sessions are closed; no lease remains.

Publication checks: staged source bytes match build002 hashes; Python syntax and
`git diff --cached --check` passed. Repository binary/media/credential-pattern
checks passed for19,464 tracked files. Private media, hives and binaries stay local.
