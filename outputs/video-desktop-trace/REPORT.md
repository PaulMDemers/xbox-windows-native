# Desktop callback diagnostic: incomplete, strict failure preserved

The unchanged probe completed its first create/switch/restore/close sequence,
then failed the immediate post-close name-absence assertion. CloseDesktop
returned1. ABSENT_AFTER was0; this encoding does not distinguish an existing
handle from NULL with last-error0. No root cause is assigned. A paired API-return
diagnostic is specified in NEXT.md; no driver patch or gate relaxation was made.

Five actual helper markers and six resident helper pins were captured. The one
ownership slot and its PDEV/surface/shadow fields stayed identical across those
five markers. None of the nine watched driver lifecycle functions fired during
this first interval. No later-cycle coverage, full driver residency, physical
scanout or surface-destruction/recreation qualification follows from this.

The helper reported failure, cleaned its resources, and restarted normally.
Supervisor28819 then signalled runner60028 to close the owned emulator while
tracer53952 still awaited the remaining markers. The GDB connection was reset,
and teardown could not remove its one remaining helper breakpoint before process
exit. All owned processes are closed, but breakpoint teardown is explicitly NOT
passed. A new supervisor must coordinate observer closure, and the observer must
handle early ExitProcess rather than waiting only for successful final markers.

Cold evidence: the two generated49152-byte images exactly match the independent
host oracle; seven expected images are absent. The allocation audit has326
directories,6764 files,327 directory clusters, zero errors and zero orphans.
Five hives, protected files, helper/startup and96MiB pagefile map pass. There is
one normal shutdown and no warning/error/application event delta. These checks
preserve useful evidence but do not override failed workload/trace qualification.
failure-verification.json rejects four mutations including invented successful
breakpoint teardown. The all-fifteen-marker verifier was NOT used to claim PASS.

Unique candidate001 accepted2026-10-08T02:41:08UTC. Preparation74084, runner60028,
tracer53952, supervisor28819 and audit94560 are CLOSED; never relaunch/recollect.
An initial preflight rejected normalized host-oracle line endings before launch;
exact original bytes were restored and the rejection is preserved. No extra guest
launch occurred. Original ordinary video-desktop-lifecycle remains strict PASS.
Both use identical probe126/display0109 and unchanged registry/device policy.
Physical0101/video0093,0088 rollback, immutable0.1.0 and prior128GiB recovery remain
unchanged and separate.
