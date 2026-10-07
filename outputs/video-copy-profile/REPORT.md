# First copy-profile attempt: failed before timing

baseline001 is CLOSED and strictFAIL. The log contains ATTEMPT_ONCE, installer
idle, expected1024x576x32 mode,64x64 geometry and FAIL_INITIALIZE0/0/0, followed
by FAIL1/54/162. No pixel stage or timing completed. The original helper combined
message/visibility/initial-copy checks at this label, so the log alone does not
identify the individual failing API. Subsequent framebuffer observation showed
the desktop welcome window; when the log was opened in Notepad, that welcome
window remained topmost over it. Occlusion is the concrete harness lead, not
proof of a driver drawing fault. A fresh helper explicitly raises only its own
window and waits for visibility; no dialogs are dismissed or policies changed.

A running read-only framebuffer observation was followed, after the probe exited,
by logged Notepad input and pause/captures. A visually verified normal Restart
was requested through the Windows dialog. This is diagnostic cleanup, not the
helper's automatic successful protocol. Full cold allocation324dirs6755files/
325directory clusters has zero errors/orphans; five hives and protected hashes
pass, one normal shutdown and no new warning/error/application events. Those
clean checks do not waive the missing workload. audit-failed.py records the
post-failure UI/capture explicitly; its SHA identifies the executed audit code.

The first compile was also rejected by -Werror misleading-indentation before
any binary/guest existed. The correction retained compiler flags. No physical
access occurred; all drivers/modes/cache/device policy remained unchanged.
