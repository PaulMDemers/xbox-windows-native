#238 published observation schema

Header version238, terminal state3, tuple_published1, journal total/count/capacity256/overwritten. Current journal row retains233's 21-field format and FIFO-valid0. Historical rows retain their own validity, sequence and loss accounting.

`fifo_when` is the FIFO sample time; the current journal row's time is the later PG sample time. Publication is immutable, sampling is not simultaneous. The separate `fifo` vector has14 unsigned fields:

0 halt;1 kick;2 FIFO pending interrupts;3 FIFO enabled interrupts;4 DMA_GET;5 DMA_PUT;6 DMA_STATE;7 PUSH0;8 PUSH1;9 DMA_PUSH;10 PULL0;11 STATUS;12 DMA_SUBROUTINE;13 atomically read PGRAPH_FIFO. Fields0 through12 are FIFO-lock owned. Field13 is an atomic PG register read under FIFO lock, not a PG-lock-owned sample.

The20 context fields are0 primitive_mode;1 draw_arrays_length;2 inline_array_length;3 inline_elements_length;4 inline_buffer_length;5 framebuffer_in_use;6 flush_pending;7 sync_pending;8 CTX_USER;9 SURFACE;10 dma_color;11 dma_zeta;12 2D object_instance;13 2D dma_image_source;14 2D dma_image_dest;15 blit context_surfaces;16 GL renderer present;17 renderer type;18 color binding present;19 zeta binding present. Fields5/18/19 require renderer_valid1; otherwise their zeros mean unavailable, not absent. PG scalars are read under PG lock, pending flags atomically, and framebuffer state under renderer lock.

`renderer_valid` records successful renderer try-lock and nonnull GL state. `surface_count` is at most128. `surface_truncated` means there was a129th entry, without dereferencing it. Every surface row has12 unsigned fields:0 VRAM address;1 size;2 pitch;3 width;4 height;5 flags;6 memory access callback present;7 equals bound color;8 equals bound zeta;9 GL buffer identifier;10 DMA address;11 DMA length. Flags1 draw_dirty,2 download_pending,4 CPU-write eviction pending,8 upload_pending,16 cleared,32 color,64 swizzle. Raw host pointers are not published. Callback presence is a retained reference, not callback execution or synchronization proof. GL buffer identifiers are not proof of live host GPU contents.

This bounded list does not enumerate texture/shader/display-context references, complete GPU commands, fence, download pixels or grant native ownership. DMA equality alone does not prove parser completion or closed producer admission. Range validation/overlap analysis is a separate post-observation check, never a silent reason to discard a captured entry. Current CPU entry bytes and lifecycle guards remain separate required evidence.
