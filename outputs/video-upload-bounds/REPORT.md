# RAM0109 upload cost measured without a driver change

Ordinary emulator candidate001 and upload attribution PASS. Accepted
2026-10-08T03:08:19.495366UTC. All owned sessions CLOSED: preparation73216,
runner88536, supervisor95044, audit4723. Never relaunch or recollect.

Each operation repeated three times with identical upload/callback deltas, quiet
idle and DIB-reference intervals, and no saturated/backwards counters. All18
samples recorded clip0,0,1024,576. Existing global counters were read; no new
instrumentation, counter reset, debugger, driver or settings change was used.

| Controlled operation | Changed pixels | Upload bytes per operation | Actual DDI |
| --- | ---: | ---: | --- |
|32x16 solid fill|512|2,048|BitBlt|
|32-pixel horizontal line, normal clip|32|2,359,296|LineTo|
|Same line, tight clip|32|128|LineTo|
|Overlapping128x96 screen copy|12,288|49,152|CopyBits|
|Two separated16x16 clip islands, solid fill|512|122,304|BitBlt|
|Small stretched solid source|512|2,048|StretchBltROP|

Every sample caused one upload. The identical line output costs18,432times more
bytes with the normal clip. The separated clip islands cost59.71875times their
changed pixel bytes: the upload spans the196x156 bounding rectangle. Code evidence
matches both observations: XwnLineTo passes NULL dirty bounds to XwnUpload, and
XwnUpload intersects clip.rclBounds rather than enumerating the clip region.

The stretched-copy case is an important limit on the earlier static suspicion:
despite that hook passing NULL bounds, this actual operation only uploaded its
2,048 destination bytes. GDI's provided clip already limited this case. Do not
claim every NULL-bound path always uploads the full screen. Similarly, the
overlapping copy was already confined to its destination and used CopyBits.

Validation:1,769,472 compared RGB pixels,18exact393,216-byte cold references against
an independent host oracle, unchanged sources/reference hashes, scanout/shadow
coherence,60host oracle/protocol checks and6actual-evidence mutations rejected.
Cold allocation326directories6778files327directoryclusters, zero errors/orphans;
five structural hives and protected binaries/helper/startup unchanged. Same96MiB,
1536-cluster pagefile and inherited emulator-only null/unsupported-device policy.
One normal shutdown/dashboard return, zero warning/error/application event deltas.

Probe128 SHAabbe3e7aa0b994142d77407426a8078bdd0ad54cfa3bb24ca397bb9412dd5311;
see pe-review.json and candidate001/preflight.json. The display remains RAM0109 SHA
ed901376d61e70a125fce834e20b366e49a1d632879debbcfedd621c18b6a440.
profile-verification.json ties the actual log, source and verified cold evidence.

Prior video-upload-profile/candidate001 remains a CLOSED strict failure before
drawing, not retroactively passed. Its unlogged visibility rejection cannot be
explained from this run. The new run used bounded uncover and logged the bounds;
although its guard allowed any adequate simple clip, all actual clips were full
screen. No driver fault or original visibility root cause is established.

These are transfer-volume measurements, not timing, FPS, actual window dragging
or physical bandwidth. Global counters cannot exclude every coincident external
draw. Own-driver coherence is not independent physical scanout verification.
Physical0101/video0093,0088rollback,0.1.0 and all prior failures remain untouched.
