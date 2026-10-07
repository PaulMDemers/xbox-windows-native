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

## Paging views and sector slack beyond EOF

A later emulator display-package installation exposed a separate read defect in
candidate0088. Windows requested the correctly installed miniport, but rejected
its image before DriverEntry with checksum mismatch. The 42,215 bytes within EOF
matched the driver exactly. Its mapped byte at EOF was 0x97 from sector slack.
The owned NT5 checksum routine includes that byte when the file length is odd.
An isolated replay failed with 0x97 and passed with only that byte changed to zero;
the executable's checksum field itself was already correct.

Candidate0098 zeroes completed paging-read bytes beyond regular-file EOF, while
holding the existing paging resource. It preserves the transfer count and keeps
zeroing within returned bytes; the memory manager handles the remainder of a
short page read. Directory, FAT and raw-volume streams are excluded. It does not
rewrite sector slack on disk or alter ordinary noncached reads. The physical
baseline remains0088 pending broader validation and a separate hardware trial.

The transferable regression is an odd-length regular file with deliberately
nonzero allocation slack: verify both file content and the mapped final-page
tail. Also cover sector/page boundaries, short completions, failed reads and
metadata/raw-volume exclusions. Exact readback alone cannot catch this defect.
Do not transfer NT-specific checksum or MDL rules verbatim into Linux code.

[Debugger evidence](../video-nt5-load-trace/README.md) and
[candidate build/tests](../fatx-paging-eof/README.md) retain the boundaries between
physical results, host tests, debugger runs and ordinary emulator validation.

A paired real NT5 mapping regression now extends that evidence: 17 file sizes
around sector/page/64 KiB cluster boundaries, deliberately 0xD7 allocation slack,
then 136 create/replace/flush/reopen cycles with 997-byte writes. FATX0088 exposed
nonzero mapped EOF tails in 74/153 checks while every in-file byte remained right;
0098 passed 153/153. Ordinary ReadFile and cold hashes alone would miss this bug.
Both retained exact input/output contents, allocation ownership and the original
dirty input slack on disk. The 0088 control also logged a shutdown rundll32 popup;
the 0098 run had none. Keep that separate from the paging comparison.

The [mapped-file regression](../fatx-mapped-eof/README.md) records complete cold
allocation scans, five parsed hives, event boundaries and exact fixture hashes.
It is serial, synthetic-resource emulator evidence, not a physical result or a
test of concurrent mapped truncation/mapped writes. The lesson for other FATX
implementations is to test the mapped final-page tail independently of logical
file contents and allocation correctness, with nonzero backing slack.

## FATX0098: bounded physical mapped-EOF validation, 2026-10-06 UTC

The [isolated hardware trial](../fatx0098-physical-trial/README.md) changed only
FATX0088 to FATX0098 while retaining the working video0093 baseline. Ordinary
Win32 APIs created 17 input sizes around sector, page and 64 KiB cluster
boundaries. Input mapping plus eight output replacement rounds passed 153/153
checks, with 136 write/flush/close/reopen cycles and exact cold readback of all
34 final files. Normal shutdown was recorded; no new popups or unexpected
warning/error events appeared.

Independent post-run checks found consistent allocation across 122,181 files
and 6,066 directories, all 3,439 expected executable/font payload hashes intact,
and nine structurally readable registry hives. Normal startup and rollback0088
were verified after collection. Hardware backing slack was not deliberately
poisoned: the paired emulator regression remains the direct negative-control
evidence for stale EOF-tail exposure. The hardware result supports this bounded
serial workload; it does not qualify concurrent mapped truncation, long soaks,
display acceleration or generic PnP behavior. Both failed emulator rehearsals
remain recorded separately from the successful physical result.

## Capacity warnings and drive identity (2026-10-06)

The completed15-minute0098 physical soak passed527 mappings,16 BMP API replays,
50 exact final files,34 absent intermediates,full allocation,3439 binary hashes
and nine structural hive checks. It remains strict FAIL on one shutdown popup
and three Srv2013 events. Do not erase these failures when reclassifying causes.

