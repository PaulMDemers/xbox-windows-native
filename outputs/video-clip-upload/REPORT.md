# RAM0112 removes complex-clip gap copying

The previous uploader copied the bounding rectangle of a complex region,including
large untouched gaps. RAM0112 restarts relevant clip enumeration after rendering
and copies only intersections with the actual rectangles. The original full-box
copy remains the bounded fallback. Simple clipping and RAM0110 line bounds remain.
Only shadow.c and identity values in enable.c change; the diagnostic0111 helper is
not part of this candidate.

The actual uploader passed385 ASan/UBSan host cases,including the retained line
tests,final nonempty FALSE batches,empty TRUE batches,multiple batches,offscreen
rectangles,invalid counts,inverted rectangles and budget exhaustion. Every pixel,
guard word and copy counter was checked with explicit engine/enumeration shims.

Matched ordinary emulator control/candidate tests passed18 exact images and strict
cold gates. Two distant16x16 rectangles now copy2048 rather than122304 bytes;
all18 samples total45120 rather than2620032 bytes. Full details and pinned actual
records are in ../video-clip-regression. Broader GDI results are separate in
../video-clip-gdi. Byte volume is not a physical speed measurement.

Source tree: ef5d01ee07931126dbf202bf98bdf3fefaf23bc6.
Parent RAM0110 tree: e6ebd1273a9214051818173a2e6a4b4b6c825a79.
Candidate xwnown.dll:91785 bytes,
SHA256 ba6e37ddb2bdaad05cc12585fe9c986bdb5203c94101443500ebf1c547c81da8.
Build27625 CLOSED. Compiler/definition/source pins are in build-report.json.

The runtime prerequisite exposed a mistaken count assumption in the first oracle;
the original failures and the corrected owned-binary-backed verification are both
preserved in video-clip-enum2. No guest error was suppressed. The earlier incomplete
observer and diagnostic host-build CRLF failure are also retained.

No physical access or deployment. Preserve installed FATX0101/video0093,original0088
rollback,immutable0.1.0 and completed128GiB work. See NEXT.md before further work.
