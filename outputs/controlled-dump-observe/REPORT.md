# A pageable network shutdown helper prevents crash dumping

crash002 is CLOSED. It launched once at11:11:25 UTC with unchanged candidate0103
FATX, candidate0102 HAL, video0093 and the same controlled-crash helper/driver.
No physical console was accessed. Do not relaunch or recollect either crash case.

The corrected observer pinned resident HAL/FATX dispatches rather than discarded
entrypoints. Five events/eight resident pins show the exact intended E058D103,
its stop-line display and entry into KiScanBugCheckCallbackList. Neither the
callback-scan return nor IoWriteCrashDump entry was reached during the bounded
600-second observation. All breakpoints were removed and the guest resumed.

A separately recorded post-timeout snapshot captured the halted CPU, callback
list, stack and64MiB RAM. The active callback record has a valid checksum and
state2 (started), names the NDIS miniport callback, and points to a72-byte buffer.
That buffer identifies the actual NVNet adapter and MiniportShutdown handler.
Cold before/after NDIS and NVNet binaries match exactly; their resident callback
instructions also match after relocation.

The kernel's current bugcheck data is now D1, with fault address/instruction
0xf8d17800 and IRQL0x1f. Independent page-table translation finds that address
not present (PTE0x00720060). It is NVNet RVA0x7800, symbol NvNetIdleTransmitter,
in the pageable PAGE section. The registered MiniportShutdown at RVA0x21f0 is
resident and calls this helper. The CPU is halted in the HAL after the nested
bugcheck. This explains why the intended crash never reaches dump writing.

The cold audit remains clean:324 directories,6756 files,325 directory clusters,
zero errors/orphans, five readable hives and unchanged protected binaries and
payloads. The exact flushed intent log is present. The96MiB pagefile retains
its1536-cluster map and PAGEPAGE header; no actual dump write or recovery is
qualified. Normal-shutdown count0 belongs to this deliberate-crash protocol,
not an ordinary PASS. All failed evidence remains preserved.

`verification.json` independently replays frozen source/binary hashes, relocated
runtime pins, raw page tables, bugcheck data, callback record/buffer, cold
component hashes and audit artifacts. `callback-review.json` binds the fault to
the exact symbol/section and recorded source call graph. The other direct
shutdown helpers reviewed are already in nonpaged .text. A concrete next change
is to keep NvNetIdleTransmitter resident without changing its MMIO sequence or
bounded polling, then test fresh matched control/candidate builds.

This diagnosis agrees with Microsoft's archived [shutdown callback contract](https://learn.microsoft.com/en-us/previous-versions/windows/hardware/network/ff550533(v=vs.85))
and [NDIS5 paging guidance](https://learn.microsoft.com/en-us/previous-versions/windows/hardware/network/ff557121(v=vs.85)):
shutdown callbacks may execute at high IRQL, so reachable code must remain
resident. The diagnosis itself comes from the pinned runtime and cold evidence.

Host notes: the first waiting post-timeout helper was stopped before any guest
access and replaced with a version that records unknown modules for later cold
verification. Its session22677 is retained as a canceled host observer;50986
performed the one actual snapshot. No frozen tracer or guest payload was changed.
Four old closed standalone runs045–048 were hash-verified to E: with original
paths preserved through junctions; the active backing chain was excluded.
Manifest: outputs/task-storage-offload/manifest-20261007b.json. C: recovered to
about29.5GB; the20GiB build guard remains unchanged.
