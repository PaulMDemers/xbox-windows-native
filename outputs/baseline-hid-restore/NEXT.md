# Diagnose the remaining crash-dump configuration event

Both ordinary restored-service cases are CLOSED, audited and verified. Read
REPORT.md and comparison.json. No active guest/tracer. Do not rerun them.
The missing HidServ component diagnosis is supported by live4/0/0 state at both
checkpoints and disappearance of SCM7000. Ftdisk49 still fails strict gates.

Next NEW emulator diagnostic should observe actual IopCompleteDumpInitialization
returns and caller event branch. Read ../baseline-event-forensics/REPORT.md,
kernel-static-sites.json and dump-initialization-static.json. Use owned pinned
kernel/publics and relative RVAs; validate relocated resident bytes. Relevant
sites: entry22e84, handle-return22eaa, query-return22ed8, FSCTLcall22f46 and
return22f4b, finalreturn22ff9; caller status check235c8/event235d0. Capture handle,
thread/frame, NTSTATUS and IOSB before claiming a cause. The parent has a96MiB
pagefile but that does not prove active dump readiness.

The static FSCTL_QUERY_RETRIEVAL_POINTERS call and missing VFAT dispatch are
leads only. That branch would also log IO_DUMP_POINTER_FAILURE; observed deltas
have only49. Do not implement a handler before identifying the actual failing
branch. No service/event suppression, CrashDumpEnabled workaround, speculative
driver changes or physical access. Diagnostic breakpoint runs remain separate
from ordinary qualification, bounded and fully torn down, with cold audit.

Use a fresh child of the restored-service fixture if useful, preserving its
emulator-only null-device/unsupported-device configuration. Its startup helper
path/results must be replaced with unique guarded payloads; never reuse existing
result files or launch an old case. Retain0101/video0093 physical baseline,
0088rollback,immutable0.1.0 and failed evidence. Check current time; work only
until13:00UTC October7, then cleanup/report/pause the existing automation.
