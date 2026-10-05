# GDI probe v2

This revision uses a dedicated CS_OWNDC window class with no background painter.
It pumps pending startup messages for two seconds, checks client geometry and
records the clip rectangle. No display mode or driver is changed.

Correctness stages stop at the first failure:

0. DIB-to-DIB copy and direct memory comparison.
1. DIB upload to screen followed by screen-to-DIB readback.
2. Fresh upload, overlapping screen copy right/down, then readback.
3. Fresh upload at the displaced origin, overlapping left/up copy, then readback.

On mismatch it logs stage, coordinates and expected/actual 24-bit RGB values.
API failures are logged separately. Timings run only after every correctness
stage passes. The temporary window is closed after completion; the existing
one-shot runner requests a normal restart only for a successful probe exit.
Failure leaves the guest running for investigation.

`Build-Probe.ps1` produces a separate artifact; `build-review.json` records import
compatibility against captured physical NT5 DLL exports. Preparation creates a
new child of the prior qualified fixture and preserves its source hash. The
fixture retains the qualified filesystem/video drivers; the newly reconstructed
package is not installed in this probe run. Run identity is
`nt5-gdi-baseline-002`, and its logs must not overwrite version 1 evidence.

Prelaunch recovery: an initial dashboard connection closed early; a subsequent
passive directory transfer was refused. The dashboard then exhausted its FTP
session slots. The owned emulator was reset before any Windows launch. A single
Windows launch was later accepted and recorded in `launch.json`. This was
fixture/transport recovery, not a Windows workload or driver failure. The
physical Xbox was not accessed.

Result: DIB copy passed, but screen readback failed at client coordinate 247,58
where the captured startup dialog overlapped the test. The complex clip region
and returned gray pixel match that explanation. Timings were skipped. The owned
emulator was closed after the failed probe; no clean shutdown is claimed.
The visibility-controlled [version 3](../probe-v3/README.md) subsequently passed
with the same qualified drivers, supporting a probe setup error.
