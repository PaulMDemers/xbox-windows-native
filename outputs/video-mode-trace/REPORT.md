# First reset diagnostic: preserved observer failure

Candidate001 is CLOSED, strict diagnostic FALSE. Never relaunch/recollect.
Exact same probe124 and RAM0109 as the successful ordinary video-mode-reset.

The observer captured case0's three cursor phases and restored background, then
case1 phase0: five raw/reference frames,491520 RGB comparisons, zero mismatches.
All256 resident pins rechecked; complete11668-byte relocated display text matches.
Before the next cursor phase, step journal entry after capturing case1 phase0 has
identical before/after values for all ten registers and thread/process/image.
EIP4203173 (0x4022a5), ESP2291396. The cursor breakpoint was absent during the step.
The following stop again supplied case1 phase0, when phase1 was expected. Raw
arguments, registers, owner and single-step records are preserved. The ordering
assertion correctly failed. This is concrete no-progress evidence, not proof of
the underlying GDB/xemu cause or a guest display-driver fault.

No mode marker or lifecycle callback was reached by this observer. Full breakpoint
teardown and guest resume succeeded. The guest then completed all26cases/78cursor
phases, accepted same-mode reset and restarted normally. Full cold allocation,
five hives, protected/payload/startup hashes, pagefile/configuration and strict
event gates pass. That cold success does not repair missing runtime coverage.

The original complete verifier remains frozen; verify-partial.py independently
rechecks the exact five-frame incomplete case and records passedFALSE in
verification.json. New video-mode-trace2 addresses the observed single-step
condition with bounded real steps and additional chronology indexes. It uses a
fresh child, same compiled probe/driver and unchanged pixel/cold gates.
