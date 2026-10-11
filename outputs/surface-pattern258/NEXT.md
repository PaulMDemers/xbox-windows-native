# Add the renderer half in a new kit

258 emu001 is CLOSED and cold-audited. Never relaunch or recollect it. All owned
sessions36361,38634,30874,87485 are closed. Read REPORT, lineage-review and the
actual baseline result. The258 driver intentionally holds one allocation until
reboot; there is no safe published-buffer release operation to reuse.

Start a fresh child from the pre-execution258 source image, not its used disk.
Use a NEW case/kit and review any inherited descriptive fixture fields. The
existing CPU-only probe cannot accept GPU-modified bytes: build a separate
explicit renderer-mode probe with an independent expected-pixel calculation.
Keep the current ordinary baseline and all original failures.

The258 exported X258Checkpoint and its pinned RVA can provide paired debugger
stops in the probe's actual address space. Verify resident bytes/process context
before using a breakpoint; do not assume the preferred image base was honored.
Attest arena generation, owning FileObject and four physical pages from actual
driver state, not only the log. The physical address from emu001 is not reusable.

Use the reviewed257 xemu source as a future diagnostic parent. On the existing
worker/context admission path, require a stopped guest, halted producer, joined
frontend/worker state and no pending primitive. Verify the entire arena is
disjoint from every live surface and any other tracked guest renderer reference.
Reject incomplete reference coverage rather than treating absence from one list
as an ownership grant. The memory belongs to the dedicated diagnostic driver;
Windows native GPU access remains refused.

The host oracle defines an asymmetric13x11 BGRA8 texture at arena+4096 with
64-byte rows and untouched padding/guards. Upload independently generated pixels
to a diagnostic texture while leaving CPU memory at its distinct initial pattern.
Validate actual GL format, scale factor, row layout and texture provenance.
Mark only this test surface dirty. Preserve and restore all affected GL bindings;
do not overwrite live guest framebuffer data.

For age eviction, set only the test surface's age, not global frame time. Before
calling the actual surface_evict_old path, require no other surface would be
evicted by that call; otherwise refuse. Compare the entire16KiB after readback,
including guards and padding, then prove deletion and callback unlink/free.

For a separate real CPU-alias case, observe callback insertion before allowing
the guest load. Require a dirty CPU-read download, then a second known GPU update
before the CPU store. The existing callback blocks that store while the worker
downloads/removes the surface. Verify the resumed store's newer pattern remains,
and that stale GPU bytes cannot overwrite it afterward. Host memcpy is not CPU
callback coverage. Pair callbacks by generation/range, not pointer value alone.

Bound every request, worker wait and guest stage. Any incomplete teardown or
failed controller closes the sacrificial emulator and preserves the disk; never
free/reuse the arena to continue after uncertain retirement. Require both pixel
cases and negative controls before a preservation claim. Maintain full cold
audit and inherited strict event failures. No functional video fix is justified
by the CPU arena or host oracle alone.
