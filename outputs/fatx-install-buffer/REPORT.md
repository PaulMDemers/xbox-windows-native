# Installer tracing: three capture misses, clean cold checks

7 October 2026 UTC. None of these debugger attempts captured the target warning.
Their clean shutdowns and disks do not remedy missing trace coverage, reproduce
the physical corruption, or qualify a driver change.

| Case | Capture outcome | Verified buffers | Pairing/cleanup |
|---|---|---:|---|
| 001 | 16000-hit limit before target | 1027 | Paired returns; breakpoints removed |
| 002 | Unreturned-write guard in unrelated activity | 495 | One pending write retained; breakpoints removed |
| 003 | 16000 write entries before target | 15841 | Only target returns armed; breakpoints removed |

All three guests resumed after tracing, completed one normal shutdown, returned
to the dashboard, and were closed before cold collection. The log grew by5300
ASCII bytes with the220-byte target warning intact at270225. Selected binaries,
five structural hives, installed GPU binding and complete F allocation passed.
No allocation errors or orphan clusters were found. Same untouched draw001
pre-install input; no guest code, drivers, startup, INF or hive changes.

Case003 retained unreadable-buffer errors. Case002's missing return is an
incomplete debugger observation, not proof of a failed filesystem write.
Neither a null byte-offset pointer nor a matching string identifies a unique
cold log occurrence. Flush/close observations were entry points only.

Per-case buffer-analysis.json and trace-summary.json pin the private raw trace,
source and cold evidence. Raw buffers and raw trace metadata remain local;
they were not discarded. Sources001/002 are preserved in each case directory;
root trace.py is the exact003 source. Compilation in write-layouts.json derives
candidate0101 driver offsets without rebuilding a driver. Header FILE_OBJECT
size128 is not an independently verified native NT5 tail size.

The next attempt increases the bounded capture window and retains only warning
requests. The unchanged physical111-byte anomaly remains unresolved.
