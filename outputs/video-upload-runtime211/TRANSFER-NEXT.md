# A transfer prototype follows the byte result, not another bounds guess

The pinned xemu revision e72e76bd supplies ContextSurfaces2D/NV062 and
ImageBlit/NV09F dispatch leads. The GL and Vulkan backend code is a model of
transfers; its host memmove is not a measurement or description of the physical
NV2A implementation. transfer-source-leads.json records line locations and full
file hashes; artifacts/transfer-leads211 retains exact source bytes privately.
No new register, channel or DMA programming was performed.

Use only after the closed physical pair confirms its measured producer result:

1. Inventory current ShadowBits allocation/lifetime and shared0106 mapping,
   actual NT5 exported contiguous-allocation/locking/physical-address primitives,
   and the existing owned GPU initialization code. A virtual Eng bitmap pointer
   is not by itself a valid GPU DMA source. Pin actual exports and source versions.
2. Design an isolated transfer-only capability with bounded source/destination
   extent arithmetic, cache visibility, exclusive FIFO/channel/context ownership,
   resident completion observation and timeout cleanup. Keep scanout, encoder,
   bootvid, storage, devices and existing CPU upload policy unchanged.
3. Start with a tiny disjoint rectangle, CPU oracle, surrounding guards and
   independent raw physical RGB check. Join/drain every GPU transfer before
   readback, buffer destruction, normal ownership change or fallback; a timeout
   does not permit freeing a DMA buffer still in use. Define failure recovery
   without inventing successful completion. Remain CPU-only if safe recovery or
   crash ownership cannot be guaranteed.
4. Expand only after that result to pitch/offset limits, complex clips, overlap,
   full-screen coherence and ordinary shutdown/cold integrity. Hardware timing
   needs a fresh matched isolated pair; xemu backend timing cannot establish it.

The existing late-cache review rejects remapping this same framebuffer from UC
to WC while preserving its continuously resident crash pointer. Do not relaunch
that failed design or mix cache types for aliases. A separate scanout allocation
is a different architecture with additional memory and crash-safe encoder/switch
requirements, not an isolated flag. New modes likewise need their own framebuffer
size/stride/encoder/handoff and rollback qualification.
