# Next: trace the later dump-initialization failure

Both control001 and candidate001 are CLOSED, collected and verified. Never
relaunch/recollect them. Read REPORT.md,pair-review.json,hal-review.json and
actual records. Candidate0102 is experimental and strictFALSE44+49. Do not
deploy it to hardware or claim dump-write capability.

Use a NEW uniquely named child and frozen scripts to trace the candidate HAL
through IopConfigureCrashDump, successful/failed usage notification, then actual
IopCompleteDumpInitialization entry, file reference, standard-information query,
FSCTL call/return/pending completion and final caller result. Reuse the pinned
kernel review logic from dump-config-trace but adapt paired frame/thread handling
and finish conditions for the now-reachable path. Capture the actual control
code and counted input/output bytes; do not assume a status from Ftdisk44 alone.
Retain bounded capture, resident pins, actual HAL identity, full breakpoint
teardown, normal workload and complete cold audit. Ordinary comparison and
debugger timing remain separate evidence. Do not modify an old frozen snapshot.

Only the exact missing contract shown by runtime evidence can justify another
implementation. No fake completion, event/service/dump suppression, device
policy change or speculative FSCTL patch. Keep strict gates. Real controlled
dump write/recovery in a sacrificial emulator child remains a later gate.
Original physical111non-ASCII corruption still needs a separate discriminator.

All owned processes closed: candidatebuild26564,controlbuild99884,offload57427,
WSLread37398,controlprep88373,runner85940,supervisor46209,audit2892,evidence25358;
candidateprep9108,runner22906,supervisor71419,audit45358; candidateevidence completed
synchronously. No runningguest/observer/build. Deadline13:00UTC October7; check
clock first and no new experiments at cutoff. Emulator-only, never physicalFTP.
