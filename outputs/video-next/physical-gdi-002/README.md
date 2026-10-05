# Physical GDI baseline retry 002

The user reported that their attached "razor chroma ornata" keyboard had stopped
the preceding attempt in Xromwell, unplugged it, rebooted, and requested a retry.
Attempt 001 was collected before this launch: startup restored, no probe/runner
logs, no changes to Windows event logs, all baseline hashes intact. The precise
USB identity and cause of that reported boot hang remain unverified.

This separate attempt was accepted at 2026-10-05 21:17:54 UTC. The four-minute
observer saw FTP offline but no subsequent dashboard return. Screen state has
been requested; there is no basis yet to claim a benchmark PASS or a crash.
No second launch was issued by the observer. Do not relaunch this attempt.

Only the new `/F/xwngdi02` helper directory and temporary startup script were
written. All six release driver/loader hashes matched before launch. The probe
is the unchanged v3 executable, SHA256
`7d90f3c0d6f8bb4615792324c749f4f2bfcf8663928d93ac5a3b41f9afec23fb`.
The runner differs only in its private working paths and passes the NT5 import
review. Logs use exclusive creation; it requests a normal restart only after
successful probe completion. No video mode, cache attribute, or driver changed.

`trial.json` records the actual state. Collection is pending and test startup is
still installed. Once dashboard FTP is available, invoke `trial.py collect` with
the existing FTP environment. It verifies and restores the original startup
first, then preserves results/event logs and verifies baseline/helper hashes.
Run `qualify.py` afterward. Record any manual reset separately from the runner's
normal restart evidence. Do not erase logs, reuse this identity, or issue another
Windows launch to obtain missing results.

The observation process has exited. No owned emulator/build/observer is left
running. A screen-state reply is the remaining evidence needed to choose recovery.
One passing sample would measure only five synchronous 256x128 GDI operations,
including flush/message/visibility overhead; it would not establish window-drag
FPS, repeated-run variance, or general storage stability.
