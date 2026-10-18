# Loaded entry512: jump proven, full observer refused

One new emulator launch10:03:59UTC reached11100 then94aff. Exact five-byte jump,
eight GPRs includingESP, EFLAGS and CR0/3/4 matched at both stops. Three actual
kernel calls (amber/manual/delay) returned0. The observer stopped at NtCreateFile
entry BEFORE execution: its reused helper hard-coded old XWNBoot504a, while the
actual pinned510 path is XWNBoot510a. This is a second harness integration failure.
The new trampoline-only host tests did not exercise the reused file helper with
the new candidate. A full exact-candidate transaction test is now required.

No file creation/receipt, final flush/close, green/automatic LED restoration,
firmware return or Windows execution is qualified. All breakpoints were removed,
physical mode restored; host exited0 without fallback. Sessions70071/32980/55429
CLOSED.397 private files,261 frozen sources,19 external inputs rehashed. Cold
full10GB map:55 changed bytes, strictFALSE; writers not fully attributed. FATX
276dirs6553files255dirclusters,zeroerrors/orphans. Five hives/three baseline
binaries,source/EEPROM unchanged. No physical access or queued launch.

The failure-review script inherits511's stale opening docstring about an
unexecuted jump; its explicit assertions/result correctly record jump_executed=true.
Original executed source/results remain frozen. Never rerun/recollect/parent512.
