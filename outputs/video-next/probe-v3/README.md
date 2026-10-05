# GDI probe v3: correctness passed

The prior probe's first readback mismatch was at client coordinate 247,58,
inside the startup dialog covering the test window. Its complex clip region
made the screen-copy comparison invalid. Version 3 restores the test window to
the top, pumps messages and requires a simple clip region covering the tested
rectangle. It also rejects visibility changes during copies or timing loops.
The test stays bounded and Escape cancels it. No display driver or mode changed.

The single `nt5-gdi-baseline-003` launch was accepted at 20:46:16 UTC on
2026-10-05. All four stages passed: DIB copy, upload/readback, overlapping
right/down copy, overlapping left/up copy. Five timing loops completed. The
runner requested a normal restart; dashboard return was observed at 20:47:46.
The owned emulator then closed. There was no physical console access.

[Cold audit](emulator-audit.json) verifies persisted PASS, runner log, payloads
and unchanged qualified FATX/video hashes. [Event review](event-review.json)
compares the actual source fixture's decoded logs with the closed child. Prior
system records 1–46 are unchanged. Records 47–51 contain the known HID service
failure, boot events, Ftdisk 49 and normal EventLog stop 6006. There are no new
application records or delayed-write events in this bounded run. These results
do not constitute a full allocation audit or resolve the known service errors.

The private xemu NV2A resource model remains in this fixture. Timings describe
this emulator only and overlapped host build activity; do not use them to claim
an Xbox drawing speed or an improvement. No acceleration was implemented.
The next performance step is the same visibility-controlled workload on the
unchanged physical baseline, followed by framebuffer/cache/copy profiling.

`supervise.py` records intent before one SITE EXEC, closes failed FTP sessions,
does not use unforwarded passive data ports, and never retries an ambiguous
launch. A dashboard return alone is not a workload PASS. `audit-emulator.py`
extracts logs after cleanup; decode before/after EVT files with the existing
`native-windows-physical-f/decode-legacy-events.py`, then run `review-events.py`.

Host incident: the first cold-audit invocation failed to start qemu-img because
the concurrent build filled C: and WSL fell back to read-only. After archived
traces freed host space, WSL mounted writable and the cold audit completed.
The guest had already returned normally before that audit failure. Preserve
this host limitation when interpreting the timings.
