# Measured clip bounds, unchanged RAM0109

This NEW kit preserves the failed video-upload-profile/candidate001. Probe128
replaces the unsupported exact-full-screen visibility assumption with the bounded
uncover procedure already used by the qualified GDI tests. Before each sample it
records GetClipBox type and bounds; the entire384x256 test area must be visible in
a simple clip. The host additionally requires a zero origin. A failure records
the actual bounds. Clip size is an independent measured variable and must repeat
exactly, along with callback/upload deltas, to qualify profile attribution.

Six real GDI operations repeat three times: small fill, short horizontal line,
the same line tightly clipped, overlapping primary-to-primary copy, disjoint clip
fill and small stretched copy. Reference draw executes in a separate DIB; every
primary RGB pixel is compared and eighteen cold reference files must exactly match
an independent host oracle. Drawing gates have not changed. Drivers are unchanged.

Existing read-only escape reports fourteen callbacks, upload count, 64-bit byte
total and scanout/shadow coherence. Idle/reference intervals must change no
counters. Saturation/backwards counters fail attribution, as does any inconsistent
repetition. Global counters cannot exclude all coincident unrelated drawing. No
wall-clock timing, FPS, physical bandwidth or actual window-drag claim. The escape
itself reads the full scanout, so its timing is deliberately not used.

Fresh immutable parent and IDs; one launch then normal shutdown/dashboard. Full
cold allocation, five hives, unchanged protected binaries/helper/startup/pagefile/
emulator device configuration and strict warning/error/application event gates.
No debugger. No physical changes; preserve0101/video0093,0088rollback and0.1.0.
