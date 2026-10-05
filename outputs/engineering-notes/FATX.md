# FATX: implementation findings and Linux handoff

Scope: the ReactOS-derived NT5 filesystem, loader and recovery tools used for
this project's native Windows 2000 installation. This is a review guide and
evidence index, not a complete FATX specification or a Linux patch series.
The most important lesson is to test cache/object lifetime and cold persistence,
not only whether a directory can be listed or a file can be read once.

## Partition identity comes before filesystem interpretation

Dashboard drive letters, Xbox kernel device queries, raw partition-table extents
and Windows letters are different namespaces. On this console the extended
PARTINFO F: extent ends at the queried physical capacity and E: ends exactly at
F:'s start. Its FATX allocation unit is 128 sectors / 64 KiB. An earlier C:
device query differed from the raw table; the user identified shadow-C behavior
as a plausible explanation, not a proven byte-for-byte mapping diagnosis.

Read sector metadata and capacity, bound every start+length calculation using
wide arithmetic, detect overlaps and validate the superblock at the candidate
start. Do not infer an extended partition from a stock-drive layout or a free
space number. The synthetic fixture was initially rejected by an emulator BIOS
reporting only 137 GB; the physical 250 GB query accepted its actual extent.
An emulator capacity rejection did not establish a bad physical partition.
See [metadata report](../native-windows-storage-metadata/REPORT.md), extended
partition tools and physical-F preflight reports.

For Linux: distinguish the raw block-device extent from an Xbox-kernel virtual
view. Require independently checked capacity and metadata before enabling writes.
Do not port our machine's literal LBAs into a generic driver.

## FATX32 is not FAT32 with a different directory name

[0049](../native-windows-fatx-format/0049-vfat-fatx32-entries.patch) separates
FATX32's full-width allocation entries from the conventional FAT32 high-nibble
mask. It updates traversal, free-entry tests, allocation, free counts and writes
together, including the all-ones end marker. Fixing only chain reads leaves
allocation and accounting inconsistent. Keep normal FAT behavior unchanged.

Directory names are counted byte strings, with a 42-byte component limit.
[0058](../native-windows-fatx-metadata/0058-fatx-volume-capabilities.patch) stops
advertising Unicode-on-disk and 255-character names.
[0059](../native-windows-fatx-name-boundary/0059-fatx-counted-oem-name.patch) and
[0060](../native-windows-fatx-rename-boundary/0060-fatx-counted-rename-name.patch)
convert to a temporary buffer that can hold a terminator, check the converted
byte count and conversion status, then copy only the counted bytes to disk.
Do not reserve a terminator inside the 42-byte on-disk field or equate Unicode
character count with encoded byte count. Broad non-ASCII interoperability is
still unqualified. Linux needs an explicit encoding/case-folding policy rather
than a silent assumption that FATX names are UTF-8.

## Directory coordinates must remain explicit

[0061](../native-windows-fatx-rename-boundary/0061-fatx-preserve-rename-indices.patch)
preserves the original slot indices for an in-place rename. Uninitialized indices
could later redirect metadata cleanup.
[0062](../native-windows-fatx-rename-boundary/0062-fatx-rename-logical-indices.patch)
handles this implementation's synthetic dot entries: non-root enumeration uses
logical positions offset by two, while the file object retains physical slots.
The +2 is an implementation convention, not a universal FATX on-disk rule.

For Linux: audit conversions between readdir cookies, synthetic entries, byte
offsets and physical slots. Exercise root/non-root rename, replace-existing,
directory expansion and close/reopen. Neighbor entries need byte-level checks.

## Cache and object lifetime caused failures beyond format parsing

- [0076](../native-windows-physical-f/0076-vfat-pin-deferred-write-buffer.patch):
  a deferred cache callback may run in another process context. Pin/map the
  caller's data before queuing it; do not retain a raw user pointer for later.
- [0054](../native-windows-fatx-flush/0054-vfat-concurrent-volume-flush.patch):
  volume flush inverted directory/global and per-file resource ordering. Pin a
  stable referenced file set, drop the outer resource, then acquire per-file
  resources in the established order. A snapshot without references is unsafe.
