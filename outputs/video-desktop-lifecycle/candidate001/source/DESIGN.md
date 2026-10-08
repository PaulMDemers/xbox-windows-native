# Supported desktop API experiment

Question: can the unchanged RAM0109 driver render correctly before, on, and after
three temporary desktops created and destroyed with supported NT5 APIs?
This ordinary run does NOT prove DrvDisableSurface/DrvDisablePDEV coverage. A
separate bounded observer must establish actual driver callbacks and identities.

Parent is immutable video-mode-reset/candidate001's prepared fixture, never its
used runtime disk. Preserve every parent/payload/driver, all five hives at prepare,
and inherited emulator null/unsupported-device policy. Change only startup and
add this one-shot probe. No physical access, driver build or mode/registry edits.

For each of three unique desktop names, require absence first, draw an exact
128x96 RGB pattern on the original desktop, release all windows/DCs/bitmaps,
create a desktop with NULL reserved device/DEVMODE parameters, attach the thread,
switch input, draw another pattern, destroy drawing resources, restore the old
thread/input desktops, close the new desktop, require name absence, and render a
third pattern on the restored original. The borrowed GetThreadDesktop handle is
never closed. Retain the original input handle for restoration on any failure.
No desktop heap edits, hooks, window messages to other apps or popup dismissal.

Nine output images must match an independent host-generated pixel formula, not
merely a guest checksum. Ordered log requires every successful API, cleanup,
install-idle and normal-restart result. Any harness failure remains failure even
when cleanup/restart succeeds. Missing results, warnings/errors/application events,
allocation/orphan errors, altered protected binaries, invalid hives or changed
pagefile map fail qualification. Outer owned runner is bounded to 1200 seconds.
The genuine OpenDesktop absence result is observed, not assumed to prove a PDEV
was freed. No timing or physical scanout qualification follows from readback.

Microsoft sources (accessed 2026-10-08):
- https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-createdesktopa
- https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setthreaddesktop
- https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-switchdesktop
- https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-closedesktop

These document Windows 2000 support. Actual owned user32/gdi32 exports are checked
before launch. Documentation alone does not establish internal NT5 lifecycle.
