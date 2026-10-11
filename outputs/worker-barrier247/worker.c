/*247 One-shot worker checkpoint. Entry/exit own FIFO; all fence waits own NONE
 * of BQL/FIFO/PG/renderer locks. The stopped CPU and acknowledged UI gate are
 * mandatory. No delete, cache flush, dirty clear, callback retirement or permit.
 * State0 unused,1 requested,2 capturing,3 parked,5 released,6 refused/expired.
 * ready publishes an immutable scalar/object record once, independently state.
 */
static void worker247_trace(unsigned phase, uint64_t key, uint64_t a, uint64_t b)
{
    trace_nv2a_lifecycle244(phase, qemu_clock_get_ns(QEMU_CLOCK_REALTIME),
                          qemu_get_thread_id(), key, a, b);
}

static bool worker247_alive(NV2AState *d)
{
    return !qatomic_load_acquire(&d->worker247.release) &&
        qemu_clock_get_ns(QEMU_CLOCK_REALTIME) < d->worker247.deadline &&
        xwn_frontend246_closed();
}

static bool worker247_context(NV2AState *d, unsigned index, GloContext *context)
{
    if (!context || !worker247_alive(d) || bql_locked()) { return false; }
    glo_set_current(context);
    d->worker247.context[index] = (uint64_t)(uintptr_t)context;
    const GLenum fields[7] = { GL_TEXTURE_BINDING_2D, GL_CURRENT_PROGRAM,
        GL_ARRAY_BUFFER_BINDING, GL_ELEMENT_ARRAY_BUFFER_BINDING,
        GL_DRAW_FRAMEBUFFER_BINDING, GL_VERTEX_ARRAY_BINDING, GL_ACTIVE_TEXTURE };
    for (unsigned i=0;i<7;i++) {
        glGetIntegerv(fields[i], &d->worker247.bindings[index][i]);
        worker247_trace(73, index*7+i, d->worker247.bindings[index][i],
                        d->worker247.context[index]);
    }
    GLenum error=glGetError();
    if (error) { d->worker247.error=error; return false; }
    GLsync fence=glFenceSync(GL_SYNC_GPU_COMMANDS_COMPLETE,0);
    if (!fence) { return false; }
    worker247_trace(74,index,100000000,0);
    GLenum result=glClientWaitSync(fence,GL_SYNC_FLUSH_COMMANDS_BIT,100000000);
    glDeleteSync(fence); /* Only the newly-created diagnostic fence. */
    d->worker247.fence[index]=result;
    error=glGetError();d->worker247.error=error;
    worker247_trace(75,index,result,error);
    return !error && (result==GL_ALREADY_SIGNALED ||
                     result==GL_CONDITION_SATISFIED) && worker247_alive(d);
}

/* Called solely by PFIFO worker with FIFO lock, before pending/pusher/reports. */
bool pgraph_gl_worker247(NV2AState *d)
{
    if (qatomic_load_acquire(&d->worker247.state)!=1) { return false; }
    if (qatomic_cmpxchg(&d->worker247.state,1,2)!=1) { return false; }
    PGRAPHState *pg=&d->pgraph;PGRAPHGLState *r=pg->gl_renderer_state;
    unsigned reason=0;
    d->worker247.thread=qemu_get_thread_id();
    d->worker247.when=qemu_clock_get_ns(QEMU_CLOCK_REALTIME);
    worker247_trace(71,0,2,0);
    bool renderer=!qemu_mutex_trylock(&pg->renderer_lock);
    bool graph=renderer && !qemu_mutex_trylock(&pg->lock);
    if (!renderer || !graph) { reason=1; }
    else if (!worker247_alive(d) || !r || bql_locked() ||
             !d->pfifo.halt || pg->framebuffer_in_use) { reason=2; }
    else if (d->pfifo.regs[NV_PFIFO_CACHE1_DMA_GET]!=
             d->pfifo.regs[NV_PFIFO_CACHE1_DMA_PUT] ||
             (d->pfifo.regs[NV_PFIFO_CACHE1_DMA_STATE] &
              (NV_PFIFO_CACHE1_DMA_STATE_METHOD_COUNT|NV_PFIFO_CACHE1_DMA_STATE_ERROR)) ||
             pg->primitive_mode!=PRIM_TYPE_INVALID || pg->draw_arrays_length ||
             pg->inline_array_length || pg->inline_elements_length ||
             pg->inline_buffer_length || pg->waiting_for_nop ||
             pg->waiting_for_flip || pg->waiting_for_context_switch ||
             pg->renderer_switch_phase!=PGRAPH_RENDERER_SWITCH_PHASE_IDLE ||
             qatomic_read(&pg->flush_pending) || qatomic_read(&pg->sync_pending) ||
             qatomic_read(&r->downloads_pending) ||
             qatomic_read(&r->download_dirty_surfaces_pending) ||
             qatomic_read(&r->shader_cache_writeback_pending)) { reason=3; }
    if (graph && r) {
        SurfaceBinding *s;
        QTAILQ_FOREACH(s,&r->surfaces,entry) {
            if (d->worker247.count==128) { reason=4;break; }
            unsigned n=d->worker247.count++;
            uint64_t flags=(s->draw_dirty?1:0)|(s->download_pending?2:0)|
                (s->cpu_write_evict_pending?4:0)|(s->upload_pending?8:0);
            uint64_t values[6]={(uint64_t)(uintptr_t)s,s->vram_addr,s->size,
                               s->gl_buffer,flags,s->access_cb!=NULL};
            memcpy(d->worker247.surfaces[n],values,sizeof(values));
            worker247_trace(76,values[0],values[1],values[2]);
            worker247_trace(77,values[0],values[3],flags);
            if (flags) { d->worker247.dirty++;if (!reason) {reason=5;} }
        }
    }
    if (graph) {qemu_mutex_unlock(&pg->lock);}
    if (renderer) {qemu_mutex_unlock(&pg->renderer_lock);}
    qemu_mutex_unlock(&d->pfifo.lock);
    /* No renderer/PG/FIFO/BQL ownership spans either finite GL fence wait. */
    if (!reason && !worker247_context(d,0,g_nv2a_context_render)) { reason=6; }
    if (!reason && !worker247_context(d,1,g_nv2a_context_display)) { reason=7; }
    glo_set_current(g_nv2a_context_render);
    qemu_mutex_lock(&d->pfifo.lock);
    d->worker247.reason=reason;
    qatomic_store_release(&d->worker247.ready,true);
    if (!reason && worker247_alive(d)) {
        qatomic_store_release(&d->worker247.state,3);
        worker247_trace(78,0,3,0);
        while (worker247_alive(d)) {
            /* Releases FIFO throughout the bounded park; no other locks held. */
            qemu_cond_timedwait(&d->pfifo.fifo_cond,&d->pfifo.lock,20);
        }
    }
    bool explicit_release=qatomic_load_acquire(&d->worker247.release);
    qatomic_set(&d->pfifo.halt,d->worker247.old_halt);
    qatomic_store_release(&d->worker247.state,
                         !reason && explicit_release ? 5 : 6);
    worker247_trace(80,0,qatomic_read(&d->worker247.state),reason);
    return true; /* Skip pending/pusher/reports for this iteration, even refusal. */
}
