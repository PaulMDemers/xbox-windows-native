# Candidate design after runtime enumeration verification

Base any optimization on RAM0110, not on this diagnostic helper. Keep the simple
rectangle and NULL-clip paths intact. For a DC_COMPLEX destination clip, restart
relevant rectangle enumeration with CT_RECTANGLES and CD_ANY after rendering.
Intersect each returned rectangle with the already bounded upload area and screen.
Copy only those intersections from the rendered RAM primary to scanout. This is a
copy after the engine's ROP, so repeated or fallback copies are idempotent.

Use a small stack batch and an explicit batch budget. Process counted rectangles
even on the final FALSE result. TRUE with zero rectangles advances the bounded
loop; it must not silently terminate traversal. On an impossible count, invalid
rectangle or exhausted budget, use the original bounding-box upload. A partial
enumeration followed by this fallback preserves the prior copy behavior. Never
read beyond the counted buffer or perform unchecked signed coordinate arithmetic.

Tests must compile the actual uploader with an enumeration shim to cover ordinary,
multi-batch,zero-progress,final-batch,offscreen,invalid-count and bounded-fallback
paths, checking every destination pixel and guard word. Retain line-bound tests.
Then use identical ordinary control/candidate probes for exact pixels and counters,
followed by broader GDI/cursor/reset checks and unchanged strict cold gates. Report
bytes separately from FPS; do not claim physical qualification.

This document is a proposal, not implemented optimization or runtime proof. Read
the completed video-clip-enum2 record before proceeding. Failed enum coverage does
not justify replacing it with the API documentation alone.
