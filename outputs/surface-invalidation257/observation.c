/*257 Bounded scalar observation only; caller's existing PGRAPH discipline.
 * No GL calls, pixel writes, resource ownership, downloads or disposal changes. */
static unsigned surface257_count[13];
static uint64_t surface257_sequence;
static void trace_surface257(NV2AState *d, const SurfaceBinding *s, unsigned site)
{
    PGRAPHState *pg=&d->pgraph;
    PGRAPHGLState *r=pg->gl_renderer_state;
    if (site>=13 || qatomic_read(&surface257_count[site])>=257) return;
    unsigned index=qatomic_fetch_inc(&surface257_count[site]);
    if(index>=256) {
        if(index==256) trace_nv2a_lifecycle244(99,qemu_clock_get_ns(QEMU_CLOCK_REALTIME),qemu_get_thread_id(),site,index,0);
        return;
    }
    uint64_t seq=qatomic_fetch_inc(&surface257_sequence)+1;
    int64_t when=qemu_clock_get_ns(QEMU_CLOCK_REALTIME);
    uint64_t thread=qemu_get_thread_id();
    unsigned flags=(s->draw_dirty?1:0)|(s->download_pending?2:0)|
        (s->cpu_write_evict_pending?4:0)|(s->upload_pending?8:0);
    trace_nv2a_lifecycle244(100,when,thread,seq,site,flags);
    trace_nv2a_lifecycle244(101,when,thread,seq,(uintptr_t)s,(uintptr_t)s->access_cb);
    trace_nv2a_lifecycle244(102,when,thread,seq,s->vram_addr,s->size);
    trace_nv2a_lifecycle244(103,when,thread,seq,s->gl_buffer,(s==r->color_binding?1:0)|(s==r->zeta_binding?2:0));
    trace_nv2a_lifecycle244(104,when,thread,seq,pg->primitive_mode,pg->draw_arrays_length);
    trace_nv2a_lifecycle244(105,when,thread,seq,pg->inline_array_length,pg->inline_elements_length);
    trace_nv2a_lifecycle244(106,when,thread,seq,pg->inline_buffer_length,pg->framebuffer_in_use);
}
