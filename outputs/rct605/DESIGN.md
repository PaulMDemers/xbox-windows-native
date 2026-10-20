# PC605: latched phase request after recorded calls drain

Preserve604's exact bounded reader,601 graphics core and call pairing. Add one
manual-reset request/ack event pair owned by the new original subject/observer.
The observer polls only while its debuggee is stopped at an owned breakpoint.
It defers the requested phase transition while any recorded frame is pending,
commits once at an empty boundary, resets only StretchDIBits' sample count, and
acknowledges the switch. Duplicate requests cannot reset sampling again.

Each StretchDIBits phase retains a32-call cap. After a cap, that entry remains
armed solely to detect a later phase request and count skipped entries; it does
not invent paired returns for skipped calls. Other API caps remain unchanged.
This adds breakpoint overhead, so the run is layout/coverage qualification,
never an uninstrumented performance baseline. Preserve the60-second/10000-event
control bounds; absence of phase evidence fails the independent review.

The new original control makes35 exact pixel-checked StretchDIBits calls after
the existing core's one call, exhausting startup sampling with four skips.
A traced exported function then signals the request while its recorded frame
is pending. The next StretchDIBits entry commits after that frame returns. The
subject checks the ack, repeats the request, and completes36 second-phase copies.
Expected observation: one deferred request, one transition,32 samples/four skips
per phase and unchanged pristine/traced subject results. Invalid transitions
and mutated traces must be rejected independently. Fresh404 fixture only, normal
restart and cold checks; no game, Xbox or functional driver modification.
