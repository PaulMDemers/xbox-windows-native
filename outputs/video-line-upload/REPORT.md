# RAM0110 bounds the upload after EngLineTo

The old path copied the full primary when an ordinary line had no clip object.
The new path passes valid NT5 line bounds to the existing upload routine, which
already intersects screen and clip bounds. Missing,empty or inverted bounds retain
the old full-clip fallback. Rendering,return values,ownership,cache mode,cursor and
surface lifetime are unchanged. Only shadow.c and the two revision values in
enable.c differ from the pinned109 tree.

The exact shadow.c passed241 host cases under ASan/UBSan, including extreme signed
coordinates,offscreen rectangles,invalid bounds,engine failure and inactive surfaces.
These tests use explicit engine/owner shims. Real NT5 behavior is checked separately
by matched ordinary emulator runs in ../video-line-regression: all18 pixel oracles,
cold images,strict event and persistence checks pass. Short-line transfer fell from
2359296 to132 bytes. Broader regression results are recorded in ../video-line-gdi.

Build source tree: e6ebd1273a9214051818173a2e6a4b4b6c825a79.
Parent tree: 1f5aa1cee2bf9b4ca03e5581a8536db9c11db3d2.
Candidate xwnown.dll:91335 bytes,
SHA256 a1d5cf1eea27729a23c06e177f89f862eedcff0a1d0aa002815f4456279b4e98.
build-report.json records locked compiler hashes,definitions,source reconstruction
and the unchanged20GiB reserve guard. patch-review.json pins both original and new
source bytes and the separately verified runtime bounds evidence.

The whole line-bounds diagnostic remains FALSE because its late process-exit
observer hit a nonresident kernel32 header; completed18 paired line intervals
were independently validated without waiving that failure. No physical performance,
additional video mode or new surface-lifetime qualification is claimed. Physical
FATX0101/video0093,original0088 and immutable0.1.0 remain unchanged.