Captured MountedDevices plus the pinned HAL partition table distinguish Windows
C: (dashboard F:, extended partition) from Windows F: (dashboard C:, system).
Windows G:/H: are dashboard X:/Y: cache partitions. The owned NT5 event resource
decodes Srv2013 as a disk-capacity warning. A separate two-minute physical probe
reported0.559%,2.892%,6.176% free on those three small volumes, with both Win32
space APIs agreeing; the large Windows C: still reported41.440% free. Two APIs
through one driver are not an independent FAT scan. No capacity/threshold or
partition contents were changed. See ../shutdown-diagnostics for exact hashes,
offsets, source provenance and observations. Softmod shadow-C relationships are
not established merely by these native partition offsets.

The bounded diagnostic reboot was clean despite an active audio-device wizard.
That supports treating installer shutdown behavior as a separate investigation;
it does not demonstrate a fix or prove every earlier popup unrelated to storage.

## Open concurrency investigation: cleanup versus volume flush

A later emulator setup/shutdown control stalled after EventLog shutdown. Its
retained stack candidates place a cache worker, volume flush worker and svchost
at DirResource acquisition sites in the exact0098 driver; winlogon waits in
PopFlushVolumes. That capture did not preserve raw memory or resource owners,
so it cannot establish a deadlock cycle or distinguish a leaked resource from
an owner waiting elsewhere.

The matching source contains MainResource->DirResource and the reverse order
in different paths. The earlier pinned-volume-flush change alone does not make
all cleanup, overwrite-create, enumeration and metadata operations follow one
order. [The focused concurrency kit](../fatx-shutdown-concurrency/README.md)
records source identities and prepares concurrent regular-file/volume flushing
with post-timeout resource-owner capture. No speculative driver change has been
deployed from this finding. Ordinary serial workload passes do not close it.

The subsequent focused concurrency001 now proves that specific inversion at
runtime. Cleanup thread876 owns DirResource0xfe6180d0 and waits on worker0.bin
MainResource0xffb7403c, owned by volume-flush thread884;884 waits back on that
same DirResource. Both owners and wait blocks were read using the matching
kernel layout. Counters stopped at1/1/1. The retained snapshot, helper code-byte
verification and [cycle report](../fatx-shutdown-concurrency/001/deadlock-summary.json)
support this finding; they do not retrospectively prove every old freeze.
Candidate0099 reorders cleanup only and remains under emulator investigation.

For Linux projects, this is a review question about their own namespace,
per-inode, writeback and eviction lock ordering, not evidence of a Linux FATX
bug. NT ERESOURCE/cache-manager layouts and the observed Windows stack do not
describe Linux synchronization. Preserve ownership and lifetime evidence before
translating a proposed fix between implementations.

## Directory-stream exception and candidate0101 (2026-10-07)

The cleanup-only0099 run first completed all three500-round workers but was
held by a test-helper bug: WaitForMultipleObjects with wait-all accepts the
whole documented success range, and returned2 rather than0. That attempt is
preserved as a failed shutdown qualification, despite complete file contents.
Correcting the helper in a fresh sibling run then exposed another real cycle.

WinMgmt's rename path held DirResource and flushed a parent directory's cache.
AcquireForCcFlush waited for that directory MainResource, which was owned by
the volume-flush worker waiting back on DirResource. The directory was
`\winnt\system32\wbem\repository`; counters stopped at17/18/10 with zero API
errors. The [retained ownership report](../fatx-cleanup-repeat/001/deadlock-summary.json)
distinguishes this from the first helper hold and from the original cleanup cycle.

Candidate0101 preserves Main-before-Dir for ordinary files, but uses
Dir-before-Main consistently for directory streams when both are required.
It retains cache flushes, FCB lifetime pins and fresh pathname/share validation
after overwrite retries. [The lock review](../fatx-directory-order/LOCK-REVIEW.md)
identifies each changed caller and the unqualified paths. Candidate0100 was
built but held before launch because its uniform ordering missed this exception.

The first0101 emulator run passed500 rounds in each of five simultaneous
workers, including resize, attributes, rename/replace, directory enumeration,
ordinary writes and volume flush. Windows restarted normally; all final bytes,
five registry hives, event deltas and complete FATX allocation checks passed.
Full mapping/BMP soak and independent repeat qualification remain separate gates.
No hardware driver was changed by this result.

The transferable lesson is to include indirect cache/writeback callbacks and
parent-directory operations in the lock graph. A regular-file ordering cannot
be blindly applied to metadata streams. Linux implementations need to establish
their own inode/directory/writeback contract; these NT callback names are not
prescriptive Linux locking rules.
