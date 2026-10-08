# Position and width discriminator on unchanged RAM0112

One new exclusive ordinary emulator child; no display/emulator binary changes,
debugger, physical access, driver settings or device-policy changes. Preserve all
previous failed and successful attempts. Parent and strict gates match the prior
video-transfer-exclusive run, but this is a new workload, not a speed comparison.

Fifteen geometries, three rotated repetitions, paired memory DIB/primary phases:
solid, horizontal16 and vertical16 each at192x96 copied area with origins(0,0),
(128,0),(0,160). Translation holds bytes, rectangle count, rows and shape fixed.
Six solid widths64/128/192/256/320/384 atheight96 andorigin(320,64) separate width
sensitivity while height/count stayfixed. Both sides move together; this does not
alter source/destination relative virtual addresses or directly measure TLB misses.
The1024x576 pitch remains4096; all changed pixels fit within768x384 verifiedROI.

Keep original500ms calibration,>=250ms final timing gate, dualclock checks,
alternating phase order/brushes, batchlimit1 and no logging inside timed batches.
45 live/fullROI pixel checks,45 reference/45 actual coldreadbacks, exact calls/
bytes, quiet counters, normalshutdown/dashboard, complete allocation, fivehives,
protected files and strict event gates. Exclusive build+xemu leases are checked
before one Windows launch; no preparation/build/audit duringtimedrun. Unrelated
host activity remains outside this cooperative isolation. No physicalFPS claim.

Static lead: XwnUploadBox copies one row at a time using ScreenDelta for both
addresses. The local xemu source indexes software TLB by virtualpage and handles
dirty display pages. These are possible address/shape-sensitive paths, NOT a
runtime attribution. Trace/instrument only after a specific discriminator.
