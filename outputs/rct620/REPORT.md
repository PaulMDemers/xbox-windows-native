# PC620 closed PASS: original instruction-location controls

Fresh404 ran20:06:39–20:11:49UTC2026-10-20 and restarted normally. All eight
original workloads passed: sleep, arithmetic, memory copy and GDI copy, each
without then with main-thread location snapshots. No game or console ran.

Each workload interval was about20.05s; independent host agreement was within
15.616ms. Five-second sleep matched4.989416240s host. Sleeping process/thread CPU
was0 at coarse resolution. Busy process/thread CPU was20.046875s in both
conditions; other threads did not account for the workload. Observer CPU was0
in busy intervals and0.015625s in sampled sleep; these quantized readings do not
prove zero sampling overhead.

224 snapshots per observed workload: sleep224 ntdll; arithmetic149 exact assembly
loop plus75 ntdll; copy208 exact assembly loop plus16 ntdll; GDI221 gdi32 plus3
ntdll. Original loop ranges were decoded independently from compiled COFF
symbols and matched subject-reported ranges. Every suspension balanced0/1 and
its measured duration was0ms at tick resolution. CPU/loop arithmetic, copy
pixels, stable module bounds, identities and normal exits passed. Snapshots
qualify gross saved-user-location attribution, not exact CPU-time percentages,
kernel-function profiling or FPS. In particular, ntdll observations in a busy
subject must not be called sleeping.

The observer uses elevated priority and deterministic jitter50–113ms; both are
part of the diagnostic method. No host screenshots or input occurred during the
measured windows. No Windows/game/driver patch was made.

Seven balanced-suspension host cases,21 location rejection cases, all18 serial
markers and five invalid-marker cases passed. An initial UI plan used an invalid
super_r key and was rejected before typing/copy launch; the meta_l-r plan then
succeeded. Keep the failed receipt and the earlier619 prelaunch case-limit
failure.620 was a new404 child;619 was not rerun or parented.

Cold validation:6495 files/310 directories, five clean hives, exact tools and
protected OS/seed, one normal EventLog shutdown. All owned processes must be
closed before final001 sealing. The closed593 leaf was archived with full
roundtrip verification under620/archive001; its cached save/reference exports
remain unchanged. No physical access; Xbox last dashboard/no hook,596 SOFTWARE
cold-only.720p, immutable packages and paused automation remain unchanged.
