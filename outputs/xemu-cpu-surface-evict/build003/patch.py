"""Renderer-owned eviction after a CPU write; no new callback API or CPU wait."""
def once(text,old,new):
    assert text.count(old)==1,old[:100]
    return text.replace(old,new)

def apply(surface,header):
    header=once(header,'    bool download_pending;','    bool download_pending;\n    bool cpu_write_evict_pending;')
    surface=once(surface,'    entry->download_pending = false;',
        '    entry->download_pending = false;\n    entry->cpu_write_evict_pending = false;')
    surface=once(surface,'''        if (write) {
            surface->upload_pending = true;
        }''','''        if (write) {
            surface->upload_pending = true;
            /* The renderer must preserve GPU contents before dropping its
             * cached surface. Do not free it or its CPU watch here. */
            if (qemu_cpu_is_self(qemu_get_cpu(0)) &&
                d->pgraph.primitive_mode == PRIM_TYPE_INVALID) {
                surface->cpu_write_evict_pending = true;
                wait_for_downloads = true;
            }
        }''')
    surface=once(surface,'''    SurfaceBinding *surface;
    QTAILQ_FOREACH(surface, &r->surfaces, entry) {
        surface_download(d, surface, false);
    }

    qatomic_set(&r->downloads_pending, false);''','''    SurfaceBinding *surface, *next;
    QTAILQ_FOREACH_SAFE(surface, &r->surfaces, entry, next) {
        surface_download(d, surface, false);
        if (surface->cpu_write_evict_pending) {
            surface->cpu_write_evict_pending = false;
            /* BEGIN can execute after the CPU request but before this worker.
             * Keep bindings alive for the whole primitive, including vertices
             * queued for END. Fall back to the original upload/download path. */
            if (pg->primitive_mode != PRIM_TYPE_INVALID) {
                continue;
            }
            /* A queued GPU operation may have dirtied it after the request.
             * Finish that download while holding the renderer's PGRAPH lock.
             * The CPU store is still blocked in surface_access_callback. */
            pgraph_gl_surface_download_if_dirty(d, surface);
            assert(!surface->draw_dirty);
            if (surface == r->color_binding) {
                pg->surface_color.buffer_dirty = true;
                pg->surface_color.draw_dirty = false;
                pg->surface_color.write_enabled_cache = false;
            }
            if (surface == r->zeta_binding) {
                pg->surface_zeta.buffer_dirty = true;
                pg->surface_zeta.draw_dirty = false;
                pg->surface_zeta.write_enabled_cache = false;
            }
            trace_nv2a_pgraph_surface_evict_reason("cpu-write", surface->vram_addr);
            /* GL deletion/unbinding belongs to this renderer thread. The
             * independent MemAccessCallback is removed by queued CPU work;
             * its opaque is NV2AState, never this freed SurfaceBinding. */
            pgraph_gl_surface_invalidate(d, surface);
        }
    }

    qatomic_set(&r->downloads_pending, false);''')
    return surface,header
