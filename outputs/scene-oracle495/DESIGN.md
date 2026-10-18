# Proposed combined scene: independent host oracle

This kit defines expected contents before implementing a new Windows sample.
There is no C sample, renderer build, guest preparation, launch or physical
access in495. Existing working720p/launcher/startup remain untouched.

Two owned8x8 RGB32 textures contain four4x4 quadrants each. Near palette:
206040,40c080,608020,80a060; far palette:802060,c04080,a06020,e08040.
Source uploads/readbacks must match all512bytes, before and after, including
explicit alphaFF for enumeratedARGB or zero for RGB. Actual format selection
and metadata validation remain work for the new runtime adapter.

Target64x64 RGB32, background102030. Model near vertices:
(-7/8,3/4,5/4),(5/8,3/4,5/4),(-7/8,-3/4,5/4).
Far:(-1/4,3/4,3/2),(5/4,3/4,3/2),(-1/4,-3/4,3/2).
Both UV:(0,0),(1,0),(0,1); submit actual XYZ|TEX1,20byte vertices.
WORLD tx=1/8, VIEW ty=-1/8, PROJECTION zz=2,zw=1,wz=-2,ww=0 with
xx=yy=1, other entrieszero. Viewport0,0,64,64,minZ0,maxZ1. Near/far
projectedZ are2/5 and2/3. World/view/projection row-vector order is explicit.

Five frames: far-near and near-far with LESS depth/write enabled, near-far
with depth disabled, clear depthzero with LESS enabled, then world tx=-1/8
with normal depth. The frozen fifth label camera_move describes apparent scene
motion; its actual change is WORLD translation, not a camera/view update.
Each frame resets target and depth and captures clear/draw independently.
Future actual sample must record all draws/state/matrices/readbacks and errors.

Expected screen positions and barycentric UV use Fraction arithmetic. Depth/W
are constant inside each triangle: this control does not qualify varying-W
perspective-correct interpolation. Fixed two-pixel L-infinity geometry and
texture-transition bands are declared before runtime. Outside bands, exact
RGB is mandatory. Texture bands permit only relevant quadrant colors;
geometric bands allow only the eight texture colors/background. These bands
are exclusions from exact location claims, not a measured runtime tolerance.
Minimum safe near/far coverage20pixels each and background2000 perrendered
frame. HighXbyte and pitch padding excluded. Five clear/draw streams total
163840capturedbytes,122880RGBbytes; source before/after add1024exactbytes.

Host001 FAILED coverage: far triangle had only15safe pixels in first two
frames. It remains preserved C:/xwn495/host001. Near triangle shiftedleft1/8
for newhost002; thresholds/bands unchanged. Host002 establishes mask coverage
before testing negative scenes so a construction error cannot masquerade as
negative rejection. Host003 adds independent literal color witnesses and
missing/flat-texture controls; oracle bytes identical002/003.

Host snapshots are synthetic and share some geometry helpers; independent
literal projected coordinates and eight hand-derived pixel witnesses anchor
those helpers. Actual Windows/D3D output, API/state metadata and full transport
are still absent. No existing closed guest result is reused as new evidence.
