# Actual input-clip telemetry, 118

The204 control proved the whole-client byte oracle was wrong:5632 copied bytes
matched its88x16 string bounds, instead of the249944 client bytes predicted by the
probe. Preserve that failed experiment. The new205 driver snapshots the actual
CLIPOBJ.rclBounds and iDComplexity before EngTextOut, then publishes them atomically
with the same last-call copied-byte record. No glyph or clip enumeration is added.
The same rendering, upload, owner selection, cache attributes and modes remain.

Read-only escape0x58574437 returns160 bytes, version118. It preserves117 fields
apart from version/size, adds signed input clip coordinates at32..35, complexity36,
clip-present37, and reserved zeros38..39. Both old117 and new118 escapes remain.
The accounting lock covers the entire snapshot or publication, never rendering or
copying. These are coordinates, not kernel pointers. Input clipping and published
per-call accounting must agree in actual runtime; that is not assumed from source.

Both paired205 builds still differ only in XWN_TEXT_BOUNDS, with clocks and scalar
stores OFF. The immutable117 host bounds/overflow tests apply to the identical
helper bytes. No new drawing optimization was introduced. The205 source review,
compiled artifacts and NT5 import checks are separate from fresh206 runtime.

206 independently counts pixel intersections from captured input clip, client
origin/size and known application clip, then applies string/opaque union only in
ON mode. Both real glyph pixels and whole RAM/scanout coherence remain required.
Matched copied bytes would reject the usefulness of this optimization rather than
justify deploying it. No physical or performance qualification is established here.
