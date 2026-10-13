# Next: turn measured display-write cost into a reviewed optimization

368 is CLOSED. Do not repeat its launch, scans, collection or audit. Original303 driver and normal E startup are restored; F rollback retained; console C remains prohibited. All processes closed, no hardware test queued, automation paused.

The four physical calls measured approximately6.4ms RAM versus10.9ms display per900KiB. Together with353's unchanged copy timing, this directs the next source-level work toward the display-write path rather than another unroll of the same routine. Do not claim cache policy is the sole cause or extrapolate four instrumented calls into desktop FPS.

Review the exact installed300/303 mapping and all consumers before proposing a new candidate. Current chain:303 surface -> miniport300 XwnSharedMap -> bootvid300 XwnFbAcquire -> one permanent MmNonCached mapping. XwnFbPublish explicitly requires that policy. The whole9MiB reservation includes the visible display and hidden boot backbuffer. Boot/error/shutdown drawing retains the pointer even when desktop reference count reaches zero. That count and InbvCheckDisplayOwnership are not cache-transition or exclusive drawing locks.

A cache-policy experiment requires evidence of actual NT5 kernel support, effective type, full physical alias/consumer inventory, ordering/flush requirements, hidden-backbuffer handling, and boot/error/shutdown fallback behavior. Do not change one MmMapIoSpace argument, add a conflicting alias, edit live PTE/MTRR/PAT state, or treat the sampled endpoint joins as exhaustive alias exclusion. Prefer a coherent boot-time ownership design over an unproved live transition. Independently consider whether existing dirty-region coalescing uploads unnecessary bytes, using the already captured344/353 operation counts before asking for another diagnostic boot.

Only a concrete reviewed implementation with host/source checks and a fresh matched emulator control/candidate should advance to physical testing. Keep all event gates and rollback ordering. Native GPU ownership and hardware acceleration are separate work. The unrelated Ftdisk49 and Srv2013 issues remain open; leave dashboard C untouched.
