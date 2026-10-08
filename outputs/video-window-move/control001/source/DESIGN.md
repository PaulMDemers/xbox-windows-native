# Ordinary matched native window movement

Shared probe136 and immutable RAM0110 fixture, control0110 vs candidate0112.
No new display binary, debugger, physical access, settings or policy changes.
A topmost parent contains a real movable128x80 child and fixed96x144 occluder.
Six positions repeated3times cross the occluder and parent clipping boundaries.
Native SetWindowPos movement and separate forced RedrawWindow are measured with
counter snapshots; images checked after BOTH operations. Paint handlers use a
known pattern plus real TextOut and native child/sibling visibility clipping.
Expected images are CPU-composited from the independently authored background,
fixed foreground and pinned guest font source. Cold oracle independently composes
positions; glyph bytes are guest-generated and are not an independent font test.
Source bitmap nontext pixels and allowed glyph colors/bounds are checked cold.
The same source bytes must match across both runs. Capture18 exact reference files.
Cursor is placed at18 authored positions during moves, then hidden outside measured
intervals for readback. This does not independently validate raw cursor pixels.

No forced invalidation before move readback: missing exposure repaint must fail.
Forced redraw has its own counter and time interval. Record paint counts/API status,
actual child bounds, before/after quiet counters and monotonic totals. Repeated
counts are observed, not assumed identical when native window movement coalesces.
Use GetTickCount only for coarse ordinary emulator milliseconds; shared functional
lease does not establish timing isolation, so no physical FPS/speedup claim.
Require same existing normal restart, complete cold allocation, five hives,
protected hashes, pagefile/configuration and strict event gates. Failures preserved.
