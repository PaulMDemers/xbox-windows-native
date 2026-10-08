# Evict CPU-written surfaces on the renderer thread

This candidate removes the cached GL surface after its first CPU write. It does
not introduce a second watch activation state or a new synchronous CPU job.
The existing surface recreation path uploads CPU memory on subsequent GPU use.

Only calls executing on the vCPU thread request eviction. The existing physical
memory hook also receives DMA/debugger accesses; those retain original behavior.
Their callback traversal is not covered by the vCPU exclusive-work guarantee.
The first unguarded build is preserved, never launched.

The CPU callback holds PGRAPH while marking every overlapping surface for eviction
and requests the existing renderer download worker. It then drops PGRAPH and waits
using the existing completion event. The actual guest CPU store has not happened.
The renderer processes the request under PGRAPH, downloads any dirty contents,
marks bound targets for recreation, and invokes the existing surface invalidator.
Only the renderer unbinds/deletes GL objects and frees SurfaceBinding. It signals
the existing completion event after the work, allowing the CPU store to proceed.

Watch removal uses the existing queued exclusive CPU operation and TLB flush.
`async_safe_run_on_cpu` and `tlb_flush_all_cpus_synced` queue work; they do not wait
for the CPU callback to finish. Thus the renderer does not wait for the CPU while
the CPU waits for the renderer. The callback opaque is stable NV2AState, not the
freed SurfaceBinding. The CPU callback retains no SurfaceBinding pointer after
unlocking PGRAPH. The separate MemAccessCallback list node remains alive until
queued CPU work removes it after the callback/iteration has returned.

Multiple watches can trigger on the same access. The first callback marks all
overlapping cached surfaces; later callbacks may scan an empty region until queued
removal runs. No watch node is freed inline. A newly created overlapping surface
uses a different callback allocation and existing FIFO CPU work ordering.

The worker checks dirty contents again before eviction, covering a GPU command
that ran between the CPU's request and worker processing. The invalidator's bound
surface assertion requires buffer_dirty; the candidate also clears the matching
draw/write cache flags after the data has reached RAM. Other bound surfaces retain
their state. Reset can invalidate a pending surface before the worker visits it;
the worker then has nothing to evict and still completes the request. Reset data
preservation remains the existing renderer contract and needs separate testing.

This trades cached GPU objects for fewer CPU callbacks. Workloads that alternate
CPU/GPU writes could allocate more textures, so the native coherence controls alone
cannot establish acceptable performance. No shared dirty bitmap, guest paging flag,
global callback disable, forced reset or framebuffer relocation is involved.

Qualification must include matched fresh control/candidate builds; read-first and
unread/write-first exact native readbacks; actual CPU-write eviction and subsequent
recreation; reset/overlap coverage appropriate to this policy; and the Windows
correctness/cold audit before ordinary performance measurement. Until then this is
an experimental candidate, not a recommended emulator or physical deployment.
