# Concurrent file cleanup and volume flush investigation

The earlier shutdown-installer-windows001 run did not return to dashboard. Its
post-deadline stack scan contained a cache worker at FATX Close+0x2e, a volume
flush worker inside VfatFlushFile+0x53, and svchost at Cleanup+0x32. Matching
FATX0098 disassembly places these return addresses immediately after acquisition
of DirResource. Winlogon waits in PopFlushVolumes. They are code candidates,
not an unwind or a proven ownership cycle; that older capture discarded RAM.

The exact873d6b4ff9505e71da119abd99aba301013e1749 source contains both
MainResource->DirResource paths (ordinary/volume file flush and extending writes)
and DirResource->MainResource paths (cleanup, overwrite-create, enumeration,
selected set-information). This warrants a concurrency investigation. Changing
one function's order without handling namespace/lifetime/revalidation in all
callers would be premature. No driver source or installed binary is changed.

The new original no-CRT helper starts three threads together: two repeatedly
create/write4097 bytes/flush/close separate regular files; the third repeatedly
flushes an existing C: volume handle. Each targets500 completed iterations.
Only the owned emulator fixture is used. No raw-volume reads/writes, volume
lock/dismount, device-policy edits, UI actions or debugger intervention occur.
The log and regular files live in an exclusively created C:\xwncc01 directory.

On completion, exact counts and zero errors are required, followed by pending
installation check and normal restart. If threads have not finished in180s,
the helper remains alive for diagnosis. It does not terminate stuck threads or
force restart. The host waits600s for dashboard return before a single paused
RAM snapshot;900s runner limit leaves time for capture and owned cleanup. Raw
memory remains private. A timeout is a failed diagnostic, not a completed soak.

The parent is the normally shut down null-placeholder001 configuration. It
retains historical01B0/01B4 failed-install flags and the emulator-only test-device
null package. Those limits remain explicit. FATX0098/video0093, registry hives,
trace and original workload payloads remain unchanged during staging.

RosBE build uses warnings as errors and NT5 subsystem/import checks. Initial
compilation rejected an ambiguous single-line for loop; braces corrected it
before any binary ran. Cold collection requires owned runner cleanup, exact
last-round worker file bytes, log completion, unchanged selected binaries,
five structural hives, event deltas and full F allocation. No hardware result
or fix for the earlier stall can be inferred from compilation or one clean run.
