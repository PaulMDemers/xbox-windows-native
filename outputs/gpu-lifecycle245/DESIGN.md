#245 natural callback and display lifecycle

Observation only on a NEW immutable239 child with unchanged native224/219/211
captured core policy; no synthetic null bindings, physical IO or peer integration.
Existing242 preservation and census remain exact except added trace calls around
natural surface disposal. No new disposal, queue draining, GL fence, actor wait,
native grant or admission change. Complete reference retirement is never inferred from counts.

Actual compiled244/build005 keeps PCIDevice parent_obj FIRST, with a compile-time
offset-zero assertion. Failed244/build004 prepended the marker field before its
QOM parent, so its first marker request was refused and preservation never ran.
That run and incomplete cold-audit failure remain separate, never requalified.

Callbacks log insert request, actual CPU insertion, remove request and actual unlink, and free completion
AFTER actual CPU-exclusive free. Before freeing, scalar pointer identity,
address and length are saved; no later dereference. Pointer reuse is a NEW
generation, never a permanent ticket. A CPU thread pairs unlink with subsequent
free completion even if a new producer request reuses that pointer before the
free-completion log. No log underflow or missing completion is treated as success. Insert completion may follow remove request;
the asynchronous FIFO order of actual insert/remove executions is checked.
Surface registration maps the hook identity to its VRAM range. Invalidation logs
begin/end around the EXISTING unregister, GL delete, list removal and free.
GL deletion return is not proof of context-wide release or GPU completion.

Frontend logs its actual renderer-locked loan begin, returned framebuffer ID,
actual UI selected/fallback texture, existing glFinish return, loan release and
post-release. Per-thread event pairing prevents treating another actor's fence
as completion. The existing rendering guard serializes frames. A selected
fallback texture is kept distinct from the accelerated display buffer.
Synchronization logs entry, empty-surface return, or existing render/display
fence return. It adds no GL state query or synchronization.

QOM accepts exactly two true marker calls (serialized monitor/BQL), no reset.
Marker41 is CPU-stopped/pinned Xromwell after its finite snapshot and before
preservation. Marker42 is the SAME boot's CPU-stopped/pinned FreeLoader after
200ms outside all actor locks. CPU stopped does not mean GPU/UI stopped, and a
queue request is not completion. A done event includes actual cpu->stopped.
The 200ms interval is observation opportunity, never a timeout success fallback.
Events are enabled from process creation through marker42 then disabled once.

Both QEMU log-backend event functions use existing synchronized logger; records
include monotonic real clock and actual host thread ID. Concurrent log ordering
is not a globally atomic actor snapshot; all asserted chains must be causal
per-reference/per-thread and complete before the second marker. A partial
frontend loan at a boundary stays partial. Run limit480s, host log limit16MiB,
GDB stop limits20s and full point teardown/mode0/resume are inherited. No RAM
captures (which invoke callbacks). Strict events, CPU workload, cold allocation,
five hives, protected hashes, startup and actual policy remain unchanged gates.

This diagnostic cannot qualify complete reference retirement or native GPU
ownership: texture/shader/module/vertex/display contexts still own references,
the UI can begin another loan, GL deletion may defer actual destruction and
there is no complete producer-close protocol.
