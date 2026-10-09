# Text upload discriminator

Ordinary emulator control and candidate both passed the new text pixel, scanout
and copied-byte scope. Candidate 118 intersects the existing clip with conservative
string/opaque bounds; rendering, clip enumeration, ownership, mode, cache policy
and row stores are unchanged. Scalar UC stores and body clocks are OFF in both.
The exact source/build pins are in ../video-text-clip205/build-review.json.

Windows already supplied tight input clips for ordinary text. The earlier204
control exposed that fact and failed its incorrect whole-client byte expectation;
that failed boot is retained in ../video-text-runtime204/REPORT.md. Candidate 204
was prepared but never launched. New 205 metadata captures the actual input clip
before rendering, and new 206 requires independent C and Python byte oracles.

In all five ordinary emulator samples, extended opaque text copied 100,656 bytes
in control and 5,632 in candidate (94.40% reduction). The complex-clip case copied
55,760 versus 5,120 (90.82%). Ordinary text copied the same bytes. The background
operation remains; these percentages apply only to the subsequent text upload,
not total operation time, desktop FPS or window-drag performance.

Each sibling completed 13 actual text cases per sample, totaling 2,129,920 new
reference-DIB/client pixel comparisons and 65 whole RAM/scanout comparisons.
The prior 265 copy checks, 200 window readbacks, 25 timed loops and 50 coherence
checks also passed. Coverage includes actual italic/underline/strikeout metrics,
rotation, negative origin, client viewport edge, opaque and complex clips, Unicode
and an empty opaque call implemented without a TextOut dispatch. It does not claim
physical screen corners or additional video modes. Visible pixel coverage matched
across all 13 cases and both five-sample boots.

Both ordinary boots completed the bounded known-device helper, installation-idle
guards, byte-exact within-measurement SetupAPI bookends, normal restart, one
EventLog 6006 and dashboard return. Complete cold allocation was 324 directories,
6,727 files, 325 directory clusters, zero errors/orphans in each. Five structural
hives, protected hashes, startup, history and typed device policies passed;
30 natural binding deltas were retained. Strict whole-boot qualification remains
FALSE for the sole inherited Ftdisk 49 before measurement. No error was waived.
See emulator-pair-review.json and both immutable emu-*/closure.json.

Both single physical boots also passed the narrow scope and confirmed exactly
the same 100,656→5,632 and 55,760→5,120 byte reductions in every sample. Ordinary
text, actual input clips, string bounds, client geometry and visible pixel coverage
matched across both modes. Each physical boot completed the same 2,129,920 new
text pixel checks, 65 full coherence checks and retained copy/window suite. The
known-device helper handled all four prompts (targets 1/2/3/4), joined successfully
and observed 5,100ms installation idle. SetupAPI measurement bookends remained
byte-exact: 320,680 bytes in control and 323,903 in candidate. Both normally
restarted, logged EventLog 6006 once and returned to dashboard without user input.

Control accepted at 22:34:54 UTC on October 9 and dashboard was observed at
22:39:08; candidate accepted at 22:40:50 and returned at 22:45:23. Collection
restored one-shot startup FIRST, captured every result and restored original
display/SYSTEM before auditing. Both sets of 10 before/after structural hives,
typed policies, protected files, deployed payload/helper hashes and final baseline
readback passed. Each retained exactly the inherited pre-measurement Ftdisk 49;
measurement warnings/errors and application events were absent. Strict whole-boot
qualification is still FALSE. See physical-pair-review.json and both closure.json.

Physical comparison is a separate evidence class. Its launch, result and rollback
records live in control001 and candidate001; no result promotes the temporary
chain. Both use the same captured original0101/video0093 baseline,
exact 202 runner/201 helper/194 guards and rollback procedure. The physical
comparison requires matched pixel coverage, input clips, actual copied bytes,
payload/helper pins, 10 before/after structural hives and baseline readback.
Full storage, crash-dump, new-mode and release qualification are outside this scope;
there was no physical allocation scan in this display comparison. The archived
before/after hives and protected files do not establish full file-content safety.

Host preparation failures and the single resumed prelaunch are documented in
HOST-FAILURES.md. All completed emulator disks were offloaded only after closure,
with standalone QCOW checks, exact hash readback and original paths preserved by
junctions. The immutable0.1.0 archives, original0088 rollback and failed evidence
remain unchanged.
