# Upload producer accounting119

This is an observation build, not a speed fix. Same118 rendering, upload/clip
algorithm, surface ownership, UC mapping and fallback. Scalar stores and body
clocks OFF; proven206 text bounds ON both. Only XWN_UPLOAD_ACCOUNTING differs.

Publish local completed-copy boxes/bytes/fallbacks once per upload after Eng/copy,
under the existing membership semaphore. Never store a mutable current-callback
tag or hold a semaphore across Eng/render/copy. Fifteen explicit kinds cover all
fourteen DDIs and both surface-lifecycle uploads. Bounded fixed arrays, saturating
32/64-bit arithmetic and an error/overflow gate make partial data unusable.
Read-only632-byte escape119 is atomically copied under that semaphore; no pointer,
reset, clock or writable driver interface is exposed. Requests with zero boxes
remain visible; NULL rectangle does not itself imply a full-screen/redundant copy.

Use a fresh fixed neutral-backdrop/window movement workload. Separate movement,
forced own-client repaint and readback accounting so readback/background work is
explicit. Require geometry and exact owned pixels/whole RAM-scanout coherence,
counter conservation and actual enabled coverage; off counters remain zero.
Global counters still include background work. Timings are descriptive, not FPS
or a clean claim of optimization. Final ordinary cold audit and normal restart
remain required. No physical deployment before fresh emulator evidence review.
