# Copy only complex-clip intersections

RAM0112 starts from pinned RAM0110,excluding diagnostic RAM0111. After unchanged
engine rendering, XwnUpload restarts relevant-only rectangle enumeration for
DC_COMPLEX. It ignores the unusable NT5 start count and consumes counted32-rectangle
batches,including final FALSE batches. Each rectangle is intersected with the
existing screen/destination/clip bounding rectangle before copying RAM pixels.
Simple and NULL clipping retain the previous path. Identity revision is112.

The loop is bounded to256 batches. Invalid counts,inverted rectangles or budget
exhaustion fall back to the original full bounding-box copy. Any earlier partial
copies are idempotent because rendering is complete and these are RAM-to-scanout
copies,not a replayed ROP. TRUE with zero rectangles continues within the bound.
No allocation,cursor,ownership,cache-mode or surface-lifetime changes.

Runtime prerequisite: video-clip-enum2/diagnostic-verification.json and the explicit
NT5 count-oracle correction. The earlier failed original verifiers remain preserved.
Actual shadow.c passes241 retained line tests plus144 enumeration/fallback cases
under ASan/UBSan,with every output pixel,guard word and upload counter checked.
These shims are not a kernel ABI or real GDI test. Matched ordinary control/candidate
and broader GDI/cursor/reset checks remain required before qualification.

The build retains locked source/compiler inputs and20GiB guard. No physical access
or deployment; installed0101/video0093,0088rollback and immutable0.1.0 are preserved.