- [0081](../native-windows-fatx-forensics/0081-vfat-truncate-deleted-stream-cache.patch)
  and [0083](../native-windows-fatx-forensics/0083-vfat-deleted-directory-paging-write.patch):
  deleting a cached directory can leave late dirty pages after its storage has
  been retired. Zero/truncate cache state and narrowly identify obsolete writes;
  never follow a stale first-cluster field into reused storage.
- [0086](../native-windows-fatx-forensics/0086-vfat-unlinked-fcb-namespace.patch):
  namespace removal differs from final object destruction. An unlinked file
  object can remain referenced, but must not reappear through name lookup,
  rewrite a recycled directory slot or free its chain a second time. A move
  that retains the live object is not the same as deletion.
- [0088](../native-windows-fatx-forensics/0088-vfat-retired-paging-write.patch):
  serialize actual chain retirement with paging writes. Once this implementation
  has retired the namespace and has no open handles, late obsolete paging writes
  cannot write through the former chain. Live and merely delete-pending open
  files still require normal I/O. The guard is not permission to discard errors
  for arbitrary live writes.

Linux equivalents involve inode/dentry lifetime, page/folio writeback, truncate,
unlink and block reuse. Those APIs and POSIX open-unlink semantics differ from
NT. Transfer the invariant, not these predicates or API calls verbatim: no stale
writeback may touch blocks reassigned to another object; live open objects must
retain the data/lifetime their OS promises. Review lock ordering and writeback
completion together. A driver-specific NT workaround is not proof of a Linux
VFS defect.

## Paging, alignment and completion

[0051](../native-windows-fatx-paging/0051-vfat-native-paging-offsets.patch) uses
stable nonpaged paging-file mappings; [0052](../native-windows-fatx-image-read/0052-vfat-native-image-paging-tail.patch)
handles an image read ending inside a sector without extending a caller's MDL.
Use a private sector buffer and copy only the valid tail. The later 0077/0078
write changes address tail and EOF/truncate behavior; 0079 resets a reused
completion event before another request. Keep buffer ownership, request length,
alignment, actual completion count and logical EOF separate. Completion from a
previous request must never release storage for an outstanding new request.

These are particularly important when the filesystem holds the OS's binaries,
registry, memory-mapped files and paging file. A mount/list/copy smoke test
does not exercise the same paths as running an operating system from it.

## Tests worth sharing with other implementations

1. 41/42/43-byte create and rename boundaries, conversion failure and encoded
   multibyte limits; root and nested directories; verify adjacent entries.
2. Allocation crossing FAT/cache/cluster boundaries; FATX16 and FATX32 separately;
   extended-partition bounds and invalid-chain rejection.
3. Concurrent writer and filesystem flush; async buffer lifetime; file tails
   just below/at/above sector, page and cluster sizes; mapped truncate/extend.
4. Dirty replace-existing, unlink/close/writeback races and immediate cluster
   reuse with distinct patterns. Check both old and new objects after reboot.
5. Full allocation accounting plus independent file-content hashes and hive or
   application-format parsing. A valid chain can still hold incomplete data.
6. Real applications as well as synthetic loops. Our Paint trace used a 14-byte
   header, 40-byte header, then 27 writes of 16 KiB, followed by position query,
   flush, EOF setting and close. An earlier 64 KiB replay was not that workload.

Current physical evidence: candidate0088 passed five/fifteen-minute trials,
300 mapped cases in the long trial, a sixteen-file matched Paint-write replay,
and two user-observed actual Paint saves/reopens. Full allocation and binary/hive
audits followed. There was one earlier unresolved Paint freeze, with a partial
file and no usable blocked-thread trace. Its persisted length did not locate
the blocked request. No power-loss/journaling guarantee, exhaustive stress result
or general Linux implementation claim follows from these bounded passes.

For repair, first preserve directory/FAT sectors, payloads and hashes. Our scoped
repair touched identified owned metadata after analysis; it was not a general
fsck algorithm. Never repair unknown users' disks by copying our literal bytes.
The [recovery kit](../native-windows-fatx-recovery/README.md) and
[Paint evidence](../native-windows-paint-save/README.md) retain the chronology.
