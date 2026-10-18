# Closed snapshot storage521

Lossless host storage work is complete. All236 selected snapshot files retain
original content, lengths, paths, file identities and single-link counts.
228 files compressed; eight system hive copies remained unchanged/uncompressed.
Actual allocated space recovered:139919360 bytes (133.44MiB). No files deleted,
moved or semantically edited. No backing image, firmware, recovery256, console,
shared source/SDK or installed baseline changed.

Application001 exited0 but skipped eight system files: its expected compression
postcondition FAILED. All56 content hashes remained exact;48 compressed, saving
29491200 bytes. The reason for the skip is unresolved. This failure is preserved;
those files were neither forced nor retried. Application002 compressed48 different
files, saving29454336 bytes. Application003 compressed132 further different files,
saving80973824 bytes. Both passed. Each used one bounded explicit compact.exe list,
with independent original historical-record joins and pre/post identity checks.

Independent review001 rehashed all236 files, all plan/source/historical record
pins and actual allocation/attribute results. It confirmed all19 owning roots had
no matching active processes and no emulator/QEMU. Actual C free22288846848 bytes,
E21499871232 bytes at review; C minus unchanged768MiB preparation projection
exceeded20GiB by8704000 bytes. This is a narrow, fluctuating margin, not a promise
of capacity for a later launch. Recheck before preparation; no guard waiver.

All storage tool subprocesses and review closed normally; no emulator preparation,
build, XBE execution, physical access, hook or guest operation occurred here.
Latest physical observation remains518's dashboard return, no startup hook.
520 candidate remains never launched.518 absent receipt/517 strictFALSE and all
historical failures remain unchanged. This is storage evidence, not boot/D3D proof.

Evidence: plan001..003.json, apply001..003.json, review001.json, final-review.json.
