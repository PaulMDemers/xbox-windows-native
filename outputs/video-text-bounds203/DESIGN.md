# Conservative text uploads, 0117

The 0116 RAM-primary driver uploads the entire clip bound after EngTextOut. This
candidate uploads the union of the supplied string bounds and opaque rectangle,
intersected by the existing screen and clip enumeration. Rendering still goes to
the RAM bitmap through the same EngTextOut call. Ownership, cache attributes,
video mode, and row-store policy are unchanged.

Microsoft documents STROBJ.rclBkGround as the string bounding rectangle. Snapshot
that rectangle and cGlyphs before EngTextOut consumes any enumeration. Do not walk
glyphs or depend on pgp being populated. See [STROBJ](https://learn.microsoft.com/en-us/windows/win32/api/winddi/ns-winddi-strobj).

The opaque rectangle can extend beyond the string. Its union must therefore be
uploaded as well. GDI supplies no extra rectangles under the documented contract;
an unexpected non-null extra pointer conservatively retains the old full-clip
upload without dereferencing it. Missing string metadata, unordered or empty
required rectangles, and Eng failure also retain that fallback. Clip and screen
intersection happen only through the old bounded upload code. See
[DrvTextOut](https://learn.microsoft.com/en-us/windows/win32/api/winddi/nf-winddi-drvtextout).

An empty string without an opaque rectangle has no documented drawing. The
bounded mode may skip that upload; an empty opaque rectangle falls back. Coordinates
use signed 32-bit min/max comparisons with no subtraction in the bounds helper.
Only already clamped upload rectangles contribute actual copied bytes.

Both matched builds disable phase clocks and scalar UC stores. The sole build
definition difference is XWN_TEXT_BOUNDS. Both carry identical saturating actual
text-copy counters. The new 128-byte escape 0x58574436, version117, reports total
and last-call copied bytes and boxes, glyph count, reason, bounds, mode and overflow.
Per-call accounting avoids subtracting device-global row counters while background
applications draw. It is published after copying under the existing accounting
lock; that lock never spans rendering or copying.

Host tests exercise geometry, fallback, signed extremes, clipping holes, disjoint
opaque regions, and saturation. They do not prove real glyph coverage. Fresh NT5
pixel readback and RAM/scanout comparison, paired copied-byte accounting, complete
cold allocation/hive/protected-file audits and separate physical validation remain
required. Prior 202 physical results do not qualify this candidate.
