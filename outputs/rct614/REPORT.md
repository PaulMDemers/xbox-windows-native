# PC614: host-correlated process-cost control passed

An original Windows 2000 control validated guest millisecond elapsed time against
independent host monotonic timestamps. All twelve bounded virtual-COM1 markers
arrived in order, matched the saved guest ticks, and satisfied the predeclared
100 ms / 5% agreement bound. The largest observed difference was about 12.8 ms.
The high-resolution QPC readings remained wrong for elapsed time and were retained
only as diagnostics. No kernel, clock driver or QPC correction factor was changed.

## Actual observations

Cases 0 and 1 slept for five seconds. Cases 2-5 executed the same 1,073,741,824-step
LCG workload, in unsampled/sampled/sampled/unsampled order. Each child allocated
and touched 8 MiB; private commitment and resident growth checks passed. The
parent queried the actual child handle, while each child independently recorded
its work boundaries. CPU counters were monotonic and contained by the parent's
interval. All deterministic checksums matched.

| Case | Parent observation | Host elapsed (s) | Guest ticks (s) | Child work CPU (s) | Periodic samples |
|---|---|---:|---:|---:|---:|
| 0 | No periodic sampling | 4.991233 | 5.000 | 0.000000 | 0 |
| 1 | 100 ms sampling | 4.987212 | 5.000 | 0.000000 | 46 |
| 2 | No periodic sampling | 1.869111 | 1.875 | 1.875000 | 0 |
| 3 | 100 ms sampling | 1.868865 | 1.875 | 1.875000 | 17 |
| 4 | 100 ms sampling | 1.879040 | 1.891 | 1.875000 | 17 |
| 5 | No periodic sampling | 1.873871 | 1.875 | 1.875000 | 0 |

No observer CPU-time increment was recorded in these intervals. That is not
zero-cost proof: coarse accounting (observed 15.625 ms steps), scheduling and only
two sampled busy cases limit interpretation. This is also not the breakpoint
recorder's overhead. The fixed workload took similar wall time with and without
periodic queries, but these observations do not establish a performance bound.
QPC/frequency still reported about 0.713 s for a five-second sleep and about
0.267 s for the busy work; host timing independently rejects those elapsed values.

## Validation and lifecycle

Build001 used the pinned NT5 compiler, PE32 imports and exact media readback.
Twelve counter/host-timestamp adversaries plus four framing adversaries were
rejected before launch; fragmented serial lines were also checked. Source and
runtime inputs were frozen and checked before creating the guest process.

The fresh immutable404 child ran once from 2026-10-20 17:26:21 UTC to 17:29:02 UTC.
It requested a normal restart and exited without deadline, forced termination,
host quit, space stop or capture error. The cold audit hashed 6,493 files and
310 directories. One new EventLog6006, raw chronology, five clean hives/raw value
agreement and exact tool/OS/seed checks passed. All owned processes and the serial
reader are closed. No game assets or physical console access were involved.
The raw original-control counters and host marker records are retained publicly;
Windows files/hives and screenshots remain private.

## Limits and next step

CLOSED PASS for this original PC TCG counter/clock control. The earlier PC613
clock failure and short-workload failure remain closed failures. Qualification
must be checked again against host markers on the actual game run; do not assume
QPC is repaired, or transfer these PC timings to an Xbox.

Next is a fresh, uninstrumented RCT process on the exact PC593 saved scene, with
verified reference pixels before and after a longer bounded measurement window.
Record whole-process user/kernel time, memory, client/display/focus and host/tick
elapsed. Keep startup, load, and the settled paused scene separate. Sample counts
are not frame counts. Only then compare an equivalent traced run and measure the
recorder's overhead. Avoid driver optimization or GPU claims until measured costs
justify them. Physical554 synthetic timings remain separate evidence.

No Xbox changes: last dashboard/no owned hook, 596 SOFTWARE restoration still
cold-only. Protected720p, ordinary launcher, saves and transfer ZIPs unchanged;
ZIPs exclude RCT. Other-console, sound, fullscreen/input, boot and1080i deferrals
and paused automation remain unchanged. No hardware reset is needed.
