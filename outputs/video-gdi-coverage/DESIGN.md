# Real GDI coverage against a separate DIB

The unchanged RAM0109 DLL is the candidate. No driver, cache, mode, device policy,
service, storage or network change. A new immutable child and output directory
contain a new probe and both old/new pinned display payloads; only candidate001
is authorized by this preparation script. No physical access.

The probe draws 26 named cases through normal Win32 GDI. It starts both targets
with the same deterministic background. It draws the reference into a separate
top-down 32-bit DIB before drawing the primary; checks per-hook counter deltas
around the reference; requires those deltas to be zero; and then checks the
primary readback against that reference. Source DIB hashes and the completed
reference hash must remain unchanged during primary drawing.

Cases cover solid/pattern ROPs, source inversion, monochrome masks, stretch and
mirror, masked/unmasked parallelograms, line/polyline, stroke/fill/combined paths,
PaintRgn, opaque/transparent text, rectangular/triangular gradient, constant and
premultiplied per-pixel alpha, transparency,24-to-32-bit translation, complex/
empty/offscreen clips and a patterned rounded rectangle. Each non-empty case
must change at least one reference pixel; the empty clip must change none.

Each case preserves a393216-byte reference file, per-hook deltas and exact API/
pixel/coherence outcomes. Continue to record all cases even after a pixel/API
failure, then request a normal restart; qualification must still fail. A harness
failure stops the probe with its partial evidence. No dialog cancellation.

Ordinary GDI readback and the driver's own RAM/framebuffer check are not an
independent scanout oracle. Only a NEW separate diagnostic run will read raw
framebuffer bytes and compare them with the independently rendered reference,
after pinning loaded code, geometry and reference memory. Its saved reference
must match cold disk readback. Debugger results stay separate from ordinary.

Per-case callback counters describe observed routing, not a requirement to call
every advertised hook. Any unobserved hook remains unqualified. The test never
calls a rendering hook directly. Cursor is parked outside the window; this is
not cursor-exclusion or mode/crash qualification and makes no speed claim.

API references: [AlphaBlend](https://learn.microsoft.com/en-us/windows/win32/api/wingdi/nf-wingdi-alphablend),
[premultiplied alpha](https://github.com/MicrosoftDocs/win32/blob/docs/desktop-src/gdi/alpha-blending-a-bitmap.md),
[MaskBlt](https://learn.microsoft.com/en-us/windows/win32/api/wingdi/nf-wingdi-maskblt),
[PlgBlt](https://learn.microsoft.com/en-us/windows/win32/api/wingdi/nf-wingdi-plgblt).
Owned NT5 exports and the fixture's actual imported API DLL hashes are checked.

The initial probe compiler indentation failure is preserved under
probe-build-failure001; no guest launch used that source.
