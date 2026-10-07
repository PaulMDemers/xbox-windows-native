# Experimental paging-file dump extent query

The new0103 patch addresses the request actually captured in
`../dump-fsctl-trace/trace001/trace.json`: KernelMode0x9003b, eight-byte map size
65536, four-byte pointer output, rejected by the existing FATX dispatch with
C0000010. It does not change general writeback, event gates or dump policy.

The NT5 consumer retains a pointer to a terminated array of byte lengths and
volume-relative byte offsets. This differs from the GET retrieval-pointers
VCN/LCN structure. See the pinned consumer/source windows in
`../dump-fsctl-trace/contract-review.json` and its report's primary-source links.

The handler accepts only a kernel caller on an actual FATX paging-file FCB,
with exact input/output sizes and non-null pointers. It rejects directories,
raw FAT/volume objects and delete-pending files. Requested bytes must be positive,
sector aligned, within the published paging-file size and fit the existing
32-bit FATX file-size contract. It does not support arbitrary regular files,
hibernation or a new system-hive contract.

The source already constructs `VFAT_PAGING_MAP` before paging-file use. It walks
the complete chain with a bounded count and requires terminal EOC. Published
maps are immutable, growth preserves the old prefix, and old maps are retained
until FCB destruction. The referenced file object holds this lifetime during
the query.0103 snapshots the pointer atomically and reads that resident map;
it performs no new FAT-cache I/O, file mutation or resource acquisition. This
avoids introducing another lock order into the dump setup path.

Construction checks map count, cluster range, sector/cluster geometry and volume
bounds with widened arithmetic. A first pass counts coalesced physical runs;
allocation contains precisely those pairs plus a zero pair. Nonpaged storage
uses an overflow-checked size. A second pass writes lengths trimmed to the
requested prefix and offsets using the existing `(cluster-2)` data-region
translation. The kernel receives the pointer only after successful construction.
Allocation failure leaves output untouched. SEH unwinds an unpublished allocation
if copying the trusted kernel input/output faults. Success transfers ownership
to the caller; this is not an embedded public retrieval-pointers buffer.

`test-map.py` compiles the actual new functions together with the actual existing
map builder under host mocks, ASan and UBSan.4,032 checks cover contiguous and
fragmented runs, sector/cluster boundaries, partial final runs, rejected caller
and buffer contracts, invalid size/map/geometry/cluster metadata, allocation
failure and4,000 deterministic prefix cases with an independent per-sector
oracle. Existing builder tests verify rejection of cyclic, short and invalid
chains and a lower read error. The initial cyclic-chain mock incorrectly
advanced by call count; it was corrected to a stable cluster-to-successor map
before the passing test. No guest failure was concealed. Host mocks do not
validate the NT ABI or real SEH faults.

Fresh RosBE control/candidate builds reconstruct pinned trees and identical
compiler flags. Both runtime fixtures use the same candidate0102 HAL and
video0093, restored owned HidServ executable and inherited emulator-only device
policy. Only the new filesystem source differs. The independent helper and
strict event checks remain identical; any error event still fails qualification.
An initial import verifier assumed all imports came from ntoskrnl; it was
corrected to validate the existing HAL fast-mutex/spinlock imports against the
exact candidate HAL exports too. Both builds then passed binary review.

Remaining gates: matched ordinary boot/workload/cold audits, successful runtime
mapping captured against independently parsed cold FAT extents, and eventually
an actual controlled crash-dump write/recovery in a disposable emulator child.
Event-free configuration alone cannot qualify crash recovery. No physical
deployment is authorized in this session; installed0101/video0093,0088 rollback
and immutable0.1.0 are preserved. The old physical111-byte anomaly remains a
separate unresolved investigation.
