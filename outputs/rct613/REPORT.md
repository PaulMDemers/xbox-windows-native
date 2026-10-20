# PC613: counter qualification failed; normal cleanup passed

An original Windows 2000 control exposed an unreliable high-resolution elapsed
clock in this PC TCG fixture. QueryPerformanceFrequency returned26,519,740,000.
Two requested two-second sleeps each measured2.000s by GetTickCount, but only
0.285730s and0.285929s using QPC/frequency. The predeclared agreement gate failed.
No correction factor or relaxed tolerance was applied. This is not an Xbox clock
finding and does not replace independently checked physical554 evidence.

Four fixed33,554,432-step busy workers completed in63-94ms by tick count with
62.5-93.75ms of process CPU. That is below the100ms workload minimum and too short
for100ms periodic sampling. All six children completed and their deterministic
results are preserved, but the control is CLOSED FAILED. No game cost or sampler
overhead claim follows. See raw-counter-logs001.json and failure-analysis001.json.

The guest ran once from17:15:37 to17:18:08UTC on2026-10-20, requested a normal
restart, and exited without a host quit/deadline. Cold readback hashed6493 files
and310 directories. One new6006, five clean hives/raw agreement, tool/OS/seed pins
passed. All owned processes exited. The automatic final screenshot raced process
exit (FileNotFoundError); preserve it separately from workload results.

The first build stopped on misleading-indentation under -Werror. Its exact
source is sampler-build001.c and its failed metadata/logs remain intact. Build002
corrected formatting; required PE32 imports and media readback passed. Twelve
synthetic host adversaries passed before the guest. review001 retains the actual
clock failure; close002 records failed qualification with successful cleanup.

Host capacity recovery archived closed603/604/605/607 leaves losslessly. The
first launch admission then stopped before process creation because free C space
was6,479,872 bytes below22GiB. archive002 subsequently verified and archived599,
then stopped at601 because its stored normal_shutdown_delta was0.601 and610 were
left untouched. The second archive batch is partial, not fully successful. Across
both maps,1,512,636,416 C bytes were recovered with complete decompression hashes;
all prior evidence remains recoverable at its exact original path. Never boot or
parent these closed runtimes. Existing611 archive maps remain valid too.

Next: fresh614, longer original workloads and independent host monotonic timestamps
from bounded virtual-COM1 markers. QPC remains diagnostic; validate tick elapsed
against host time before using it for game costs. Physical Xbox unchanged/last
dashboard/no owned hook;596 restoration cold-only. No hardware action required.
