# PC623 closed PASS: original busy-versus-paced timer controls

Fresh immutable404 ran 2026-10-20 from20:53:16.768534Z to20:58:04.600537Z and
restarted normally. One admitted eight-case run; no game or physical Xbox.
Two exact compiled tools were copied; CD ejection was read back before launch.
No host input/captures or heavy host work occurred in the measured intervals.

## Measured result

Each CPU window lasted20.046–20.063 seconds; independent host agreement was
within17.263ms. The five-second sleep measured4.990391309 seconds on the host.
All subject CPU was accounted for by its actual main thread. Observer CPU
increments and paced subject CPU increments were zero at coarse resolution;
these are not proofs of zero cost or zero sampling overhead.

| Case | Sampling | CPU seconds | Payload calls | Subject seconds |
|---|---|---:|---:|---:|
| busy timeGetTime | off | 20.03125 | 436,645,888 | 20.078 |
| paced timeGetTime | off | 0.0 | 1,284 | 20.063 |
| busy GetTickCount | off | 20.046875 | 971,673,600 | 20.063 |
| paced GetTickCount | off | 0.0 | 1,284 | 20.062 |
| busy timeGetTime | on | 20.046875 | 408,563,712 | 20.078 |
| paced timeGetTime | on | 0.0 | 1,284 | 20.078 |
| busy GetTickCount | on | 20.046875 | 971,366,400 | 20.078 |
| paced GetTickCount | on | 0.0 | 1,284 | 20.078 |

CALLS counts payload-loop calls, excluding the initial selected-timer read and
GetTickCount setup/deadline calls. Subject windows enclose the20s CPU windows;
the unchanged1s boundary gates all passed. See timing-bound-review001.json.
Busy modes batch4096 payload calls between release/deadline checks. Paced modes
request Sleep(10) after each call. Counts are not exact20s API counts, pristine
API latency, game FPS or a measured optimization gain. Only one interval per
condition was run; observed/unobserved count differences do not isolate overhead.

Each observed case yielded224 balanced snapshots, with0/1 suspend/resume and
0ms maximum hold at coarse tick resolution. Busy timeGetTime:155 WINMM,43
original subject,26 ntdll. Busy GetTickCount:93 kernel32,68 subject,63 ntdll.
Both paced cases:224 ntdll. Stable module bounds and identities passed.

Exact protected DLL identity and export/instruction review maps the155 WINMM
samples to88 timeGetTime-body and67 direct arithmetic-helper locations. Paced
ntdll locations map to NtDelayExecution's syscall return; busy ntdll locations
map to NtWaitForSingleObject's return, consistent with the original zero-timeout
release checks. An API name or ntdll location alone does not prove a blocking
wait. No kernel stacks/runtime code bytes or CPU-time sample percentages.

This qualifies the method's busy/paced contrast and makes621's timer-polling
lead more concrete. It does not establish RCT's call count, exact hot-loop body,
or whether pacing RCT preserves game behavior. Do not replace timers, add sleeps,
or patch drivers based on these controls alone. Xbox FPS/acceleration remain
unmeasured by this work.

## Correction and closure

622 failed the unchanged1s ending bound: the subject continued through buffered
log flushing. Preserve its failed review and closed runtime.623 moves only the
release/join block: after end counters and module capture, before buffered output.
Host source checks confirm exact workload, oracle and sampling loop, apart from
namespace and that one block movement. All seven suspension cases,23 snapshot/
timer negatives and five serial negatives passed. No bound was relaxed.

Cold audit passed6495 files/310 directories, five clean hives, exact tools/OS/seed
and one new normal EventLog shutdown. All owned processes closed; no forced quit
or termination. Never reopen/recollect/parent closed runtimes. No new archival
cleanup was necessary; capacity guards passed. No physical access: Xbox last
known dashboard/no owned hook;596 SOFTWARE cleanup remains cold-only.720p,
ordinary launcher, packages and deferrals unchanged; automation paused.
