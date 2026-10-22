#647 CLOSED: narrow the vertical-blank timeout before changing behavior

Read REPORT.md and actual launch/user-observation/collection/audit/closure001.
One watched launch: red/green, black, automatic dashboard return. All28 selected
files identical; no new Windows events. No hook, rollback or owned process.
Ordinary720p remains selected. Do not rerun/recollect647 or any earlier runtime.

Next prepare a NEW bounded diagnostic based on exact633/647 source. Capture
which of the six clear/set waits failed, expected bit, first/last sampled byte,
sample count and observed transitions, using the values already read by edge().
Keep the same register address, predicates, poll bound, delays, write order and
fail/reset path. No extra reads of status registers merely assumed side-effect
free. Record that added RAM bookkeeping/code layout still perturb timing.
Distinguish setup-before-writes from final context. Do not clear pending bits,
borrow firmware state, increase timeout or bypass validation as a speculative fix.

First add host cases for stuck-low/stuck-high at each of six waits, delayed
transitions and boundary success/failure, checking unchanged writes and bounded
failure. Existing633 tests only exercise one constant-low edge failure and a
read-by-read toggling success model; neither establishes physical timing.
Independently review the exact compiled candidate and how its bounded indication
will distinguish all six phases without ambiguous ordinary boot colors. If a
reliable state receipt cannot be obtained, retain that limitation explicitly.
Use a new unique kit/build/remote path with source/binary pins and existing leases.
Only then stage/readback and obtain a watched observation for the new question.
No additional launch is queued by647's result.

A status-bit timeout is not yet proof of absent physical scanout or a bad adapter.
The current result does not identify645's cause or establish a 480p reliability
fix. Composite remains a separate480i path; keep the current adapter for this work.
No live switching, other-revision or acceleration promotion. Automation paused.
