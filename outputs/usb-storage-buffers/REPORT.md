# Source-buffer and completion diagnostic, closed

The bounded emulator capture found correct source data, mapped prefixes and
submitted write buffers for the first 360 payload bytes. All 25 captured child
requests completed successfully. The complete 2,226-byte payload subsequently
read back exactly from disk. This did not reproduce the earlier payload failure
or locate its producer: the exit marker is still stale, SYSTEM and SOFTWARE fail
full hive traversal, and setup prevented normal restart. No driver fix is claimed.

## Attempts and cold results

Both attempts are fresh second-boot siblings of the same closed no-XID first-boot
parent, not consecutive boots of these diagnostic children. Storage binaries,
guest probe, 64 MiB configuration and controller are unchanged. Both guests were
launched once and stopped by their owned watchdog; no dashboard return or new
EventLog 6006 was observed.

| Evidence | emu001 | emu002 |
| --- | --- | --- |
| Buffer capture | Failed before events: old kernel VA unmapped | Complete bounded capture: 123 events, 25 requests |
| Payload | Exact 2,226 bytes | Exact 2,226 bytes |
| Status | Parsed; setup held restart | Parsed; setup held restart |
| Exit marker | Exact stale parent bytes | Exact stale parent bytes |
| Allocation | Clean, zero orphans | Clean, zero orphans |
| Five hives, full traversal | All parse | SYSTEM and SOFTWARE fail; other three parse |
| Strict new-event check | False: Ftdisk 49 | Empty delta; does not establish boot success |
| Normal restart / ordinary qualification | False / false | False / false |

emu001 retained its initial E14 debugger failure. A read-only post-failure RAM
snapshot located the kernel at 0x82405000 instead of the unmapped 0x823df000.
Snapshot checks matched FATX executable code and resident ATA executable code;
unavailable pageable ranges remain unverified. This was not a successful capture.
Its inherited scoped cold_integrity_passed flag excludes the optional shell exit;
it must not be read as whole-file integrity, normal restart or overall PASS.

emu002's first lease request was refused before creating an emulator instance.
The refusal is retained in emu002-lease-busy001.json and emu002-failure.json. After
the lease became available, the single Windows launch was accepted at
2026-10-10 23:11:00.803 UTC. Capture ended at 23:11:58.909 UTC; all breakpoints
were removed, no requests or dispatch returns remained outstanding, and the guest
resumed. Observation lasted 304.48 seconds. Cleanup closed it at 23:16:05.666 UTC.

## What was actually captured

The exact loaded FATX and ATA binaries were checked after relocation. Every
nonpaged executable byte and every readable pageable executable byte matched.
Nonresident pageable ATA ranges remain unknown. Actual breakpoint instructions
were separately checked. sites.json and each attempt's frozen source directory
record the addresses, instruction bytes, import and calling conventions.

Twelve nonpaging source writes supplied the expected 30-byte pattern chunks.
Twenty-four source-to-resolved-buffer comparisons matched their requested
prefixes, including twelve paging paths. The paging source virtual address was
unavailable before mapping; those comparisons use pinned physical MDL bytes and
the subsequently resolved prefix, not a claim of a valid early virtual mapping.

Thirteen reads and twelve writes were identified by a monotonically assigned
request ID as well as their reused IRP address. Every IofCallDriver dispatch
returned STATUS_PENDING (0x103), then the matched child completion reported
status 0 and Information 512. No completion was inferred from dispatch return.
All completions in this capture ran on the submitting thread; a cross-process or
cross-thread mapping failure was therefore not exercised.

Each submitted write's virtual and physical bytes agreed. Its PFN mapping and
physical bytes remained unchanged through completion. The requested pattern
prefix grew from 30 to 360 bytes; every prefix matches the corresponding final
cold bytes. Intermediate full 512-byte sectors differ from the final sector
because later writes extended the pattern. No captured submitted write was the
unchanged parent sector. See emu002/buffer-analysis.json, trace.json and
source-mapping-analysis.json; raw buffer bytes remain private and hash-pinned.

This is FATX child-request evidence, not observation of the emulator's actual
DMA scatter/gather bytes. The trace stops before the payload's first sector
boundary and does not cover later payload, exit-marker or registry writes.
Debugger pauses change timing; the successful payload does not disprove the
retained earlier host-trace-only corruption.

## Independent cold evidence

Independent qemu-nbd and qemu-img readers agree on all three logical files,
complete FAT, selected directory entries/sectors and all five extracted hives.
The payload SHA256 is
b75a944b0372b5c98bdeda88cdbe594de66f63e897522d58ccb813ac05c5cdf9.
All five payload sectors changed. The exit sector at byte 148564860928 remained
byte-exact to the parent, despite one IDE/block/root write request triplet.
The status and payload have six and 133 matching host request triplets. These
host entries alone do not establish successful completion or submitted content.

SYSTEM and SOFTWARE headers/checksums are valid, but hivex raises Bad address
while reading values under the TCP/IP service parameters and EventSystem
subscription paths recorded in emu002/details.json. Both before-hive hashes match
the previously qualified parent. The cold integrity result is false. Because
SYSTEM traversal fails, post-run policy/binding equality and complete absence of
XID registry references are unknown. Prelaunch SYSTEM had no XID references;
the XID binary remains absent. Protected file hashes remain exact.

The original audit exception is retained. Collection code was then adjusted to
record per-hive failures and unknown policy results without losing other checks.
No hive or disk was repaired. Frozen prelaunch scripts are unchanged; current
postprocessing hashes are in collection-source-hashes.json. A forced host stop
limits conclusions about the registry failures and ordinary shutdown durability.

## Preservation and next boundary

All eight closed images were hashed. Seven previously pinned images remain
unchanged; emu002's closed image SHA256 is
fa789847b49a0bb8e3744cbe6205c5d4a618c06e63f67081e695380a56d6cd5a.
The common parent is
6de11f0ce947138eddbabfa503836f3bb4b7eb51905795238a489f1236584f97.
Storage pins are recorded in storage-pins.json; source parent is commit 32f8217.
Exact original sectors, buffers, snapshots, hives and disk images remain private
on E:, with hashes in private-evidence.json and preserved-disks.json.

The producer is unresolved. The next useful capture must cover the failing exit
or registry writes and the actual DMA buffer through backend completion, with
less guest pausing. See NEXT.md. All owned sessions and resource leases are
closed. No physical-console, shared baseline, candidate or integration changes.
