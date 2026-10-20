# PC613 original process-cost sampler control

Fresh immutable404 child only. No game, physical launch or changes to existing
fixtures. Six sequential children: unsampled/sampled two-second sleep, then fixed
33554432-step LCG work in unsampled/sampled/sampled/unsampled order. All allocate
and touch8MiB. A ready/go handshake excludes startup from the parent interval.
The child records its own work interval; the parent reads that child process's
CPU times and memory. Periodic sampling is100ms; store samples in bounded memory
and flush after measurement. Final terminated-process query reads CPU only.

Record raw QPC/frequency, tick count, user/kernel100ns counters and process-memory
fields. Validate monotonicity, independent tick agreement, enclosing parent/child
CPU intervals, idle versus busy behavior, deterministic checksum, memory growth,
sample ordering and normal shutdown. Report guest clocks separately from host UTC.
Compare observed sampled/pristine costs; do not presume negligible overhead or
infer Xbox/game FPS from this synthetic TCG control. Predeclare generous clock
agreement (max100ms or5percent), sleep CPU<25percent, positive busy CPU>=100ms,
CPU<=elapsed+100ms on one logical CPU. Failure remains evidence, not a reason to
widen gates after observation. Build imports and actual API availability required.

22GiB fresh-fixture admission,2GiB allocation allowance,20GiB reserve including
WSL backing. Preserve all build/check failures; no closed runtime reuse.
