# A separate owned graphics control

The installed nxdk revision58427c078b4ccb0121f359b6b6c536b3b2914976 is suitable as
a source for a NEW standalone homebrew control. The exact reviewed files and
prebuilt pbkit library are pinned in fixture-review.json. The mesh sample has
contiguous texture allocation and real guest draws; the triangle sample provides
simpler vertex setup. Neither already implements the required experiment. The
older color-bars launcher refers to a missing configuration and was not run.

The new control must boot independently in a unique owned disposable fixture. It
must not insert pbkit into Windows or reuse firmware channels as native Windows
ownership. pb_init claims instance memory, creates DMA/graphics contexts and
configures the GPU. That initialization must finish BEFORE the observed interval.
No pb_kill/pb_init, global reset, whole finalizer or renderer switch is permitted
between the before and after measurements. Standalone application initialization
does not establish that Windows can safely acquire the GPU.

Proposed sequence for implementation and review:

1. Allocate four separate immutable linear A8R8G8B8 textures, initially16x8 with
   explicit64-byte pitch, plus independent guards and a distinct render target.
   Produce four different integer pixel patterns. Preserve allocation, physical
   range, shape and raw expected bytes; reject overlap with target, push buffer,
   vertices or other textures. Bound all guest wait loops and record timeouts.
2. Submit real textured draws using the application's own pbkit-created graphics
   and DMA objects. The four texture stages must actually create four distinct
   renderer bindings/cache owners; source setup alone does not prove this. Choose
   shaders with an independent integer framebuffer oracle, nearest sampling and
   known blend/depth/dither settings. First establish pixel coordinates, channel
   layout and tiling in a no-release control; never adjust expected pixels to the
   first observed screenshot. Inspect generated shader instructions and constants.
3. Disable all four texture stages, then issue a real nontextured draw to force
   the normal disabled binder path. Merely updating enable registers does not
   prove unbinding. Submit a guest idle command and poll FIFO/PGRAPH with a finite
   timeout. pb_busy alone does not prove host shader/context/callback quiescence.
4. Reach a compiled, pinned noinline guest checkpoint with a bounded state record.
   A NEW homebrew-specific attestor must pin the actual XBE/loaded instructions,
   checkpoint invocation, application-owned allocations, push-buffer objects and
   address translations. Do not pretend the Windows process/handle/258-driver
   attestation applies here. Stop the guest and use acknowledged renderer/context
   and CPU inventories. Verify refs2/cache1/unit1, disabled state and zero unknown
   edges from actual records before arming the observation-only watch.
5. Resume the guest without host data/register changes. Re-enable and draw with
   the same live allocations and unchanged contents, through normal guest
   commands. The new observer must retain four first binds and all watched
   generation transitions without truncation. Compare independent raw texture
   and GL contents, guards, key and generation, and the resulting framebuffer.
   Selected channels must distinguish all four textures. Capturing unchanged CPU
   arena bytes is not this test. No host invocation of the normal binder.
6. At a second pinned checkpoint collect terminal inventories, seal the observer
   and preserve exact state. Resume bounded guest completion, then orderly host
   exit and appropriate full cold fixture audit. Preserve any timeout, mismatch,
   non-reuse, unexpected replacement or unknown edge as failure, without rerunning
   until a convenient result appears.

No release helper belongs in this first control. Only qualifying actual unchanged
reuse permits a separate matched narrow release candidate, with retained cache
owners and exact context-specific unbinding. The existing proposed268 helper is
still host-only. Future adapter/source changes require new builds and unique IDs.

Framebuffer readback must independently establish the actual surface identity,
pitch and layout; pb_finished changes the back-buffer index after submission and
is not a stable surface reference. The pinned pb_agp_access documents a linear
alias, but its use still needs allocation and coherence evidence. CPU code must
leave source textures untouched throughout both captures, with ownership and
alias review. No claim that two equal samples alone exclude an ABA write.

This experiment isolates emulator texture-reference behavior. Even a full PASS
will not establish native Windows PTE/cache aliases, deferred-release safety,
hardware GPU ownership, physical video acceleration or a measurable speedup.
