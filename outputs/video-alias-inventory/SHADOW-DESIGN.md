# Shadow-surface decision and required contracts

This is a design lead, not an implemented display driver. The fixed-driver
profile compares a system-memory overlap plus upload with screen overlap, with
independent final-pixel verification. Even a favorable emulator result needs a
separate physical measurement; the current CPU/device model is not a physical
memory-bandwidth oracle. At1024x576x32 one shadow costs2,359,296 bytes before
allocation overhead. RAM cost matters on the64MiB Xbox.

A complete shadow path must preserve one authoritative pixel image for every
supported render and readback operation, and copy changed destination pixels to
the framebuffer before successful synchronous completion. A temporary RAM copy
that first reads the framebuffer cannot remove the initial read cost. Merely
redirecting BitBlt misses text, paths, cursor operations and other drawing entry
points; advertising a bitmap while allowing unobserved engine writes can leave
the scanout stale. Do not implement only a favorable benchmark path.

Microsoft documents [DrvBitBlt](https://learn.microsoft.com/en-us/windows/win32/api/winddi/nf-winddi-drvbitblt)
with clipping, translation, masks and raster operations, and allows forwarding
to EngBitBlt. An owned device surface can represent driver-managed storage via
[EngCreateDeviceSurface](https://learn.microsoft.com/en-us/windows/win32/api/winddi/nf-winddi-engcreatedevicesurface).
Proposed use of a separate engine bitmap for software fallback is an engineering
inference requiring NT5 tests; it is not established by the API names alone.

[DrvSynchronize](https://learn.microsoft.com/en-us/windows/win32/api/winddi/nf-winddi-drvsynchronize)
is called before direct engine drawing, so it cannot serve as an assumed generic
after-draw shadow upload callback. Do not turn on that hook and claim complete
scanout synchronization. Current Microsoft documentation must also be checked
against pinned NT5 exports and actual callbacks before implementation.

A future isolated owned display candidate needs:

- Explicit surface identity, backing bitmap, stride/format bounds, allocation
  limits and failure unwind. Keep the physical mapping alive until consumers
  and surfaces are released; preserve0097 cleanup lessons without assuming its
  unqualified generic PnP lifecycle is solved.
- Full render/readback fallback, region clipping, negative or offscreen source
  coordinates, overlapping copies in both axes, and nontrivial ROP/masks/fonts.
  Passing the SRCCOPY profile is necessary but insufficient.
- Software/hardware cursor agreement, pointer hide/show during readback, mode
  assert/re-enable, disable ordering, allocation failure and repeated boot tests.
- Genuine pixel oracles plus external scanout checks: reading the shadow back
  cannot prove the real framebuffer was updated. Instrumented comparison must
  compare both surfaces after completion without relying on the display's own
  readback implementation as the only oracle.
- Matched unchanged-miniport control; fixed device policy and storage stack;
  ordinary full cold/event gates before any physical trial. No GPU FIFO/cache
  policy/mode changes in the same candidate.

Before that larger change, a bounded direct-RAM mapping comparison remains an
alternative experiment, but0096's stop/remove/restart consumer-lifetime gap must
remain explicit. Neither route is promoted by these notes. HD mode selection
and1080i reservation/encoder handling remain separate work.
