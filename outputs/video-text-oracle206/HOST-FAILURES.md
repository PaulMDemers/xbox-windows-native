# Preserved host preparation failures

The first invocation of compare.py used Windows Python. Its shared cold-audit
imports require the owned Linux fatx_stage_boot module, so import failed before
the comparator created an output record or accessed a console. The same exact
comparator subsequently ran under owned WSL Python and produced the pinned
emulator-pair-review.json. This host failure is not a guest result.

Physical control staging then encountered a missing local artifacts/gdi-probe.exe
alias. The compiled helper is artifacts/replay.exe; the frozen controller still
references the older local name. At failure, only the exact runner and captured
rollback archive had been staged. No driver, SYSTEM or startup was written and
SITE EXEC was not sent. See control001/prelaunch-resume.json.

resume-prelaunch.py retained the original failed record hash and verified the
unchanged installed baseline, original startup, known staged files and absent
remaining helpers/results. It created a byte-identical local alias of the pinned
replay.exe and resumed only the unfinished staging. Drivers and SYSTEM preceded
one-shot startup, and launch intent was persisted before the single SITE EXEC.
The frozen controller and ready record were not edited. A later candidate must
verify this alias against the pinned replay helper before staging.

No launch or collection may be repeated because of either host failure. Actual
launch, return, collection, restore and closure records determine the guest state.
