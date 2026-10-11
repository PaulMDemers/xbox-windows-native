# One-shot frontend admission closure

This new emulator child uses the exact compiled244/build005 parent and immutable
239 disk seed. Native drivers, hardware and peer work remain unchanged.

The actual UI rendering token serializes its regular and SDL-event frame paths.
A QOM request only publishes a one-shot close request; it never waits under BQL.
The next UI actor acquiring the token admits no new framebuffer loan. Any prior
frame must already have finished its existing glFinish, loan release and swap.
The actor refuses if BQL is held, context selection fails, the renderer trylock
is busy or the actual loan flag is nonzero. It then uses its own current context
and a 100ms GL fence, records seven actual bindings and last selected texture
liveness, and publishes the scalar record with release/acquire ordering.

No GL object is deleted except the new diagnostic fence. No binding, HUD texture,
surface dirty flag, cache, context or native GPU permit is changed. The closed UI
does not imply that render/display worker contexts are idle or unreferenced.
Dirty data at natural surface invalidation remains an independent unresolved gate.

One reopen is required before guest resume. A pending close can be aborted without
overwriting a reopen request: the UI terminal publication uses CAS. Reopen is
acknowledged by the real UI actor before its next ordinary frame. Timeouts remain
failures, never late success or automatic grant. Host cleanup always attempts the
one reopen after an accepted close before removing points/mode0/resuming.

Freeze source/binary/fixture pins before the sole fresh preserve001 launch. Keep
the old244 failed layout/audit and245 result unchanged. Require actual loader
resident pins, prior preservation, close/reopen causal trace, closed interval with
zero new loans, normal restart and complete existing cold audits. Strict Ftdisk49
remains a failure. This debugger run never qualifies physical acceleration.
