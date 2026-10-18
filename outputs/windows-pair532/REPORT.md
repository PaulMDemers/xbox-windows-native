# First Windows boot succeeded; second returned black to dashboard

The user reported Ready after a newly requested full power-off/on. The first
ordinary launcher request was accepted at18:34:24UTC. The user reported Windows
at the desktop, then Rebooted in response to Start/Shut Down/Restart instructions.
Independent cold readback found five clean registry hives and new EventLog6009,
6005 and6006 records. The6006 normal-shutdown delta was1. Ftdisk49 also recurred:
this is not a strict clean-event qualification. No new application records.

The second request at18:37:45UTC used the same installed300624-byte XBE, same path
and same FTP method, without a power cycle or host trace/file reset. Launcher SHA:
`6240a801d97c4894e56d516a934059da056446fb77cf895b5364bdd6cd24be9a`.
User: "This time it booted to a black screen then back to the dashboard".
All ten collected files were byte-identical to the first run's after-state,
including five hives, both event logs, video trace, normal startup and launcher.
No new Windows startup/shutdown records were found. Absence does not locate the
failure or prove that no early Windows instruction executed.

This is one observed success/failure pair with unchanged executable and no
intervening reported reset. It supports studying ordering/retained-state effects,
but does not prove deterministic alternation or distinguish retained state from
another intermittent cause. All532 runtime records are CLOSED. A separately
predeclared533 third invocation tests immediate recovery after the failed second;
no fourth run is planned. Read533 for that independent result.

The installed driver's retained source and cache enable TRACE_REUSE; its binary
hash matches the installed policy. Old trace records are cleared in memory by the
driver after validating the header/length. No host reseeding was performed. The
ordinary Xromwell wrapper has no added one-shot receipt logger. No guest binary,
firmware, startup hook or driver was changed; dashboardC was not accessed.

Preserved harness failure: before-review001 incorrectly required a terminating
NUL beyond the full16-byte marker. That command failed, but orchestration wrongly
continued to launch1. The file itself matched closed531's independently collected
bytes. Corrected review002 uses the established video-trace-reuse/audit.py marker,
rejects18 malformed inputs and passed. The controller's baseline checks passed
before launch; this additional review sequencing failure is retained rather than
represented as a clean prelaunch gate. A separate successful presecond001 was
required before launch2. Also corrected unexecuted audit wording: the EVT decoder
scans valid records and may include stale ones outside the active ring; it does
not prove complete active-ring membership. Prior source/review are retained.

Thirteen actual admission/request host tests used modeled evidence and FTP;
physical evidence is the watchers, exact cold files and decoded new events.
No full allocation audit, GPU/game support, boot fix or release promotion.
