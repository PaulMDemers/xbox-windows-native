# A controlled guest workload, not another copy of the same boot

Read REPORT.md, DESIGN.md, final-review.json and emu001/watch-analysis-failure.json.
All owned processes are closed.269emu001 is immutable failed reuse qualification;
never relaunch, recollect or parent it. Normal guest/host shutdown and cold audit
passed, but the complete watch failed explicit saturation and unit0's first real
reuse had changed source and GL content. The remaining three later lifetimes are
unknown after saturation. Do not infer a leak or preservation bug from this test.

Next independent work:

1. Inspect existing owned nxdk/guest graphics fixtures and exact normal texture
   command paths for a small deterministic guest workload. It must create and own
   its channels, objects, texture memory and expected pixels; no borrowed firmware
   commands or fabricated host invocation of pgraph_gl_bind_textures. Select an
   existing meaningful test if available before introducing another toolchain.
2. Design actual disable/idle/checkpoint/re-enable draws with immutable texture
   patterns and an independent framebuffer/readback oracle. Account normal guest
   ownership/coherence at both captures. This is an emulator renderer lifetime
   test, not Windows native GPU ownership, PTE/cache alias clearance or a speedup.
3. Fix observation accounting in a NEW kit: retain first-bind/final-destruction
   generation records separately from exact bounded counters/run-length records
   of repeated nonfinal decrements. Saturation must still refuse, never truncate
   and PASS. Test actual269 repetition prefix, final-free/address-reuse mutations,
   overflow boundaries and the exact one-word observer seal before a fresh guest.
4. Only a qualifying unchanged control justifies a separate matched narrow release
   candidate. Retain cache owners, perform actual counted decrements, validate the
   complete before/after graph and actual guest content. Never whole-finalize or
   force renderer reset/switch as a shortcut.

Exact269 build005 is E:/Codex-archive/xbox-windows-native/reuse269-build005,
xemu-reuse269.exe SHA489c9af75c8734c47ce8b67231bedb7b10d15dc98617902350514252e5fcc295.
Its diagnostic source is not a proposed functional renderer patch. Preserve
failed build001, never-launched002..004, failed seal host001 and passinghost002.
Complete original texture source was reconstructed by undoing only observer hooks.
2094 frozen inputs and108 invoked dependencies remain exact.

Preserve267/266/263 scoped evidence and all prior failures; Ft49 remains strict.
Keep physical audio004/video118/shared158/FATX0101 and recovery256/0.1.0/0088 intact.
No hardware test queued. Historical emulator policy differs from physical demo.
Check actual time and stop new experiments at October12 04:00UTC; retain20GiB
build/projected-launch guard, owned leases and full cold audits. Do not move backing
chains. Update reports/continuation, check/review/commit/push the private repo.
