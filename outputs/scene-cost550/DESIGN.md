# 550 bounded scene process resource control

Keep the qualified547/549 scene executable unchanged (4073e0a0f5a62a483d11a12b573ffbf7bbb1f2a914a835e7a25364cbdf49d436).
An original user-mode wrapper launches three sequential children per backend,
with fresh result prefixes and no inherited handles. Each has a50second bound;
only its owned process may be terminated on failure. A failure is not a pass.
Poll50ms for completion and GetProcessMemoryInfo; record actual CPU FILETIMEs,
GetTickCount elapsed, working-set/commit peaks and sample counts. Record global
available physical memory only as context, not attribution or a leak verdict.
Exact allfive-scene checks are required on every child. No mode/driver changes.

This measures whole processes including capture I/O and deliberate display
pauses; it is not FPS, GPU speed, game compatibility or in-process leak proof.
Three instances expose process-to-process variation but cannot prove a trend.
Preserve every instance and do not discard the first as an outlier.
Use NT5 PSAPI from the system directory, checked against exact cold exports.
The terminated-process memory race is accepted only after a signalled wait;
other failed queries invalidate the run. Recorded CPU clocks need not be nonzero.

Host receipt mutations and actual exported imports precede a fresh bounded PC
fixture from the original404seed, never from a closed graphics runtime.
Require six independent scene results, normal restart, cold module identity,
hive/event audit and closed ownership before a matched physical package.
Boot diagnosis remains tabled. Retain20GiB including WSL backing onC.
