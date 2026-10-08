# Next optimization target

All current cases are CLOSED. Use the measured LineTo over-upload as the first
narrow optimization target; keep complex clip enumeration as a separate change.
There is no reason to alter overlapping copies or the measured stretched-copy
path, which already upload only their destination in this baseline.

Microsoft's DrvLineTo contract supplies prclBounds as the rectangle bounding the
unclipped cosmetic line:
https://learn.microsoft.com/en-us/windows/win32/api/winddi/nf-winddi-drvlineto

Before relying on NT5's actual bounds, use a NEW bounded, resident-pinned diagnostic
to record real LineTo arguments, prclBounds, clip bounds and surface identity for
the horizontal baseline and a meaningful set of diagonal/reversed/vertical,
offscreen and clipped lines. Do not infer runtime argument contents from the API
documentation. Use independent pixel references and full breakpoint teardown;
debugger evidence remains separate from ordinary qualification.

Then implement the narrow upload-bounds change with conservative fallback if
required by observed contracts. Preserve EngLineTo behavior, return value,
ownership checks, surface lifetime, framebuffer caching and cursor contract.
Host-test actual changed upload code for screen/clip intersections, endpoints,
empty regions and arithmetic bounds; do not merely mirror helper expressions.
Fresh matched unchanged-control/candidate ordinary runs must retain all pixels,
cold integrity and strict events, and demonstrate actual byte reduction. Re-run
the broader GDI/cursor/mode-reset regression before considering hardware.

Complex clips will separately require safe CLIPOBJ enumeration, bounded batches,
correct handling of enumeration exhaustion and no omitted dirty pixels. Full
screen uploads can be safe while inefficient; a performance fix must not trade
correctness for lower counters. Do not suppress draw/event gates or call driver
hooks directly to fabricate coverage. Actual window dragging, hardware bandwidth,
additional video modes and surface destruction/recreation remain unqualified.
