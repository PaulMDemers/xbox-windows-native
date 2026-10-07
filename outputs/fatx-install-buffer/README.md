# Installer syscall-buffer observations

Owned emulator debugger diagnostics using fresh seeds of the unchanged
fatx-install-draw001 control input. No new helper, driver, hive, INF or startup
changes. Normal paired installation results remain separately recorded there.

review-sites.py decodes the pinned owned ntdll syscall stubs. Each live hit must
match its reviewed bytes before arguments are read. NtWriteFile entry records
the requestor, handle, optional byte offset, length and a bounded source-buffer
snapshot. Its return stub records EAX and IOSB; STATUS_PENDING is not treated as
completion. NtFlushBuffersFile and NtClose observations only identify entry to
those calls, not their successful completion. No guest arguments/registers are
modified. Breakpoints and single-stepping perturb timing; no ordinary or physical
qualification can follow from this trace.

Private buffer snapshots are stored by SHA256 under each artifacts directory.
They are not committed. Source requests must be correlated with cold log bytes
and actual offsets, and a null offset pointer must not be interpreted as an
explicit offset. Buffer capture limits and unreadable data remain visible.

Attempt001 armed all four stubs before Windows launch. Its 16000-hit bound was
exhausted by unrelated calls before target warnings. It captured1027 paired
writes without buffer read errors, removed all breakpoints and resumed Windows.
This is a coverage miss. Its exact source is preserved as001/trace-source.py.

Attempt002 uses the same immutable guest input. Only write entry/return are armed
initially; flush/close breakpoints are armed while a matching warning handle is
being watched. It records counts per breakpoint and counts warning occurrences
within requests rather than assuming each line is a separate request. Its final
status, launch, collection and analysis records determine the actual outcome.

Run preparation and preflight to completion before starting the runner. Arm the
tracer before the single local FTP launch. Never relaunch or cold-read an active
disk. Collection follows owned cleanup, once per stage. Both normal shutdown
and retained failures are useful data, but neither promotes debugger results to
normal stability. Preserve any incomplete trace and make a fresh attempt for a
changed capture strategy.

Final outcomes are recorded in REPORT.md; all three cases are closed.
Do not relaunch or repeat completed collection stages.
