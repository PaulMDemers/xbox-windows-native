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

## First ordinary result and remaining gates

Case001 returned normally at2026-10-07T00:20:02UTC. All five workers completed
500 rounds in19260ms with zero API errors. Exact three4097-byte files, absent
meta.tmp, normal shutdown, event deltas, five structural hives and full allocation
passed. See001/qualification.json. No timeout snapshot or debugger was used.

The original fifteen-minute mapping/BMP soak runs in../fatx-lock-order-soak/004.
A fresh sibling002 reuses the exact helper, driver and settled parent after001
PASS; enable-repeat.py records that expansion without overwriting case001.
qualify-candidate.py requires both stress replays and the full soak to pass before
marking the binary eligible for a controlled hardware trial. It never marks a
physical or release qualification, and does not waive earlier physical events.

## Final emulator result

All three gates passed. Independent002 completed the same five500-round workers
in18060ms and returned normally at00:44:42UTC on7October2026. The original full
fifteen-minute soak passed527 mappings,16BMP API cases,50 exact final files,
34 absent intermediates, all timed rounds, normal shutdown and the existing
cold/event/package gates. Each stress run also passed its exact files, five
structural hives and full allocation audit. No snapshots or debugger actions
were needed in these successful runs.

`candidate-eligibility.json` pins the qualified emulator evidence and exact0101
binary. All owned runs are closed; do not relaunch them. See [NEXT.md](NEXT.md)
for the separate hardware step and unresolved physical event gates.
