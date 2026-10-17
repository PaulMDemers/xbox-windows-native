# 425: native file-call diagnostic

The unchanged 423 operations are surrounded by seven no-inline checkpoints in
a new original probe at preferred image base 0x17000000. The original operation
body reconstructs exactly after removing these additions. The probe records
its actual PID, TID, module bases and four GetProcAddress results; it neither
hooks APIs nor alters provider inputs, return values, files or registry settings.
It still writes the original schema423 result and requests ordinary restart.

One owned GDB session observes NtCreateFile, NtOpenFile, NtQueryAttributesFile
and NtQueryFullAttributesFile at entry and their reviewed native-stub return.
The exact owned SP4 stubs use int2e. Each pair is keyed by actual kernel thread,
process, user stack and API, allowing distinct threads and nested calls. The
checkpoint cross-checks kernel PID/TID/image fields against native Win32 results;
their layout source was previously reviewed for the same cold kernel hash.
Actual checkpoint/header/stub bytes are pinned. This is debugger evidence,
not an ordinary-run or performance qualification.

Only bounded OBJECT_ATTRIBUTES, counted UTF-16 filenames, scalar parameters,
statuses and successful open handles/IO_STATUS_BLOCKs are read. No private-key,
DPAPI, file-payload or credential buffer is captured. Relative root handles stay
unresolved; the trace must not invent an absolute name. Background-process calls
remain separately labeled, and temporal overlap with DPAPI is not RPC causality.
STATUS_PENDING cannot count as a proven final completion. Pre-arm unpaired
background returns remain explicit. All owned calls must be paired by the final
checkpoint. Bounds are 4096 hits, 2048 filename bytes, 360 seconds after arming.

The fresh runtime comes from a new prepared child of unchanged closed406, never
an executed423/424 child. It contains only one additional diagnostic executable.
Boot, ordinary logon and typing the Run path precede tracing. After visual path
verification the tracer arms its first breakpoint and submits one Enter itself,
using the same held monitor lock. It removes every breakpoint, verifies physical
read mode0 and resumes the guest on completion/failure. The owned runner permits
900seconds total; its supervisor permits960seconds, with no repeated launch.
The hardware wizards remain unchanged. Normal restart, orderly host exit and a
complete cold FATX audit remain required. Failure never licenses a silent retry.

Original423/424 failures and the physical demo remain untouched. No namespace
fix or gate waiver is part of425. Actual requested names/statuses, not predicted
provider behavior, determine the next storage-design investigation.
