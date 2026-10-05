# Exploratory shutdown popup investigation

This single owned emulator run used the unchanged candidate0096 binary and
120-second settling protocol from ../video-direct-map-settled. It was debugger
interrupted and cannot qualify an ordinary boot or a physical deployment.

The first GDB attachment timed out before its handshake completed, leaving the
guest paused. harderror-attach-failure.json preserves that failure. The corrected
handshake resumed the same guest with a breakpoint at the matched kernel's
NtRaiseHardError (0x8247282E). No hard-error event was captured. The guest returned
to the dashboard and the supervisor closed the owned emulator; the debugger then
reported connection reset in harderror.json. An empty capture does not establish
that Windows raised no error or identify the popup's creation path.

Cold audit.json records successful GDI pixel checks, direct-RAM UC mapping,
payload checks, a normal shutdown event and one dashboard return. It also records
two new Application Popup events: rundll32.exe DLL Initialization Failed because
the window station was shutting down. diagnostic_checks_passed is false and
ordinary_boot_qualified is unconditionally false. No root cause or fix is claimed.

Owned run nt5-video-shutdown-probe-001 launched at23:00:39 UTC October5,2026;
cleanup completed at23:05:47 UTC. All debugger/supervisor/emulator processes are
closed. Runtime snapshots contain selected observations, not retained RAM dumps.
No physical access or driver deployment occurred in this diagnostic run.

Next work is to inspect the popup creation path and complete mapping stop/remove/
restart lifetime before strict ordinary validation. Preserve both normal failures
and the interrupted diagnostic evidence; a timing-only clean retry is not proof.
