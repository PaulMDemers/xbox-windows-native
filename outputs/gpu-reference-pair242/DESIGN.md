#242 paired reference observation

Emulator-only opt-in diagnostic using unchanged native224/build002,219 bootvid,
captured211 core policy and immutable239 seed. Actual239/control001 and241
preservation remain closed; no replay. No physical access or peer integration.

One actual stopped Xromwell entry request uses existing227 preservation ownership
and5-second deadline. New242 slots are separate from238 observer and each other:
FIFO sample0 under FIFO lock with admission halted; release FIFO; acquire PG
with existing renderer TRY ownership; capture0 with shader-cache TRY lock; actual
preservation fences/full comparisons; capture1; release PG; reacquire FIFO;
FIFO sample1; existing finish restores old halt only on safe3/4, then releases
terminal publication. No lock waits added, apart from unchanged PG acquisition.
FIFO and PG sampling times differ; the samples are not an atomic all-thread
snapshot. Producer halt is measured in both intervals. Guest CPU remains stopped.

Only3/4/6 worker-published terminal states expose valid slots. Timeout5 hides all
slots even if a late worker writes them. No reset, second request or reuse. An
invalid initial capture refuses42 before preservation. Invalid post-capture
after readback fails6/reason43 and retains quarantine; deadline remains terminal.
Normal non-opt-in rendering and previous preservation implementation unchanged.

Read-only inventory copies up to128 surface rows/512 texture-cache rows,4 bound
texture records, context20 and stats48. Cache walks bound at512/51200 nodes and
check actual worker state/deadline per node; free nodes' uninitialized payloads
are never read. Shader cache counts and active data are protected by TRY lock.
All used-counts must agree with walked active counts, no silently truncated PASS.
No GL queries, invalidation, callback removal, disposal, joins or native permit.

Texture rows identify VRAM texture/palette ranges and GL model IDs/refcounts;
shader/module/vertex rows summarize active counts, initialized programs and
non-null save handles. A save handle is not thread-liveness/completion proof.
Display/vertex/framebuffer handles describe the renderer's CPU model; they are
not GL object/binding validation or proof that UI/display context refs are gone.
CPU callback queues and their completion are explicitly unobserved. Therefore
this is a finite reference census, not complete retirement qualification.

The expected pixel buffer and actual surface download use the same conversion
implementation: separate allocation/full comparison, no independent pixel oracle.
No pre/control RAM read; pmemsave invokes GPU callbacks.242 does not need any RAM
capture; existing241 private post-success buffers remain evidence separately.

Unique preserve001 runtime, complete debugger teardown/resume, existing normal
restart/dashboard/orderly host exit, full allocation,5 hives/protected/staged
hashes and unchanged strict events. Ftdisk49 remains a failure if observed. No
ordinary/physical/accelerated GPU ownership qualification from diagnostic data.
