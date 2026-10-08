# Second reset diagnostic: incomplete virtual reference capture

Candidate001 is CLOSED, strict diagnostic FALSE. Never relaunch/recollect.
Three cursor phases for case0 were captured and independently rechecked:294912
RGB pixels, zero mismatches;255 resident pins including complete11668-byte
relocated display text. At the first restored-background marker HMP memsave
produced57344 bytes instead of393216, so the observer correctly stopped.
The HMP response was not retained; the underlying cause is unresolved. The
partial raw file is preserved, hashed and compared with the cold file by
failure-evidence.py. No missing bytes are treated as captured.

No mode marker/lifecycle callback was reached by this observer. The bounded
single-step progress check from the first failure is present; its exact journal
is retained. Do not claim it cured an underlying emulator/GDB defect.

All breakpoints removed and guest resumed. Guest completed26GDI cases/78cursor
phases and same-mode reset with normal shutdown1/dashboard. Full allocation,
five hives, protected/payload/startup hashes, pagefile/configuration and strict
event gates pass. Cold success does not repair runtime capture failure.

Original complete verifier remains frozen; separate verify-partial.py records
passedFALSE for exactly this three-frame incomplete case. The next fresh
video-mode-trace3 changes reference acquisition:104 physical snapshots compared
after closure against exact persisted reference files and runtime marker digests.
It retains identical compiled probe/driver and expected-pixel/cold requirements.
