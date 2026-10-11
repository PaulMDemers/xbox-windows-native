# Complete observation of the diagnostic surface

This emulator-only child changes scalar observation limits relative to the exact
compiled260 renderer. Site11 (CPU read) allows4096 groups, every other site256.
A strong compare/exchange claims a monotonically increasing ticket capped at
limit+1. Exactly one caller can claim the overflow marker. A failed CAS implies
progress by another caller, so retries are bounded by the finite ticket range.
Neither counters nor historical one-shot actors are reset. No rendering,
ownership, admission, cache, callback or native driver behavior changes.

The host counter test compiles the actual helper with atomic builtins under
ASan/UBSan and exercises both capacities, saturation, extreme old counter values
and32 races with eight joined threads each. The independent stream parser uses
explicit per-site capacities, rejects duplicate/incorrect markers and incomplete
groups, and never allows a truncated stream to qualify complete coverage.

The old proof's all-zero state predicate for CPU-write retirement was wrong.
Pinned surface_access_callback sets upload_pending before requesting eviction.
Pinned pgraph_gl_process_pending clears cpu_write_evict_pending, completes dirty
download, then invalidates while upload_pending remains. This new proof requires
exact flags8 at both write eviction and common invalidation: draw_dirty,
download_pending and cpu_write_evict_pending must all be clear, with explicit
upload intent. It separately requires actual callback insertion/unlink/free,
the dirty read/store observations, four exact guest reads and all guard bytes.
Synthetic negative controls reject all three forbidden bits and missing upload
intent; the old261 parser/failure/raw data remain untouched.

The copied runtime now includes the owned257 close-host.py helper using the tested
bounded atomic JSON writer. Simulated monitor cases exercise EOF/reset on quit,
early EOF, invalid stop command and timeout. A pre-execution manifest checks every
invoked local helper, all conditional Invoke modes and the integration scripts.
Real host exit must still be zero after orderly stop/quit; a fallback kill fails.

The unique262 runtime starts from a new copy of the never-executed261 standalone
seed, whose complete files, five hives and full allocation are reverified cold.
The header-locked261 probe, reboot-held258 arena driver and224 workload are
unchanged. Five native ownership attestations, four renderer stages, CPU-exclusive
before/after inventories, GL binding restoration, breakpoint teardown, normal
Windows restart, cold storage checks and orderly host exit remain independent
gates. Ft49 remains a strict failure; a scoped diagnostic is not an ordinary
renderer qualification, physical speedup or native GPU grant.

Only the closed224 non-backing portable was hash-verified offloaded to E, retaining
its original path via junction. The second planned222 offload refused a missing
summary field before changing222; the partial manifest records that failure.
No disk backing chain moved, and the20GiB guard remains unchanged.
