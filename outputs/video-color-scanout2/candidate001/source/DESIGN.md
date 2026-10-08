# Observe the first color observer's sequencing failure

Fresh child, same exact probe123/driver/settings and unchanged104-frame oracle.
The first diagnostic captured75cursor phases+24restored frames, all exact,
then rejected a cursor-marker sequence assertion before recording its raw args.
Guest continued all26cases and normal shutdown with clean cold audit. Incomplete
diagnostic remains FAILED; it is not evidence that the guest skipped its marker.

Discriminator: preserve every stop's raw registers/process/thread/armedbreakpoints
and expectedcounts, each single-step's before/after registers/process/thread, and
raw marker args before assertions. Bound640stops/512steps/600seconds; keep all
strict sequence/pixel/gate requirements and teardown. This observes whether a
step/context transition contributes to a missed/duplicate breakpoint; it does
not assert that cause or silently accept unexpected marker ordering.
Same exported markers and no guest code/driver patch, register forcing or UI.
