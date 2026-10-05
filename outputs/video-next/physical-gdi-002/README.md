# Physical GDI baseline retry 002

The user reported that their attached "razor chroma ornata" keyboard had stopped
the preceding attempt in Xromwell, unplugged it, rebooted, and requested a retry.
Attempt 001 was collected before this launch: startup restored, no probe/runner
logs, no changes to Windows event logs, all baseline hashes intact. The precise
USB identity and cause of that reported boot hang remain unverified.

This separate attempt was accepted at 2026-10-05 21:17:54 UTC. The four-minute
observer saw FTP offline but no subsequent dashboard return. The user's photo
subsequently confirmed `E0580001(0D,4,C000003E,10)`. Source review identifies the
one-shot video logger rejecting nonzero trace content at offset16. The benchmark
launcher omitted the existing preserve-and-reseed step. This is a harness defect,
not a passing benchmark or evidence of a GDI rendering defect.

Only the new `/F/xwngdi02` helper directory and temporary startup script were
written. All six release driver/loader hashes matched before launch. The probe
is the unchanged v3 executable, SHA256
`7d90f3c0d6f8bb4615792324c749f4f2bfcf8663928d93ac5a3b41f9afec23fb`.
The runner differs only in its private working paths and passes the NT5 import
review. Logs use exclusive creation; it requests a normal restart only after
successful probe completion. No video mode, cache attribute, or driver changed.

Collection completed at 2026-10-05 21:24:51 UTC after the dashboard returned,
restoring original startup first. No probe or runner log exists. Before/after
event logs are byte-identical, and all baseline/helper hashes match. The preserved
4096-byte trace has the correct marker and41 records; its first nonzero byte
after the marker is offset16, exactly matching the photo. See
`photo-diagnosis.json` for the source interpretation and trace hash.

Qualification is false because Windows stopped before the workload. A normal
benchmark shutdown was not recorded; the return following the photo must not be
counted as one. This attempt is closed and must not be relaunched or recollected.
The corrected, separately identified retry is `../physical-gdi-003`. Its launcher
preserves and verifies the trace before resetting it, checks the exact seed again
before launch, and refuses unknown trace identity/size or failed readback.
