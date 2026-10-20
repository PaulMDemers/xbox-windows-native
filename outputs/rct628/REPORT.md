# PC628 matched RCT timer callers: scoped PASS

The fresh immutable404 child completed one matched paused Forest Frontiers
measurement and normal restart at 2026-10-20T23:27:10 UTC. The scene matched the
retained save reference exactly across 165,600 interior pixels before and after
the measurement. Nine private captures were inspected. The camera move and reload
were independently visible and checked; input submission alone was not the proof.

RCT used 19.890625 CPU seconds (13.40625 user, 6.484375 kernel) in 20.016 guest
seconds / 20.025054937 host seconds. The main thread accounted for 19.875 seconds.
Observer CPU rounded to zero at the available accounting resolution, not zero
cost. The maximum observed suspension interval was 16 ms. This is a sampled PC
emulator result, not game FPS, Xbox performance, or a native-GPU result.

All 237 bounded instruction and stack reads succeeded. Of these, 171 instruction
snippets matched the exact loaded-address-adjusted DLL bytes; 64 were packed RCT
live-code captures, and two USER32 locations were left unreviewed. All 87 captured
fixed-version WINMM timer frames led to the same RCT return RVA 0x1828d6. Captured
caller instructions and the corresponding indirect target confirmed timeGetTime.
This validates a game timer caller, not a CPU-time percentage, a call frequency,
a complete loop interpretation, or proof that the timer causes the CPU cost.
The remaining 150 observations were outside the supported timer-frame capture;
they are not 150 failed timer reads. No functional game or driver change was made.
Raw code, stacks, call instructions and target bytes remain private.

Cold readback enumerated 7,004 files and 315 directories, with five clean hives,
unchanged protected OS binaries, exact helper bytes and save, restored temporary
game registry, and one new EventLog 6006. The audit is not an independent NTFS
allocation-bitmap audit. All owned processes are closed. final001.json pins the
closed evidence; never rerun, recollect or parent this runtime.

Initial preparation missed the 22 GiB admission threshold before allocating any
child. Preserve prepare-space-refusal001.json. Closed helper CDs were losslessly
archived with roundtrip verification in archive001.json. Two display confirmations
reverted during setup; display-preparation001.json preserves them. The corrected
1024x768/16-bit desktop was verified before the sole game launch. Neither reverted
setup attempt produced a game measurement. Earlier failures remain preserved.

Next: a bounded physical Xbox process-cost comparison with fresh clock/counter
sanity, the same saved scene, explicit mode/format and independent scene checks.
Then inventory and qualify other console revisions before acceleration. Keep
720p and the recording build intact. No physical access occurred in this attempt.
