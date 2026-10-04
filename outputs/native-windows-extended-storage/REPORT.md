# Native Windows 2000 on extended FATX F

The emulator boots the native Windows 2000 desktop from FATX partition 6 on a
250,059,350,016-byte disk with 64 KiB clusters. Native Windows read and write
operations passed at byte offset 145,644,445,696, beyond LBA28. A normal Windows
restart returned to UnleashX and its FTP server without console input.

Physical evidence remains separate: the real console reached the Windows boot
bitmap (XWN390), and an automated read-only metadata probe confirmed its PARTINFO
table, F geometry and automatic return to FTP. This session did not deploy or
run native Windows storage on the physical console.

## Implementation

- Patch 0065 explicitly opts into a partition-6 Windows root. Ordinary defaults
  remain unchanged. F begins at LBA 15,633,072 and contains 472,764,096 sectors.
- Patch 0066 adds a bounded whole-device length fallback. Windows 2000 returned
  `STATUS_NOT_IMPLEMENTED` for `IOCTL_DISK_GET_LENGTH_INFO` in run 002. The fallback
  uses `IOCTL_DISK_GET_PARTITION_INFO` only for the three unsupported-request
  statuses, and requires PartitionNumber 0, StartingOffset 0, a complete reply,
  and a positive sector-aligned length. It does not estimate capacity from CHS
  geometry or from the partition table itself.
- The HAL records diagnostic telemetry without requiring debugger edits.
  All 84 imports resolve against the pinned Windows kernel. Diagnostic stop
  exports are disabled in this ordinary boot build.
- The private SYSTEM hive maps Windows C: to the Xbox F partition and enables
  ATAPI `EnableBigLba`. The native FATX driver remains the verified 0059 build;
  experimental rename patches 0060–0062 are excluded.

The source chain is reproducible through `patch-check-0066.json`; verified tree
`6f2bc6a2868ee0b9b37055d59ef51d03a02b31f9`. Current package hashes are in
`package-004.json`. Windows binaries, disk images, SDKs and credentials are not
included in the repository.

## Runtime evidence

| Run | Result |
| --- | --- |
| 001–002 | 7B before mounting F; telemetry isolated the unsupported length IOCTL. |
| 003 | F desktop and 4,097-byte high-LBA read, seek and EOF checks passed. Host stopped this exploratory run. |
| 004 | High-LBA generation 0→1, flush/reopen verification, then normal Windows shutdown. |
| 005 | Cold boot of 004, generation 1→2, then normal shutdown. |
| 006 | High-LBA write and normal Windows restart to UnleashX/FTP. |
| 007 | Corrected fixture and final HAL: generation 0→1, normal restart, FTP, and clean cold allocation/binary/hive audit. |
| 008 | Cold boot of 007: generation 1→2, normal restart to dashboard, second clean cold audit. |

Runs 004 and 005 display the real safe-to-turn-off bitmap and enter the HAL halt
path. Their observed virtual-disk writes after the first native-kernel interrupt
all fall within F. Xbox startup performs separate pre-kernel writes, including a
512-byte write at offset 4096. These traces do not establish that the entire disk
outside F remains untouched throughout Xbox startup, nor are they a physical
hardware guarantee. Reboot runs include later dashboard activity and must not be
interpreted as an uninterrupted Windows-only trace.

Run 007 cold audit checked 6,490 files, all 3,439 baseline immutable binaries,
allocation ownership, crosslinks, chain sizes and reachable registry trees.
There were zero unclaimed allocations. Its high-LBA payload matched generation 1,
and the remainder of the 64 KiB sentinel cluster stayed zero.
Run 008 repeats those checks successfully for generation 2, with zero unclaimed
allocations. Dashboard FTP control login worked after restart; a passive data
transfer failed because that ephemeral port was not forwarded by the emulator
network. The bounded VM run ended before the active-mode retry. Its report was
therefore collected offline, not over FTP. Physical metadata retrieval already
worked over FTP in the separately recorded physical cycle.

## Fixture issue found and corrected

The initial offline writer filled unused directory tails with zeroes. Our host
reader treated zero as end-of-directory, whereas this pinned FATX driver treats
only `0xff` as the end marker. Windows therefore extended some directories past
those slots. The cold audit appeared to find three orphans, but inspection found
their live references in those later directory clusters: Crypto/DSS and CSC
entries. They were not evidence of three lost writes or a growing allocator leak.

`bulk_fatx.py` now fills new and extended directory clusters with `0xff`; file
padding stays zero. `normalize-fixture.py` creates a separate fresh test fixture,
normalizes 305 directory tails, and verifies all 6,487 file contents unchanged.
It never repairs a used disk or touches hardware. `test-fixture-directories.py`
covers creation, two chain extensions and cold reads. Run 007 confirms the clean
result under native Windows. Historical audit failures remain recorded.

## Remaining work

Prepare a file-based physical deployment on F that preserves existing games and
softmod data, then validate native storage and hardware-specific drivers. The
emulator BIOS/dashboard reports a smaller F capacity than the native Windows
path; emulator FTP capacity is not used as proof of LBA48 correctness. Physical
capacity and bounds come from the console metadata probe, while high-LBA native
I/O is currently emulator evidence only. A physical desktop remains unverified.

Supporting sources: pinned ReactOS `vfat.h` defines FATX end as `0xff`;
`dirwr.c::vfatFindDirSpace` uses that predicate. Microsoft's
[GET_LENGTH_INFO documentation](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/ntdddisk/ni-ntdddisk-ioctl_disk_get_length_info)
lists Windows XP as its minimum supported client. HP's
[Windows 2000 large-drive guidance](https://h10032.www1.hp.com/ctg/Manual/c02716774.pdf)
documents the `EnableBigLba` registry setting. Runtime conclusions above are
based on the attached local test reports, not inferred from those documents.
