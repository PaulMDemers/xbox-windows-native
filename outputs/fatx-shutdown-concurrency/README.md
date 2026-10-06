# Concurrent file cleanup and volume flush investigation

Attempt001 is completed and FAIL. Its post-deadline snapshot proves a two-thread
exclusive cycle on the same volume and worker0.bin: cleanup holds DirResource
waiting for MainResource; volume flush holds MainResource waiting for DirResource.
All three worker counters are1, with zero reported API errors. The helper log
contains only its initial line because the timeout reporter also blocks on I/O.
No normal shutdown occurred. Five hives and the full allocation audit remain
consistent, which does not turn the failed run into a pass. The new Messenger7022
event is retained. [Evidence](001/deadlock-summary.json),
[qualification](001/qualification.json). Raw memory remains private.

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

`compile-layouts.py` compiles structure offsets with the original0098 compiler
command, writing only a private diagnostic object. It does not rebuild the
driver. `read-resource-layouts.py` checks the matching owned kernel PDB hash.
The extended timeout decoder labels volume/file/paging resources and active
owner threads. `decoder-replay.json` is an offline validation against the older
completion006 held-shell snapshot: six volumes and their resources can be
traversed, with no exclusive wait cycle observed there. It is not a new run or
evidence against the earlier lost-snapshot shutdown stall. Shared ownership
tables and non-resource synchronization still remain outside this decoder.

`read-probe-symbols.py` pins the executed helper's counter RVAs. If its user
pages are resident in a timeout snapshot, the decoder first verifies its loaded
code section against the reviewed binary, then reads progress/error counters.
Unknown or nonresident user memory is not interpreted as zero progress.

Additional disassembly review places the older volume worker's caller candidate
at driver RVA0xded5: immediately after VfatFlushFile inside the pinned-file loop,
with MainResource held. This is more specific than a generic volume flush wait,
but it still lacks the old resource address and owner needed to prove a cycle.
