# Windows field-pattern and mapped scanout comparison

Two physical runs completed with the same user-mode probe and unchanged Windows
drivers: control001 at 1280x720 and interlace001 at 1920x1080. Each checked
4,194,304 independently expected pattern pixels across eight cold captures,
with eight zero-mismatch comparisons between the installed driver's RAM shadow
and its actual volatile mapped scanout. Both ran the real USER window-movement
phase. This narrows investigation beyond the shadow-to-framebuffer copy at the
sampled instants; it does not validate the encoder output or prove every moving
frame was correct.

The user reported for 720p: "yes it did everything you outlined. rebooted".
For 1080i: "every other column is a solid color, and they fish when it moves,
pictures taken. rebooting now". Preserve that wording; photographs have not yet
been supplied for this test. Several solid vertical bands are intentionally the
binary row labels, so they alone are not corruption evidence. Earlier separate
observations reported clean text and dragging at 720p.

Each run has one new EventLog 6006 shutdown record and sole new warning/error
Ftdisk49 in the validated record scan. Strict event qualification remains false.
The scan may include inactive ring records and is not complete event coverage.
There was no full allocation audit or new clean-install qualification.

The temporary xwn428 startup hook was removed after each normal user restart,
with its exact bytes retained under that run's console evidence directory.
Original xwnsetup.cmd and protected drivers were unchanged. The qualified display
selector restored the exact 720p launcher, SHA256
6240a801d97c4894e56d516a934059da056446fb77cf895b5364bdd6cd24be9a.
Only the owned E paths were changed; Xbox C was not accessed. Both SITE EXEC
requests were accepted and reached Windows. No repeat launch is needed.

Evidence: build001/review001 pin the NT5 compiler, executable imports and sources;
scanout-source001 proves the public scanout-check implementation matches the
actual 303 source tree and installed driver hash. Host001 runs the actual pattern
helper under ASan/UBSan with an independent byte oracle: 2,105,360 checks, including
2,097,152 pixels. Its 8,192 local mutation checks include 32 full-parser mutations;
they are not 8,192 full-parser tests. analysis001 independently validates complete
log ordering, mode/identity/scanout fields, movement and durations, rejecting
128 actual-log mutations per run. Both collection manifests and all private
captures were rehashed. No emulator test was run for this user-mode probe.

Private captures and receipts are under E:/xwn428. Before building, deduplicate001
verified two identical 1,187,374,397-byte archived QCOW compression files, then
replaced the duplicate with a verified NTFS hardlink. Both original paths remain;
no backing disk moved. The original archive/source-removal receipts were checked.
The 20 GiB build reserve was retained.

All 428 sessions are closed. These are observation results, not a 1080i fix.
