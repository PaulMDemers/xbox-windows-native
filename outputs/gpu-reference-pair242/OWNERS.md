# Actual source owners and missing completion evidence

All paths below are from the pinned build004 source capsule. This is a source
review, separate from the new paired runtime observations. No disposal has been
invoked by242. Existing preserved native/hardware builds stay unchanged.

| Reference | Owner and actual disposal path | Completion requirement still needed |
| --- | --- | --- |
| Surface list, color/zeta bindings, GL surface buffers | GL worker under renderer/PG ownership; surface.c pgraph_gl_surface_invalidate unbinds matching surface, removes list entry, queues callback removal, deletes GL buffer and frees surface | Actual paired disposal/fence evidence after preserved bytes; conflicting aliases must refuse |
| Surface CPU access callback | physmem.c mem_access_callback_remove_by_ref queues do_mem_access_callback_remove_by_ref through async_safe_run_on_cpu; that CPU callback removes its list entry and frees callback | CPU-exclusive removal actually completed, not merely enqueued; safe stopped-CPU execution and lock ordering need a separate bounded protocol |
| Texture cache binding and current texture units | texture.c texture_binding_destroy decrements refcnt, deletes GL texture/frees binding at zero; cache post-evict and texture-binding replacement each own references | Every modeled ref released once, cached/current alias relationship accounted for, actual GL/context completion |
| Shader cache programs and save handles | shaders.c cache post-evict joins non-null save_thread, deletes GL program and frees saved program; disk reload accesses cache under shader_cache_lock | Non-null handle does not prove live thread; disk reload/save ownership and join must be bounded outside locks needed by actors |
| Shader modules | shaders.c shader_module_cache_entry_post_evict deletes GL shader; renderer-owned module cache | Defined context and actual complete deletion; no assumption that cache counts alone prove this |
| Element cache and vertex/inline buffers | vertex.c finalize_buffers deletes element buffers, flushes LRU, deletes inline/memory/vertex-array objects | All objects retained by draw/display paths must be accounted for before teardown |
| Display buffer and display render objects | display.c finalize_display deletes display texture, program, VAO, VBO, framebuffer and overlay texture; separate render/display contexts are shared | Frontend/UI use, context ownership and pending sync/fences need explicit completion |

process_queued_cpu_work in cpu-common.c removes work under work_mutex, drops it
before execution, and for exclusive work drops BQL around start_exclusive and
the callback. The removal work is not a synchronous return value of the surface
unregister call.242 intentionally does not inspect/manipulate that queue or run
its callbacks. The callback opaque is the device, not the SurfaceBinding;
surface_access_callback traverses the currently owned surface list under PG.
That fact does not prove all CPU hooks have been retired.

Display has an additional unresolved source concern:
pgraph_gl_get_framebuffer_surface takes FIFO, contains a source FIXME about a
possible PG race, retains a selected surface during its setup and waits for
sync_complete after releasing FIFO. The read-only census doesn't make that
frontend path atomic or establish that no waiter retains a display resource.
Do not use presence of global GL contexts or a zero host pointer as retirement.

Shader/element/module cache census counts are bounded summaries, not individual
VRAM range/GL identity inventories. Texture entries carry modeled texture and
palette ranges; surface entries carry modeled ranges and callback presence.
CPU callbacks and actual GL bindings are explicitly unobserved. Further native
ownership remains refused until their completion is established.
