#268: narrow unit release passes host rebind tests

No xemu build or guest was prepared/launched in this kit. No renderer or physical
driver changed. The proposed release remains host-tested source, not an installed
functional patch.

Host003 passed32 combinations of original bind/rebind behavior and28 refusal
cases under ASan/UBSan with warnings treated as errors. It executed exact pinned
xemu binding, counted destruction and cache functions with real QEMU LRU/queue
code. GL, texture upload, register and dirty-memory interfaces are explicit
models. All212 model uploads were eventually deleted/freed exactly once; no leak
was reported. These are not real GL, resumed-guest, image-preservation or speedup
results.

With the release applied in the harness, four disabled unit references become
zero unit edges while all cache owners remain live. Clean cached data rebinds
through the actual source path without creating replacement textures. Changed
texture/palette data and ordinary cache eviction exercise replacement paths.
Malformed ownership, enabled units, foreign context/unit/target aliases, missing
acknowledgments, stale actual identities/cache counts/GL bindings and GL error
preflight all refuse without changing refcounts.

Host001 failed compilation due to a missing model constant and a warning.
Host002 compiled but failed an over-restrictive harness expectation: after cache
eviction, the original clean unit can legitimately keep a sole unit reference
through its fast path. Host003 uses actual cache-plus-unit edges for the control
invariant. The proposed release helper and original extracted functions did not
change between002 and003. All failures and exact inputs are retained under
E:/Codex-archive/xbox-windows-native/unit-release268-host001..003.

Source review shows normal reset marks cached textures possibly dirty without
discarding their cache identities. Actual reuse after restart is still unproven.
DESIGN.md specifies a read-only control to observe real guest binds and preserve
bounded texture readbacks before trying a release. It must reject insufficient
reuse coverage instead of treating the return to dashboard as a success.

Prior267 remains closed: scoped ownership observation PASS, strictFALSE for
Ftdisk49. Physical audio004/video118/shared158/FATX0101 and recovery256 are unchanged.
All268 subprocesses are closed. There is no pending hardware test.
