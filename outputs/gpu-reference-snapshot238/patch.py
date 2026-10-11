"""New one-shot observation only; FIFO and PG phases deliberately distinct."""
def replace(s, a, b):
    assert s.count(a) == 1, a[:100]
    return s.replace(a, b)

def apply(root):
    names=['hw/xbox/nv2a/nv2a.c','hw/xbox/nv2a/nv2a_int.h',
           'hw/xbox/nv2a/pgraph/gl/renderer.c']
    for name in names:
        p=root/name
        s=p.read_text(encoding='utf-8').replace('snapshot234','snapshot238').replace('Snapshot234','Snapshot238').replace('/*234','/*238').replace('version=234','version=238')
        p.write_text(s,encoding='utf-8')
    p=root/names[1];s=p.read_text(encoding='utf-8')
    s=replace(s,'    NV2AWaitRow233 current, rows[NV2A_WAIT233_CAPACITY];', '''    NV2AWaitRow233 current, rows[NV2A_WAIT233_CAPACITY];
    /* FIFO sample precedes PG sample; publication is atomic, sampling is not. */
    uint64_t fifo_when, fifo[14], context[20], surfaces[128][12];
    unsigned renderer_valid, surface_count, surface_truncated;
''')
    s=replace(s,'void nv2a_snapshot238_copy(NV2AState *d);','void nv2a_snapshot238_copy(NV2AState *d);\nvoid nv2a_snapshot238_fifo(NV2AState *d);')
    p.write_text(s,encoding='utf-8')
    p=root/names[0];s=p.read_text(encoding='utf-8')
    s=replace(s,'/* Caller holds actual PG lock, FIFO has been released. No FIFO reads. */', '''/* Actual FIFO lock is already owned; PG is NOT acquired here. */
void nv2a_snapshot238_fifo(NV2AState *d)
{
    uint32_t words[10];
    nv2a_preserve231_snapshot(d, words);
    d->snapshot238.fifo_when = qemu_clock_get_ns(QEMU_CLOCK_REALTIME);
    d->snapshot238.fifo[0] = d->pfifo.halt;
    d->snapshot238.fifo[1] = d->pfifo.fifo_kick;
    d->snapshot238.fifo[2] = d->pfifo.pending_interrupts;
    d->snapshot238.fifo[3] = d->pfifo.enabled_interrupts;
    for (unsigned i = 0; i < 10; i++) {
        d->snapshot238.fifo[4+i] = words[i];
    }
}

/* Caller holds actual PG lock, FIFO has been released. No FIFO reads. */''')
    s=replace(s,'        wait233_format(report, &d->snapshot238.current);', '''        NV2AWaitSnapshot238 *v = &d->snapshot238;
        g_string_append_printf(report, " fifo_when=%" PRIu64
            " renderer_valid=%u surface_count=%u surface_truncated=%u fifo=",
            v->fifo_when, v->renderer_valid, v->surface_count, v->surface_truncated);
        for (unsigned i = 0; i < 14; i++) {
            g_string_append_printf(report, "%s%" PRIu64, i ? "," : "", v->fifo[i]);
        }
        g_string_append_printf(report, " context=");
        for (unsigned i = 0; i < 20; i++) {
            g_string_append_printf(report, "%s%" PRIu64, i ? "," : "", v->context[i]);
        }
        for (unsigned n = 0; n < v->surface_count; n++) {
            g_string_append_printf(report, " surface=");
            for (unsigned i = 0; i < 12; i++) {
                g_string_append_printf(report, "%s%" PRIu64, i ? "," : "", v->surfaces[n][i]);
            }
        }
        wait233_format(report, &d->snapshot238.current);''')
    p.write_text(s,encoding='utf-8')
    p=root/names[2];s=p.read_text(encoding='utf-8')
    start=s.index('    /*238 worker enters');end=s.index('    /* Request is one-shot',start)
    s=s[:start]+'''    /*238 FIFO-owned sample first. Renderer lock is TRY only, then FIFO is
     * released BEFORE PG acquisition. Never block FIFO/BQL on renderer lock.
     * This is not a producer halt, reference release, fence or readback. */
    if (nv2a_snapshot238_claim(d)) {
        nv2a_snapshot238_fifo(d);
        bool renderer_locked = !qemu_mutex_trylock(&pg->renderer_lock);
        qemu_mutex_unlock(&d->pfifo.lock);
        qemu_mutex_lock(&pg->lock);
        nv2a_snapshot238_copy(d);
        NV2AWaitSnapshot238 *v = &d->snapshot238;
        uint64_t context[20] = {
            pg->primitive_mode, pg->draw_arrays_length, pg->inline_array_length,
            pg->inline_elements_length, pg->inline_buffer_length,
            renderer_locked ? pg->framebuffer_in_use : 0,
            qatomic_read(&pg->flush_pending), qatomic_read(&pg->sync_pending),
            pgraph_reg_r(pg, NV_PGRAPH_CTX_USER), pgraph_reg_r(pg, NV_PGRAPH_SURFACE),
            pg->dma_color, pg->dma_zeta,
            pg->context_surfaces_2d.object_instance,
            pg->context_surfaces_2d.dma_image_source,
            pg->context_surfaces_2d.dma_image_dest, pg->image_blit.context_surfaces,
            r != NULL, pg->renderer->type,
            renderer_locked && r ? r->color_binding != NULL : 0,
            renderer_locked && r ? r->zeta_binding != NULL : 0,
        };
        memcpy(v->context, context, sizeof(context));
        v->renderer_valid = renderer_locked && r != NULL;
        if (v->renderer_valid) {
            SurfaceBinding *surface;
            QTAILQ_FOREACH(surface, &r->surfaces, entry) {
                if (v->surface_count == 128) {
                    v->surface_truncated = 1; break;
                }
                uint64_t fields[12] = {
                    surface->vram_addr, surface->size, surface->pitch,
                    surface->width, surface->height,
                    (surface->draw_dirty ? 1 : 0) |
                    (surface->download_pending ? 2 : 0) |
                    (surface->cpu_write_evict_pending ? 4 : 0) |
                    (surface->upload_pending ? 8 : 0) |
                    (surface->cleared ? 16 : 0) |
                    (surface->color ? 32 : 0) | (surface->swizzle ? 64 : 0),
                    surface->access_cb != NULL, surface == r->color_binding,
                    surface == r->zeta_binding, surface->gl_buffer,
                    surface->dma_addr, surface->dma_len,
                };
                memcpy(v->surfaces[v->surface_count++], fields, sizeof(fields));
            }
        }
        qemu_mutex_unlock(&pg->lock);
        if (renderer_locked) { qemu_mutex_unlock(&pg->renderer_lock); }
        nv2a_snapshot238_publish(d);
        qemu_mutex_lock(&d->pfifo.lock);
    }

'''+s[end:];p.write_text(s,encoding='utf-8')
