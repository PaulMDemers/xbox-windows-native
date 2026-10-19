# PC585: prelaunch integrity failure, closed

RCT did not launch and no save was created. The guest verifier stopped after
31 files because the generated metadata was wrong. An unrestricted `582` to
`585` replacement changed the expected CSS35.DAT size from 5,823,602 to
5,853,602 bytes and renamed one expected track from `u(5827).td4` to
`u(5857).td4`. The retail files themselves were not changed by this substitution.

The independent cold SHA256 inventory confirms all 502 copied assets match
the pinned retail manifest. Thus this is a harness-generation failure, not
evidence of damaged game assets or a game/storage compatibility failure.
See [the metadata comparison](asset-header-review002.json) and
[the closure record](final001.json).

Windows restarted through its normal UI. The owned VM exited normally, a new
EventLog6006 was present, all five audited hives were clean, and the game
registry subtree was unchanged. No owned process remains. Phase2 was never
admitted; its separately built observation helper was not executed. The overall
experiment is closed and must not be reopened or used as a parent.

Preserved failures include build001's signed-comparison compiler error, the
first metadata review's KeyError on the renamed track, the guest verifier
failure, and the automatic screenshot race after QEMU had already exited0.
The first display-change confirmation also timed out and reverted; the second
was accepted and visually verified at1024x768 before the copy.

Storage receipts record deduplication of fifteen inactive identical emulator
executables into hard links, preserving every path and exact contents, plus
lossless compression of closed582/584 disks with unchanged hashes. Neither
operation reopened those runtimes. No Xbox access occurred in this attempt.

The corrected, independently checked preparation is [PC586](../rct586/REPORT.md).
