# Preserved physical prefix: source-identification search

Read-only host analysis on October 7, 2026. No console access, guest execution,
driver change or modification of the recovery archive.

The preserved physical SetupAPI anomaly contains 111 bytes at offsets
270225..270335. Mean absolute byte difference is 4.42 at lag three, versus
37.56/37.52 at lags one/two. There are 91 high-bit bytes and one DEL. This is
strong three-byte periodicity and a possible interleaved-data lead. It is not
evidence that the bytes are pixels or that the video driver caused corruption.

`analysis.json` records the exact input hash, lag statistics and searches of
6,618 retained recovery files (891,446,701 bytes, no read errors). Neither the
complete 111 bytes nor the first, middle or last 24-byte fragments matched.

`image-search.json` extends the search to supported image formats and PE bitmap
and icon resources, decoded as RGB24/BGR24 in both row directions. It processed
13,159 image frames, including 12,887 decoded resources from 3,330 PE files,
without a match. All 109 decode failures remain listed; these are coverage gaps,
not negative matches. One is the archived desktop untitled.bmp (truncated).
There were no oversized-image skips. No image content is published here.

The searches cover this retained archive only. They cannot exclude absent files,
unsupported resources, scaled/transformed surfaces, live memory, or original
pre-write disk slack. The initial physical restart method remains unknown.
The later emulator interruption produced zeros, not these non-ASCII bytes, and
must remain a separate finding. Do not prefill an experiment with these bytes
to manufacture a superficial match. A future match would identify a candidate
byte source; proving how it reached the file would still require write-path
evidence.

Both scripts refuse to overwrite existing output. `analyze-prefix.py` was
renamed from inspect.py before image scanning to avoid shadowing Python's
standard-library inspect module. The two early image-search startup failures
occurred before scanning (package import/path setup); the completed scan ran
once. Source and report hashes are recorded in provenance.json.
