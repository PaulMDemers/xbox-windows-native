# Directory cache-flush lock ordering candidate0101

The cleanup-only0099 repeat produced a second exclusive cycle, preserved in
`fatx-cleanup-repeat/001/timeout-analysis.json`. WinMgmt's rename path held the
volume DirResource and waited in AcquireForCcFlush for the parent repository
directory's MainResource. Concurrent volume flush held that directory resource
and waited for DirResource. The helper counters stopped at17/18/10 with no API
errors. The cold attempt failed qualification; allocation and hives remained
structurally consistent. This is distinct from the first0099 harness hold.

Candidate0100 was built but never launched. Its ordinary-file corrections do
not remove the parent-directory cache-flush inversion. Candidate0101 therefore
keeps Main-before-Dir for ordinary files but uses Dir-before-Main for directory
streams whenever both locks are needed: directory enumeration, cleanup,
set-information, handle flush and the directory pass of pinned volume flush.
Rename's existing parent flush can then reacquire that directory's MainResource
without meeting a holder waiting back on DirResource. Cache-manager paging I/O
retains its existing paging resource path, not namespace acquisition. Overwrite
retry/pinning from0100 is preserved.

The existing FILE_OBJECT or pinned volume snapshot retains each FCB throughout
its waits. Failed nonblocking acquisitions unwind their held locks before
queueing; successful paths release in reverse order. Cache flushes and error
propagation are preserved rather than skipped to avoid the hang.

The unchanged corrected five-worker helper performs500 rounds each of two
ordinary writers, volume flush, resize/attribute/rename operations and directory
enumeration. Require exact final bytes, absent intermediate, clean event deltas,
normal restart, structural hives and complete allocation audit. On timeout,
preserve memory before owned cleanup and keep that failed result.

This is an emulator candidate, not a physical deployment or qualification.
Volume lock/dismount, arbitrary concurrent mapped truncation and all possible
resource interactions are not proven by this bounded workload. Physical0098,
video0093, original0088 and immutable0.1.0 remain untouched.
