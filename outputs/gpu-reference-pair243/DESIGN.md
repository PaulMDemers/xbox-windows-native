#243 host interpretation correction, unchanged242 binary

242 captured real before/after inventory and preserved3072000 bytes, then its
host qualifier wrongly required stats[3] (enabled interrupt mask) to be zero.
Actual source initializes enabled interrupts toFFFFFFFF, distinct from pending
interrupts0.242 failed trace/overall result remains failed, never replayed or
retroqualified. It resumes the guest and retains the normal workload/cold audit.

243 uses a NEW unique runtime, same immutable239 seed and unchanged compiled242
build004. Host qualifier gates pending/wait/work indices1,2,4,5,6 at zero and
requires enabled index3 to match the actual pre-observed PG row field5. This
corrects a category error, does not suppress an event or waive a pending-work
gate. Actual host tests now include the observed nonzero enabled mask and reject
a changed mask. All other surface/reference/chronology/cold/event gates unchanged.

New242 before/after slots belong to the one227 preservation owner; FIFO admission
is actually halted at each separate FIFO/PG sample before old finish restores it.
No additional request/reset, GL query/disposal, callback removal, worker join or
native permit. No pre/control RAM read and no pmemsave. CPU callback queues and
actual GL bindings remain explicitly unobserved. Shader/module/vertex summaries
are not complete per-object identity inventories. Save handles aren't liveness.

Read outputs/gpu-reference-pair242/DESIGN.md/OWNERS.md for exact locks, bounds,
timing, publication and limits. Same captured211/no-null device policy, native224
and219 payload, strict event gates. Full debugger teardown/resume and normal
restart/dashboard/orderly VM exit/cold allocation/hives/protected audit required.
Emulator-only; no physical access, no ordinary/native acceleration qualification.

Earlier compiled tests and binary/source capsules are reused with hash checks,
not represented as new compiler/sanitizer runs. Only new host interpretation tests
execute here. Build copies/manifests retain their actual242 origin paths.
