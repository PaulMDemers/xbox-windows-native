# 1080i hypothesis and discriminating follow-up

The user's hypothesis is plausible, not a diagnosed cause. Interlacing sends
alternating lines in separate fields. Field ordering/timing and reconstruction
on a progressive display can affect stationary fine detail and moving edges.
Microsoft's explanation: https://learn.microsoft.com/en-us/windows/win32/wmformat/to-deinterlace-video

Owned evidence: outputs/text-screen381/REPORT.md records a visually clean
1920x1080 Paint screenshot but damaged-looking TV text, followed by clean text
AND clean full-window dragging at720p with the same Windows drivers. The screen
read path substitutes the RAM shadow; it does NOT prove scanout bytes. The photo
and screenshot were not simultaneous. These observations narrow the issue to a
mode-dependent display path, not a particular device or field bug.

Source: src/boot/xromwell/drivers/video/xwn_hd_profile.c explicitly has separate
720p and1080i register profiles, with1080 marked interlaced,1920x1080/pitch7680.
The flag alone is not runtime proof of correct field presentation. The Windows
miniport exposes the inherited framebuffer; changing its advertised flags alone
would not establish correct scanout or fix the TV. No speculative driver patch.

Next display experiment, separate from this inventory diagnostic: a reviewed
owned pattern containing alternating numbered odd/even rows, thin and two-line
strokes, and stationary versus moving rectangles. Require independent expected
pixels and actual physical framebuffer readback, not only the RAM-shadow capture.
Compare paused and moving cases, record actual timing/field settings and same-TV
video. If framebuffer bytes are exact but line content differs on output, isolate
encoder/adapter/display processing using a second known-good display/adapter path.
Do not blame the adapter from a clean shadow screenshot alone. Do not relaunch
closed381 cases, force1080p, change EEPROM flags, or replace the720p demo default.

720p is progressive; lower modes may include480i, so not every lower resolution
is necessarily progressive. Current production/demo advice remains720p, which
the user observed as clean. This review did not change the physical video mode.
