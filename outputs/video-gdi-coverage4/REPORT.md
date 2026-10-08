# RAM0109 real GDI coverage: ordinary strict PASS

Unchanged RAM0109 passed26 actual Win32 GDI cases:2,555,904 RGB pixels exactly
match independent DIB references. All API outcomes, source/reference immutability,
zero reference callback deltas,26 driver coherence checks and26 cold393216-byte
reference files pass. Normal shutdown1/dashboard, zero warning/error/application
events, full allocation325dirs6785files326directoryclusters without errors/orphans,
5 structural hives and protected/payload/startup hashes pass. Configuration,
96MiB/1536-cluster pagefile and permanent shared UC mapping are unchanged.

Observed10/14 callbacks: BitBlt,CopyBits,TextOut,StrokePath,LineTo,StretchBltROP,
PlgBlt,AlphaBlend,GradientFill,TransparentBlt. FillPath,StrokeAndFillPath,Paint,
StretchBlt remain unobserved; Win32 calls with related names are not proof those
callbacks were reached. No hook was called directly to manufacture coverage.

Cases include masks, noncopy ROPs, mirror/stretch, parallelograms, paths/lines,
text, gradients, alpha/transparency,24-bit translation and complex/empty/offscreen
clips. Full-desktop own-window coverage removes the reference-count interference
observed with the smaller window. This does not retrospectively attribute or waive
those eight earlier global CopyBits increments. Gates remain unchanged.

Probe121 SHA256276da9973597131f11fc9de031c5660b91df6cc8053e0ba577a3110d078bf3ac.
Display ed901376d61e70a125fce834e20b366e49a1d632879debbcfedd621c18b6a440,
unchanged source tree1f5aa1cee2bf9b4ca03e5581a8536db9c11db3d2. Real-log tests
reject13 deliberate pixel/API/hash/coherence/counter/completion corruptions.

Separate video-gdi-scanout5 uses exactly the same source/probe/display bytes to
check raw physical framebuffer against runtime and cold DIB references. Its
status must be read from its own verification.json; ordinary success alone does
not establish physical scanout, hardware performance or full display lifecycle.

Earlier evidence retained: first ordinary incomplete; three observer failures;
fourth observer confirmed actual harness exit10, then assisted restart recovered
its log with a retained kbdhid warning; probe119 isolated visibility guard failure;
probe120 zero RGB errors but eight reference counter failures. No failed case
was relaunched or reclassified as passed. All fixtures and physical baseline
remain separate. No physical FTP/deployment/testing or display-driver change.

## Independent emulated framebuffer result

Separate scanout5 strict diagnostic PASS:26 raw physical-memory framebuffer
captures,2,555,904 RGB pixels and zero mismatches. Runtime DIB references exactly
match all26 cold reference SHA256 values.277resident pins include all11668 bytes
of relocated display.text. Full breakpoint teardown/resume; normal shutdown1,
strict cold workload/integrity/events pass.73foreign process API hits were safely
recorded/stepped;2 current-entry page faults were allowed to resolve naturally.
The display header remains GDB-unreadable and is explicitly recorded as such;
loader identity, exact resident text and cold PE hash provide its required pin.
This is debugger evidence (ordinary_qualified=false), not physical-console proof.

## Actual ordinary case coverage

| Case | Changed reference pixels | Observed primary callbacks |
| --- | ---: | --- |
| solid_patcopy | 55100 | BitBlt:1 |
| hatch_patinvert | 55100 | BitBlt:1 |
| srcinvert | 8192 | BitBlt:1 |
| maskblt | 12288 | BitBlt:1 |
| stretch | 65100 | StretchBltROP:1 |
| mirrored_stretch | 65100 | StretchBltROP:1 |
| plgblt | 57600 | PlgBlt:1 |
| masked_plgblt | 28800 | PlgBlt:1 |
| line | 311 | LineTo:1 |
| dashed_polyline | 1139 | StrokePath:2 |
| stroke_bezier_path | 1305 | BitBlt:1 |
| fill_polygon_path | 30632 | BitBlt:1 |
| stroke_fill_ellipse_path | 45167 | BitBlt:1, StrokePath:1 |
| paint_region | 52033 | BitBlt:1 |
| opaque_text | 21700 | BitBlt:1, TextOut:1 |
| transparent_text | 655 | TextOut:1 |
| gradient_rectangle | 62000 | GradientFill:1 |
| gradient_triangle | 29770 | GradientFill:1 |
| constant_alpha | 60000 | AlphaBlend:1 |
| pixel_alpha | 59998 | AlphaBlend:1 |
| transparent_blt | 39976 | TransparentBlt:1 |
| 24bit_translation | 12288 | CopyBits:1 |
| complex_clip | 24389 | StretchBltROP:1 |
| empty_clip | 0 | none (empty clip) |
| offscreen_clip | 6299 | CopyBits:1 |
| hatch_roundrect | 65496 | BitBlt:1, StrokePath:1 |
