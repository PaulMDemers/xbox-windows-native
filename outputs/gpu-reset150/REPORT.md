# Explicit reset and resumed rendering

The build003 candidate completed one explicit emulator system_reset, returned to
dashboard FTP, ran the separate native149 probe, and returned normally again.
Its twelve arena snapshots match the independent byte oracle. The matched control
reset rendered a dashboard but did not regain FTP within 150 seconds; native149
was never launched there. The matched pair therefore remains unqualified. Do not
infer that CPU-write eviction fixed networking from this single pair.

|Case|Before reset|Reset|After reset|Strict cold result|
|---|---|---|---|---|
|control001|Six exact snapshots, flushed/closed|One CPU reset and surface invalidation recorded; dashboard screenshot shows DHCP 0.0.0.0|No second launch|FAIL: missing second phase and FTP return|
|candidate001|Six exact snapshots, flushed/closed|One CPU reset and surface invalidation recorded; FTP returns|Six exact snapshots, CPU-write eviction exercised, normal reboot/FTP return|PASS|

Both disks retain clean full E allocation, unchanged existing E contents/chains,
and no top-overlay writes anywhere in F. The control has exactly the eight first
phase output files. The candidate has sixteen outputs across both phases. The
control's six absent second-phase files and missing protocol remain failures;
clean allocation does not override them.

Native150 uses the already tested overlap sequence and flushes/closes every output
before submitting a unique 80 × 40, pitch-320 color surface at arena offset 8,192.
It leaves pbkit active and waits. The supervisor observes the marker upload, records
the trace offset and one reset request, then sends system_reset through the owned
HMP monitor. The trace records CPU Reset (CPU 0), invalidation of the marker,
recreation/upload, and later overlap invalidation. In the candidate, a new FTP
connection launches native149 only after the reset dashboard returns. Its exact
post-reset color/Z16 lifecycle and cold outputs are independently verified.

This is no proof of preserving GPU-only dirty RAM through system reset. Existing
flush_surfaces has its dirty download commented out. Only outputs explicitly
flushed before reset are required to survive. It also does not force a queued
CPU callback/removal race. The marker's pb_busy loop has no guest timeout; the
host marker wait and entire runner remain bounded. No debugger or guest-memory
patch was used. No Windows, physical-console or performance qualification applies.

The control timeout was recorded before a host stop signal requested normal
runner capture/cleanup. The runner's external_capture_complete completion reason
is a cleanup signal, not a test pass; host-stop.json and reset.json retain the
failure. A read-only monitor capture produced reset-screen.png. A preceding HMP
screendump attempt returned unknown command and changed no guest state.

The source review of NVNet reset/link handling is only a lead. Neither additional
link commands nor configuration changes were applied after reset. Candidate FTP
returned about 25 seconds after reset. Control waited the full 150-second bound.
The cause of that difference remains unproven. No new networking patch is justified
by this evidence alone.

All four runs in this turn are closed, recorded in series-closure.json. Source,
fixture, emulator, app and private evidence hashes are retained. Ten negative
reset-evidence checks reject omitted/duplicate resets, invalid ordering, missing
CPU reset evidence and missing marker invalidation. The main.c header inherited
the old Z24S8 description; actual format, operations and oracle here use Z16. The
frozen tested source is intentionally retained verbatim.
