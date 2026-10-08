All three color-cursor attempts CLOSED. Ordinary video-color-cursor strict PASS;
video-color-scanout incomplete diagnostic FAIL; this diagnostic strict PASS.
Read REPORT.md, verification.json, oracle-tests.json, pair-review.json and
history-review.json. Never relaunch/recollect any of these cases.

Next follow ../video-color-scanout/TRANSITION-PLAN.md using fresh unique fixtures.
Enumerate actual modes; investigate whether same-mode CDS_RESET really reaches
DrvAssertMode or surface/PDEV replacement on NT5. Require observed callback
entry/return/lifetime evidence and independently correct pixels afterward.
A successful API or source inspection is not transition coverage. Keep driver
unchanged until an actual failure justifies a patch. Boot-video/crash ownership
is separate from a mode reset. Do not invent new resolutions or cache changes.

Preserve physical FATX0101/video0093, original0088 rollback, immutable0.1.0,
qualified128GiB recovery and every failed record. Emulator only. Original111-byte
physical damage/restart remains unresolved. C:about22.7GBfree; keep20GiBbuildguard
and inspect actual capacity before further builds. No owned sessions remain.
