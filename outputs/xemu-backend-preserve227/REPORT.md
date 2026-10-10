#227 closed diagnostic: preservation refused

Build005 implemented actual opt-in OpenGL fence/download/VRAM comparison without
discarding cached surfaces. Its executable SHA256 is
097a0eeae0a33ae90e7757f7a92f4b716ccfa14565f14eb541973ae1bb00b2bb.
The single trace001 launch was accepted19:16:01 UTC October10; dashboard returned
19:17:32; controller/cold audit closed19:17:53. No relaunch or recollection.

The actual pinned Cromwell exit stopped once; request returned state4 REFUSED,
surfaces0/dirty0/downloaded0/bytes0/error0. This is failed backend coverage.
227 did not record the exact refusing predicate. No cause is inferred from zero
counts. Reserved20KiB instance memory and84KiB CPU tail were unchanged; all
breakpoints removed, guest resumed, no native ownership granted or references
retired. No GPU surface was downloaded in this run.

Normal CPU workload completed65 leases/releases,3194880 checked bytes and four
joined workers, one normal shutdown and dashboard return. Full cold allocation
is320 directories/6724 files/321 directory clusters, no errors or orphans.
Five structural hives, protected hashes, startup/history/device policy passed.
Strict whole-boot remainsFALSE for inherited Ftdisk49/error3. Backend and ordinary
qualification areFALSE; this intervention is a debugger diagnostic, not physical
evidence or all-file-content qualification.

All owned sessions closed: preparation75375, runtime47563, builds68533/73744/
22965. Controller114060, runner96376, tracer112680, observer111884 closed0.
Build001/002 failures and successful but never-launched003/004 are retained.
Closed build005 was subsequently hash-verified offloaded to E through its
original-path junction; frozen byte pins remain valid. No disk chain moved.

Next228 adds a specific refusal reason, preserving every existing predicate.
Post-run source review also found a check/store race in terminal publication:
a reporter timeout could be overwritten by a late worker. This was not observed
in trace001; the frozen DESIGN's terminal-race claim is not qualified. NEW228
build002 uses a CAS publication claim and tests that actual helper before launch.
Actual dirty-readback coverage, reference retirement, native context/allocator
ownership and cache-alias safety are still prerequisites for accelerated copies.
Physical0101/video0093,0088 rollback and immutable0.1.0 are untouched.
