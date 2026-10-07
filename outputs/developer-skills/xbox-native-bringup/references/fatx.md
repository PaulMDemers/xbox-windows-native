# FATX invariants and regression design

These lessons came from an NT5/ReactOS-derived FATX implementation. Transfer
invariants to Linux, not NT-specific predicates or cache-manager calls.

## Identity and format

- Dashboard letters, Xbox kernel partition devices, raw extended partition
  tables and Windows mount letters are different namespaces. Softmod shadow-C
  may add another view; a discrepancy is evidence to investigate, not proof of
  the mapping. Validate capacity, sector size, overflow-safe start/end bounds,
  overlap and candidate superblocks before interpreting a partition.
- FATX32 uses full-width allocation entries. Do not accidentally apply FAT32's
  high-nibble mask. Audit traversal, free tests, allocation, end markers and
  accounting together; preserve separate FAT16/FAT32 paths.
- FATX names are counted bytes with a 42-byte component field. A terminator
  belongs in a temporary conversion buffer, not inside that full on-disk field.
  Validate conversion status and encoded byte count. Do not assume UTF-8,
  Unicode storage, or that character count equals byte count.
- Synthetic dot entries and logical enumeration offsets belong to an
  implementation, not the FATX disk format. Keep readdir cookies, byte offsets
  and physical directory slots explicit across rename/replace/cleanup.

## Lifetime and writeback

Namespace unlink, handle close, cache-map teardown and chain retirement are
distinct transitions. Referenced objects must remain valid, but an unlinked
object must not reappear through name lookup, rewrite a reused directory slot,
free its chain twice, or direct late dirty writeback into a new owner's blocks.
Serialize retirement with paging/writeback; preserve the OS's live-open-file
semantics. Do not broadly suppress write errors to make a test pass.

Deferred I/O may run in another address space. Pin/map user buffers before
queuing callbacks and retain them through actual completion. Volume flush needs
stable referenced objects and consistent lock order; do not take per-file locks
under an inverted global/directory lock. Reused completion events must be reset
before issuing a new request.

A confirmed NT5 cycle paired cleanup holding the volume DirResource while
waiting for a file MainResource with volume flush holding that same MainResource
while waiting for DirResource. Releasing the namespace lock only in volume flush
did not fix reverse-order callers. Existing file objects can retain an FCB while
acquiring MainResource first; create-by-name needs a safe retry with fresh lookup
and sharing checks after dropping the namespace lock. Pinning lifetime alone does
not preserve pathname identity. Audit enumeration and metadata paths as well.

Do not extrapolate ordinary-file ordering to directory metadata streams. A
second retained NT5 cycle had rename holding DirResource while CcFlushCache on
the parent directory acquired that directory's MainResource; volume flush owned
the same MainResource and waited for DirResource. Include indirect cache-manager
callbacks in the lock graph. Directory streams may need namespace-before-stream
ordering even when ordinary files require the reverse. Keep every directory
operation needing both locks consistent; do not skip cache flushes or discard
their failures to make a hang disappear. A source fix still needs runtime and
cold persistence qualification.

Distinguish logical EOF, allocation size, page/sector alignment and actual
completion length. Use private sector buffers for tails when the caller's
mapping does not cover a complete sector; never overrun an MDL or silently
extend a short write into neighboring data.

Regular-file paging views must zero the returned sector slack beyond logical EOF.
A byte-for-byte file hash can pass while its mapped tail is wrong. One NT5 driver
load rejected an odd-length, valid-checksum image because its checksum routine
included a nonzero byte just beyond EOF. Compare mapped bytes and the EOF tail
before changing PE checksums or bypassing image verification. Bound zeroing by
the actual completed buffer, preserve directory/FAT/raw-volume streams, and test
short reads and failure paths. This invariant transfers to Linux; the NT checksum
routine, MDLs and completion rules do not define Linux's implementation.

## Useful regressions

Exercise 41/42/43-byte names, nested/root rename and replace, allocation boundary
crossings, mapped truncate/extend, concurrent volume flush, async buffers, dirty
replace-existing and immediate cluster reuse with distinct guard patterns.
Check old/new object semantics and exact content after a normal reboot.

Match real application's write sizes and ordering when replaying a failure.
One observed Paint sequence wrote 14-byte and 40-byte headers followed by 16 KiB
chunks, then queried position, flushed, set EOF and closed; a generic 64 KiB
writer was not equivalent. A partial file alone cannot locate a blocked request.
Capture thread stacks or operation traces before assigning the root cause.

Before repair, preserve the original relevant sectors and hashes. Literal
metadata fixes for one owned disk are not a generic fsck implementation.
