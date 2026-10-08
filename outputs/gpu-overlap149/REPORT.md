# Overlapping addresses, pitch changes and Z16

The unchanged build003 xemu control and candidate both pass the native149 test.
Each run produces six exact 32,768-byte arena snapshots, performs 50 CPU stores,
and returns normally to the dashboard. Cold inspection verifies full E allocation,
all existing E file contents and chains, the exact eight new output files, and no
top-overlay writes anywhere in F. All cases are closed; never launch or collect
them again.

For each color/depth arena, a GPU clear fills surface A without a CPU readback.
An overlapping surface B uses a different pitch and receives a partial clear.
The probe captures the entire arena, patches 25 pixels through volatile CPU stores,
captures again, then rebinds A and performs another partial clear before the last
capture. The independent oracle includes all pitch gaps and untouched tail bytes.

|Property|Color|Depth|
|---|---|---|
|Format|A8R8G8B8|Z16|
|Dimensions|64 × 64|64 × 64|
|A pitch|256 bytes|128 bytes|
|B pitch|320 bytes|192 bytes|
|B relative address|4,096 bytes|2,048 bytes|

Sparse lifecycle evidence proves A is downloaded before overlap invalidation and
B is uploaded from the preserved memory. On the subsequent CPU patch, the candidate
records a cpu-write eviction of B; the control retains B until overlap replacement.
Both then recreate/upload A and return identical bytes. The verifier requires the
exact 14-event sequence for each arena, including addresses, dimensions, pitches,
linear layout and bytes per pixel. Forty-eight negative checks reject missing
downloads, incorrect offsets/pitches/Z16 widths, wrong eviction causes, wrong store
counts and corruption of tested or untouched bytes.

This tests replacement of overlapping cached surfaces. The pinned surface_put
invalidates existing overlaps, so simultaneous overlapping CPU watches are not
established. It does not force the request-to-worker BEGIN race. No Windows boot,
physical-console test, performance improvement or driver change is claimed.

Source, app, SDK, fixture and emulator hashes are recorded in build-inputs.json,
build.json, frozen-inputs.json, fixture records and verification.json. The emulator
pair is the existing xemu-cpu-surface-evict/build003 pair, unchanged. The following
reset150 kit tests explicit reset and resumed native rendering separately.
