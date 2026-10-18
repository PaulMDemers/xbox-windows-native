# Windowed D3D presentation491

New original sample: D3D7 RGB software device renders a flat triangle into an
owned128x112 system-memory target in the primary's native RGB565/555/32 format.
It neither changes mode nor replaces a driver/runtime. Default and explicit HEL
are separate process cases. Non-supported formats/capabilities refuse.

Four stages render red/cyan, green/magenta, white/blue, yellow/black respectively.
Triangle vertices are (8,8),(120,8),(8,104), z=.5,rhw=1. Depth, lighting, fog,
alpha test/blend, dither, antialias and specular are explicitly disabled. Texture
stage0 selects diffuse, stage1 is disabled. Draw and end-scene must succeed.

Independent source oracle: x>=12,y>=12,6x+7y<=724 must be foreground; x<=4,y<=4,
or6x+7y>=828 must be background. The remaining narrow boundary may be either of
those two colors, never arbitrary RGB. Exact rasterization edge placement is not
qualified. The allowance is declared before any runtime capture, not fitted to
screenshots. The full source is captured again after presentation and must be
byte-identical. Pitch padding is not an allocation-guard claim.

The existing rung03 geometry supplies an owned256x192 GDI panel, a96x80 target
at(16,16), blue guards and a magenta sibling cover at(48,40)..(88,72). Stages are
visible, covered, moved while covered, uncovered. Actual clip rectangles must
form the exact target-minus-cover union. An oversized primary blit exercises the
clipper. GDI readback must equal independently qualified source pixels inside
the visible target and exact blue/magenta guards elsewhere. GDI paint handlers
never draw the D3D image. No claim of physical scanout, GPU or performance.

Capture/API/module/state/vertex/cleanup records and the external process exit
are required. DLL/driver calls can block: the owned NT5 controller has90seconds
per sample and a600second outer VM watchdog; sample.cmd alone is not a watchdog.
New fresh output IDs, source/binary/compiler pins, admission-checked immutable
floppy and child of the approved404 reusable seed. No closed runtime parenting.
Windows PC control and complete cold audit precede any separate Xbox package.

References: existing project present.c and triangle.c provide reviewed API paths.
[Microsoft Blt](https://learn.microsoft.com/en-us/windows/win32/api/ddraw/nf-ddraw-idirectdrawsurface7-blt)
documents the destination/source and clip operation. Newer
[D3D9 rasterization guidance](https://learn.microsoft.com/en-us/windows/win32/direct3d9/rasterization-rules)
is background only, not a guarantee of the pinned D3D7 rasterizer's exact edges.
