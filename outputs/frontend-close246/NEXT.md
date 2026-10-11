# Continue from closed246

Read DESIGN.md, REPORT.md, review001.json, actual preserve001/frontend.json,
trace/audit/matrix and process-closure001.json. All owned processes are CLOSED;
never relaunch or recollect this case. The compiled emulator is pinned build001,
not a physical candidate. One real UI close/reopen passed; strict Ftdisk49 remains.

The UI rendering token and acknowledged gate prevent new loans during the closed
interval, but render/display worker contexts, caches and UI GL bindings still
retain objects. Next design a worker-owned admission/barrier protocol with finite
completion outside actor-required locks. Capture actual worker GL context/current
bindings and individual retained object identities. Do not make QOM/main thread
delete GL objects or wait holding BQL/FIFO/PG/renderer locks. Preserve latest dirty
surface data before any natural or diagnostic disposal; entry readback is stale
with respect to unobserved later draws. Save-thread handles are not liveness proof.

Use a NEW child and IDs, unchanged native policy, pinned source/build/seed and
full cold audit. Keep frontend barrier cancellation and acknowledged reopening
on every failure path. No native permit, hardware deployment or peer merge is
authorized by this diagnostic result alone. Preserve physical0101/video0093,
0088rollback, immutable0.1.0 and every failed artifact. Capacity projection and
20GiB guard remain required; closed portable246 is offloaded, backing chains intact.
