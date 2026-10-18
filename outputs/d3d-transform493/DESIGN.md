# Rung09a: actual XYZ transforms, independent rational image oracle

Six unlit D3D7 RGB software cases render to a64x64 RGB32 system-memory target.
D3DFVF_XYZ|DIFFUSE has16-byte vertices, not pretransformed XYZRHW. Each case
sets and reads back WORLD, VIEW, PROJECTION and viewport; actual pixels are a
separate mandatory predicate. Depth, lighting, fog, alpha, dither, specular and
antialias are disabled; clipping and vertex color are explicitly enabled and
all state values are read back. No primary surface, display-mode change or GPU.

The model triangle is(-.5,.5,.5),(.5,.5,.5),(-.5,-.5,.5), color0x40c080.
Background0x102030. Before each case reset viewport tofull64x64 and clear the
whole target, then install the case viewport. Six concatenated clear/draw
snapshots each contain98304bytes (196608bytes/case/process). Ignore unused high
RGB byte/pitch padding. Require exact format, pitch, ownership and bounded IO.

Cases independently derived by row-vector multiplication W then V then P:
- Identity: screen(16,16),(48,16),(16,48).
- World translation x+.25: (24,16),(56,16),(24,48).
- View translation y-.25: (16,24),(48,24),(16,56).
- World quarter-turn(-y,x), then viewx+.25: (24,48),(24,16),(56,48).
- Perspective: model xy doubled, depths1.25/1.5/1.5; Pzz2,Pzw1,Pwz-2,Pww0,
  near1/far2. Screen(32/5,32/5),(160/3,32/3),(32/3,160/3).
- Viewport(16,16,40,40,0,1): (26,26),(46,26),(26,46).

Python Fraction arithmetic is independent from runtime D3D and C matrix setup.
Literal expected coordinates test matrix order and perspective divide. A fixed
2pixel L-infinity edge band permits onlyFG/BG; safeinterior mustFG and safeoutside
mustBG. Require>=20interior and>=2000exterior pixels percase. Unknown/missing/
failed metadata, altered matrices/readback/vertices, incorrect clipbounds and
invalid geometry refuse. Actual raster clipping, interpolation, lighting,
full-scene behavior and performance remain unqualified.

Oracle001 FAILED before build: unchanged identity synthetic image could satisfy
perspective/viewport cases within broad edge band. Preserved privateoracle001.
Oracle002 enlarged perspective but32x24 viewport failed existing minimuminterior
coverage gate; preserved privateoracle002. Oracle003 uses stronger perspective
and40x40 displacedviewport, same tolerance/minimum gates; all4testgroups pass.
No guest was used to choose expected pixels. Never rerun consumed tests/outputs.

Reference: Microsoft Direct3D transformation pipeline (legacy SetTransform
D3DTRANSFORMSTATE API):
https://learn.microsoft.com/en-us/windows/win32/dxtecharts/the-direct3d-transformation-pipeline
Pinned RosBE NT5 headers supply actualABI; no modern D3D interface substitution.

First a fresh owned404 PCchild with independent coldread and no networking.
Run default/HEL in bounded processes; normalrestart, exactmoduleprovenance,
protectedOSfiles andfivehives. Only qualifiedPC permits NEW matchedXbox attempt.
Oldclosed491/492 fixtures remain untouched; no physical launch in493.
