# Finish the259 runtime bridge before any guest launch

Read DESIGN and actual build/review records. Probe build001 is compiled and
independently checked; admission002 is sanitizer-tested. admission001's original
inputs/results are preserved in prior-admission001; review added bounded total
counts and pointer/boolean checks before walking caller-provided arrays.

The renderer stage implementation has NO QOM/PFIFO caller. Inspect
renderer-build001.json and final-review.json before proceeding. Build44179 is
CLOSED; all borrowed sources restored. Never treat the
presence of its executable as a ready test harness. There is no prepared guest,
no emulator launch, no callback coverage and no pixel-preservation result259.

Implement one new opt-in bounded sequenced bridge around the actual CPU-exclusive
callback inventory and renderer worker. The existing247/246 actors are one-shot;
do not reset them or mistake an empty CPU work queue for completed work. Account
for all seven reference families and active vertex/report/pending state. Refuse
unknown ownership; don't weaken admission to make the experiment run.

Use the five actual X259Checkpoint stops and immutable258 held driver. Verify
actual process/base/resident instructions, loaded driver Arena/owner/generation,
and all four physical pages before the first GL reference. Parse real event
sequences, not success flags. Real dirty CPU read and blocked CPU store must run
with the worker unparked. Preserve/restore all GL bindings and prove callback
insertion/removal/free. Host debugger reads cannot consume the intended guest
callback. The new probe requires the full three-pattern sequence.

Then prepare a NEW unique source child from pre-execution258, replace only the
probe/startup as intended and correct inherited fixture descriptions explicitly.
Freeze the complete sources/binaries/fixture; launch exactly once after review.
On failure preserve evidence and close owned processes. Full cold audit and
unchanged strict gates are mandatory. Keep physical demo/recovery untouched.
