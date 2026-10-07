# Pointer intersection discriminator

Trace003 captured EngCopyBits calls involving small31x27 surfaces around the
central pointer rectangle; the large overlap became15 EngCopyBits calls, while
small overlap took one. This is a concrete software-pointer lead, not measured
time attribution. It motivates a matched ordinary emulator comparison.

Same new probe/binary, fixed1024x576x32 video0093/Microsoft framebuf, same parent
fixture and storage/network/device policy. Only startup environment differs:
inside001 selects pointer512,288; outside001 selects1000,550, beyond the drawing
window. Both explicitly choose the standard arrow; the historical31x27 shape
is not assumed to be that arrow. The pointer remains visible. Every timed loop
checks actual GetCursorInfo handle/visibility/coordinates; each precheck positions
it outside timing and pumps messages. Any unexpected pointer/visibility change
fails the case. No host UI input, driver/cache/mode/device-policy change.

Require54 timing cases and162 exact RGB stages, stable expected pointer position,
normal shutdown/dashboard, all cold allocation/hive/protected/config/pagefile
and strict event gates. Fresh private children; never reuse attempt/output IDs.
Timings include the added pointer-state check equally in both cases. They are
functional xemu measurements, not physical drag FPS or isolated bandwidth.
No debugger runs with this pair; prepare both fixtures before timing runs.

This measures the contribution of visible pointer intersection under these
conditions. It does not authorize hiding the pointer as a product fix, establish
GPU cursor support or implement a new display driver. Any benefit still needs
driver ownership/render/cursor correctness and independent physical validation.
