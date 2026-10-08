# Next discriminator: actual post-close OpenDesktop result

Both new cases are CLOSED. Never relaunch or recollect either candidate001.
Ordinary video-desktop-lifecycle passed three desktop cycles/nine exact files.
This diagnostic failed after the first CloseDesktop returned success: the probe
logged ABSENT_AFTER0 and stopped. The log encodes zero for a nonnull OpenDesktop
handle AND for NULL with last-error0, so it does not settle which occurred.
Preserve the strict failure. No driver fix or relaxed disappearance gate yet.

Create a NEW fresh diagnostic kit, ideally with identical helper bytes, and pin
owned user32 OpenDesktopA and CloseDesktop entry/paired returns, plus
kernel32 GetLastError and ExitProcess. Exact export leads are recorded in
../video-lifecycle-research/owned-images.json. Use actual loaded bases and resident
relocated bytes; capture name/access arguments and returned handle, TEB last-error,
thread/frame, and original/current desktop where readable. Five first-cycle
markers retained the same owner; no watched driver lifecycle function fired.
This is partial evidence only and never proves all future cycles use one PDEV.

Observe helper ExitProcess explicitly. On early exit record diagnostic failure,
remove ALL breakpoints and resume before normal shutdown. The new supervisor must
wait for observer closure, then signal runner cleanup after dashboard return;
the current old supervisor closed the VM with the observer still waiting for
more markers. Its remaining virtual breakpoint died with the owned process; it
was NOT a successful teardown. Do not rewrite that failed trace.

Microsoft CloseDesktop documents handle closure, not immediate object-name
disappearance. Investigate the actual result before deciding whether a separately
defined bounded reclamation observation is justified. Do not silently reinterpret
the current assertion as passed, attribute a debugger timing effect without
evidence, or equate desktop deletion with DrvDisableSurface/DrvDisablePDEV.
All driver/settings/physical baselines stay unchanged. Full ordinary cold gates
and no warning/error/application events remain mandatory for a new attempt.
