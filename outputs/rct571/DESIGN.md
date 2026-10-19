# Fresh PC571: preserve and verify game foreground

569 failed on splash/occlusion;570 rejected because the game never became
foreground after the helper minimized its console before game creation. Both
are closed, with successful registry/shutdown cleanup and no Xbox access.
Retain their actual failures. This new child uses immutable404, not either disk.

Remove that premature console minimization. Once the launched PID's visible
game class exists, make one SetForegroundWindow request and log its return.
Keep verifying actual foreground, geometry and exposed mouse targets. Do not
disable foreground policy, join unrelated input queues, or treat an activation
return as sufficient input evidence. Read geometry/foreground context even if
the overall guard rejects. Keep570's hash-only title signatures; their positive
runtime match has not yet been established.

After the bounded sequence finishes or fails, release inputs and close the
game immediately using the existing graceful-close/registry-restore/normal
restart path. Record whether the desktop dimensions return to their initial
values. No idle wait for a human observer. Prepare the PC800x600 desktop and
dismiss its Start balloon before starting the helper. No host game input.

Only independent capture inspection and exact cold readback can qualify cases.
No console deployment, game FPS, native acceleration, audio or save-persistence
claim is implied by this source or a successful build.
