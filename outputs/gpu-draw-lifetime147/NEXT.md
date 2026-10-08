# Continue from primitive-aware build003

Read REPORT.md,series-closure.json,verification.json and
../gpu-evict-regression148/verification.json. Never launch or collect any145/146/
147/148 case again. Build002 failed actual draw retention; do not promote its earlier
clear-only pass. Build003 candidateSHA685f24e317322469cac8710286bf928f7b2accbde5062f3cf8c86a9b21e97890
is the corrected experimental candidate. Physical0101/video0093,0088rollback and
immutable0.1.0 remain unchanged.

Next concrete native discriminator: overlapping surface addresses/pitches, including
Z16, with GPU-write/CPU-partial-write/rebind exact readbacks. Establish which
overlapping cached bindings can coexist from the renderer's overlap eviction rules;
do not claim simultaneous watches without runtime evidence. Follow with explicit
owned-emulator reset and resumed rendering, distinguishing it from pbkit teardown
and dashboard reboot. Swizzled surfaces need their own integer layout oracle.

The request-side and worker-side primitive guards are both required. Current147
tests stores after observed BEGIN; they do not force BEGIN into the short gap
between request and worker. A future bounded scheduling diagnostic must retain
that distinction and must not count injected scheduling as ordinary performance.

Only after these contracts pass should the candidate enter ordinary Windows
correctness/cold validation and the prior top/topx128/lower/window benchmarks.
No performance improvement measured yet. Stay emulator-only.

C is close to the unchanged20GiB guard. Inspect actual capacity before another
build or fixture. Recover space only from proven closed standalone artifacts with
readback-verified offload manifests; never casually move a backing chain.148's
generated filenames contain gpu-regression148-regression148; retain their exact
recorded names rather than renaming completed evidence.
