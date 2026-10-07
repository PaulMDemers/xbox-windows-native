# Lock review and evidence limits

The negative control on0098 and corrected cleanup-only0099 repeat both retained
complete timeout memory. Their exclusive-resource owners and wait objects prove
two different cycles. Stack addresses are matched source/binary call candidates,
not a complete unwind; shared owners and unrelated synchronization are not fully
decoded. Neither capture retrospectively identifies every older hardware freeze.

| Operation | Regular file | Directory stream |
| --- | --- | --- |
| Cleanup | Main, then Dir, then paging | Dir, then Main, then paging |
| Set-information needing namespace | Main, then Dir | Dir, then Main |
| Directory enumeration | Not applicable | Dir, then shared Main |
| Handle flush | Main, cache flush, Dir for entry update | Dir, Main, cache flush, recursive Dir update |
| Concurrent volume flush | Pin under Dir; drop Dir; Main, cache flush, Dir update | Pin under Dir; reacquire Dir before Main and cache flush |
| Existing-file overwrite | Try Main under Dir; on contention pin, undo attachment, unlock, wait, release pin under Dir, redo lookup | Existing directory-disposition validation remains |

The directory exception follows from rename's existing parent-directory
CcFlushCache calls. That cache callback acquires the parent stream's MainResource
while the namespace lock is already held. A volume flusher must not own the same
directory MainResource and wait for Dir. The common DirResource also serializes
multi-directory namespace changes before their directory-stream acquisitions.

Cache-manager lazy write owns the stream MainResource while paging writeback
uses the existing paging path. AdvanceOnly EOF notifications return without
allocating or reacquiring the namespace resource. This patch does not change
those earlier NT5 compatibility fixes, paging views or cache-manager callbacks.

The FILE_OBJECT retains each ordinary operation's FCB. Concurrent volume flush
pins its stable FCB list before dropping Dir; references are released under Dir
after all per-file acquisitions have been released. The overwrite retry repeats
pathname and share checks after every unlock window. A reference is a lifetime
guarantee, not a guarantee that the old pathname still denotes the same object.

Nonblocking failures unwind held resources before queueing. Directory cleanup
releases Main before Dir; ordinary cleanup releases Dir before Main. Volume
cleanup does not take a per-file MainResource and may destroy the VCB, preserving
the existing conditional Dir release. Existing cache flushes are retained.

The five-worker stress includes file rename/replace and parent cache flush,
concurrent enumeration/cleanup, regular overwrite, resize, attributes and volume
flush. Full mapping/BMP persistence and an independent stress replay are separate
gates. This is not a proof for volume lock/dismount, arbitrary simultaneous
mapped truncation, every possible cache callback, or physical driver behavior.
