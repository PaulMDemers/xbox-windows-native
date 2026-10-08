# Unchanged RAM0109 upload baseline

One fresh ordinary emulator child, no debugger, driver, device policy or registry
changes. Six controlled GDI operations repeat three times: small fill, short
horizontal line, the same line with a tight clip, overlapping primary copy,
disjoint clip fill and a small stretched copy. This is not actual window dragging.

The full-screen topmost window provides a stable unclipped destination. Each
sample resets a 384x256 pattern outside the measured interval. The same operation
runs against an independent DIB reference. Primary readback must match every RGB
pixel; all eighteen reference files must also match a separate host pixel oracle.
Source bytes and reference hashes must remain unchanged. Cursor is hidden.

The existing read-only escape exposes fourteen callback counters, upload count,
64-bit upload byte total and a scanout/shadow coherence check. Snapshot twice before
the reference operation, once after it and once after the screen operation. Quiet
and reference intervals must change no counter; measured counters cannot saturate
or go backwards. Three repetitions must have identical callback, upload and byte
deltas before attributing costs. These global counters cannot rule out all
coincident background drawing. Reject attribution on observed contamination;
preserve pixel/integrity and attribution results separately. No wall-clock/FPS or
physical bandwidth claim. Escape itself scans memory, so timing it would distort
throughput measurements. No counter reset or driver instrumentation is added.

Cold gates: normal restart and dashboard return, no warning/error/application event
deltas, complete allocation audit, five structural hives, unchanged protected
drivers and files, pagefile map and inherited emulator-only null/unsupported-device
policy. Preserve physical0101/video0093, original0088 and immutable0.1.0. Failure
does not permit rerunning this attempt. Any follow-up gets a new child and ID.
