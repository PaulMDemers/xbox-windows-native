/*265 One immutable observation request. Reuses the proven CPU-exclusive audit
 * mechanism but never starts a260 renderer-pattern slot or disposes an object.
 */
typedef struct X265State {
    X260Slot boundary;
    X265Rows ledger;
    X265Binding bindings[X265_BINDINGS];
    unsigned binding_count,accounting_error,page;
    unsigned shader_jobs_unknown;
} X265State;

static bool x265_binding(X265State *s,TextureBinding *binding,bool unit)
{
    if (!binding) return false;
    unsigned i=0;
    while (i<s->binding_count && s->bindings[i].identity!=(uintptr_t)binding) i++;
    if (i==s->binding_count) {
        if (i==X265_BINDINGS) return false;
        s->bindings[i]=(X265Binding){(uintptr_t)binding,binding->refcnt,0,0};
        s->binding_count++;
        if (!x265_add(&s->ledger,4,(uintptr_t)binding,binding->refcnt,
                binding->gl_texture,binding->gl_target,binding->draw_time,
                binding->scale,binding->data_hash)) return false;
    }
    if (binding->refcnt!=s->bindings[i].refs) return false;
    if (unit) s->bindings[i].unit_edges++; else s->bindings[i].cache_edges++;
    return true;
}

static bool x265_collect(NV2AState *d,X265State *s)
{
    PGRAPHState *pg=&d->pgraph; PGRAPHGLState *r=pg->gl_renderer_state;
    X265Rows *out=&s->ledger;
    unsigned walked=0,used=0;
    SurfaceBinding *surface;
    QTAILQ_FOREACH(surface,&r->surfaces,entry) {
        if (++walked>128) return false;
        unsigned flags=(surface->draw_dirty?1:0)|(surface->download_pending?2:0)|
            (surface->cpu_write_evict_pending?4:0)|(surface->upload_pending?8:0);
        if (!x265_add(out,1,(uintptr_t)surface,surface->vram_addr,surface->size,
                surface->gl_buffer,(uintptr_t)surface->access_cb,flags,
                (surface==r->color_binding?1:0)|(surface==r->zeta_binding?2:0))) return false;
    }
    LruNode *node; walked=0;
    QTAILQ_FOREACH(node,&r->texture_cache.global,next_global) {
        if (++walked>512) return false;
        if (!lru_is_node_in_use(&r->texture_cache,node)) continue;
        used++; TextureLruNode *t=container_of(node,TextureLruNode,node);
        if (!x265_binding(s,t->binding,false) ||
            !x265_add(out,2,(uintptr_t)t,(uintptr_t)t->binding,t->key.texture_vram_offset,
                t->key.texture_length,t->key.palette_vram_offset,t->key.palette_length,t->possibly_dirty)) return false;
    }
    if (r->texture_cache.num_used<0 || used!=(unsigned)r->texture_cache.num_used) return false;
    for (unsigned i=0;i<NV2A_MAX_TEXTURES;i++) {
        TextureBinding *t=r->texture_binding[i];
        if (t && !x265_binding(s,t,true)) return false;
        if (!x265_add(out,3,i,(uintptr_t)t,pgraph_is_texture_enabled(pg,i),pg->texture_dirty[i],0,0,0)) return false;
    }
    s->accounting_error=x265_account(s->bindings,s->binding_count);
    /* A discrepant reference count is evidence, not permission to free it. */
    for (unsigned i=0;i<s->binding_count;i++) {
        X265Binding *b=&s->bindings[i];
        if (!x265_add(out,5,b->identity,b->refs,b->cache_edges,b->unit_edges,0,0,0)) return false;
    }
    if (!r->element_cache_entries) return false;
    used=0;
    for (unsigned i=0;i<51200;i++) {
        if (!(i%256) && !x260_alive(d,&s->boundary)) return false;
        VertexLruNode *t=&r->element_cache_entries[i];
        bool live=lru_is_node_in_use(&r->element_cache,&t->node); used+=live;
        /* Free-node key/initialized bytes were never initialized: do not read. */
        if (!x265_add(out,6,(uintptr_t)t,t->gl_buffer,live,
            live?t->initialized:0,live?t->key.addr:0,live?t->key.count:0,live?t->key.stride:0)) return false;
    }
    if (r->element_cache.num_used<0 || used!=(unsigned)r->element_cache.num_used) return false;
    GLuint fixed[]={r->gl_framebuffer,r->gl_display_buffer,r->gl_inline_array_buffer,
        r->gl_memory_buffer,r->gl_vertex_array,r->s2t_rndr.fbo,r->s2t_rndr.vao,
        r->s2t_rndr.vbo,r->s2t_rndr.prog,r->disp_rndr.fbo,r->disp_rndr.vao,
        r->disp_rndr.vbo,r->disp_rndr.prog,r->disp_rndr.pvideo_tex};
    for (unsigned i=0;i<G_N_ELEMENTS(fixed);i++)
        if (!x265_add(out,7,i,fixed[i],0,0,0,0,0)) return false;
    for (unsigned i=0;i<NV2A_VERTEXSHADER_ATTRIBUTES;i++)
        if (!x265_add(out,8,i,r->gl_inline_buffer[i],0,0,0,0,0)) return false;
    /* Shader lock excludes the actual background cache loader. A thread handle
     * is reported as UNKNOWN completion, never interpreted as joined/finished. */
    if (qemu_mutex_trylock(&r->shader_cache_lock)) return false;
    bool okay=true; walked=used=0;
    QTAILQ_FOREACH(node,&r->shader_cache.global,next_global) {
        if (++walked>51200 || !x260_alive(d,&s->boundary)) {okay=false;break;}
        if (!lru_is_node_in_use(&r->shader_cache,node)) continue;
        used++; ShaderBinding *b=container_of(node,ShaderBinding,node);
        if (b->save_thread) s->shader_jobs_unknown++;
        if (!x265_add(out,9,(uintptr_t)b,b->initialized,
                b->initialized?b->gl_program:0,
                b->save_thread?0:(uintptr_t)b->program,
                (!b->save_thread && b->program)?b->program_size:0,
                (uintptr_t)b->save_thread,b==r->shader_binding)) {okay=false;break;}
    }
    okay &= r->shader_cache.num_used>=0 && used==(unsigned)r->shader_cache.num_used;
    if (!x265_add(out,10,(uintptr_t)r->shader_binding,
            (uintptr_t)&r->shader_disk_thread,1,0,0,0,0)) okay=false;
    /* Loader completion is not instrumented in this read-only diagnostic. */
    s->shader_jobs_unknown++;
    qemu_mutex_unlock(&r->shader_cache_lock);
    if (!okay) return false;
    walked=used=0;
    QTAILQ_FOREACH(node,&r->shader_module_cache.global,next_global) {
        if (++walked>51200 || !x260_alive(d,&s->boundary)) return false;
        if (!lru_is_node_in_use(&r->shader_module_cache,node)) continue;
        used++; ShaderModuleCacheEntry *m=container_of(node,ShaderModuleCacheEntry,node);
        if (!x265_add(out,11,(uintptr_t)m,m->gl_shader,m->key.kind,0,0,0,0)) return false;
    }
    if (r->shader_module_cache.num_used<0 || used!=(unsigned)r->shader_module_cache.num_used) return false;
    QueryReport *q; walked=used=0;
    QSIMPLEQ_FOREACH(q,&r->report_queue,entry) {
        if (++walked>128) return false;
        /* clear-only reports do not initialize their other fields. */
        unsigned count=q->clear?0:q->query_count;
        if (count>4096-used || (count && !q->queries)) return false;
        if (!x265_add(out,12,(uintptr_t)q,q->clear,q->clear?0:q->parameter,count,0,0,0)) return false;
        for (unsigned i=0;i<count;i++) if (!x265_add(out,13,(uintptr_t)q,i,q->queries[i],0,0,0,0)) return false;
        used+=count;
    }
    if (r->gl_zpass_pixel_count_query_count>4096-used ||
        (r->gl_zpass_pixel_count_query_count && !r->gl_zpass_pixel_count_queries)) return false;
    for (unsigned i=0;i<r->gl_zpass_pixel_count_query_count;i++)
        if (!x265_add(out,14,i,r->gl_zpass_pixel_count_queries[i],0,0,0,0,0)) return false;
    if (!x265_add(out,15,d->pcrtc.start,memory_region_size(d->vram),
        d->pvideo.regs[NV_PVIDEO_BUFFER],d->pvideo.regs[NV_PVIDEO_BASE],
        d->pvideo.regs[NV_PVIDEO_OFFSET],d->pvideo.regs[NV_PVIDEO_SIZE_IN],
        pg->framebuffer_in_use)) return false;
    if (!x265_add(out,16,pg->primitive_mode,pg->draw_arrays_length,
        pg->inline_array_length,pg->inline_elements_length,pg->inline_buffer_length,
        s->boundary.pending_mask,0)) return false;
    if (!x265_add(out,18,d->pfifo.regs[NV_PFIFO_CACHE1_DMA_GET],
        d->pfifo.regs[NV_PFIFO_CACHE1_DMA_PUT],d->pfifo.regs[NV_PFIFO_CACHE1_DMA_STATE],
        d->pfifo.halt,0,0,0)) return false;
    return !out->overflow;
}

bool pgraph_gl_ledger265_worker(NV2AState *d)
{
    X265State *s=qatomic_load_acquire(&d->ledger265);
    if (!s || qatomic_cmpxchg(&s->boundary.state,1,2)!=1) return false;
    X260Slot *v=&s->boundary; PGRAPHState *pg=&d->pgraph;
    PGRAPHGLState *r=pg->gl_renderer_state;
    unsigned reason=0; bool locked=false;
    v->worker_thread=qemu_get_thread_id();
    if (!r || !x260_alive(d,v) || bql_locked() || pg->framebuffer_in_use) {reason=1;goto finish;}
    if (!x260_cpu_boundary(d,v,0)) {reason=2;goto finish;}
    qemu_mutex_unlock(&d->pfifo.lock);
    bool render=x260_context_fence(d,v,g_nv2a_context_render);
    bool display=render && x260_context_fence(d,v,g_nv2a_context_display);
    glo_set_current(g_nv2a_context_render);
    qemu_mutex_lock(&d->pfifo.lock);
    if (!render || !display) {reason=3;goto finish;}
    if (qemu_mutex_trylock(&pg->renderer_lock)) {reason=4;goto finish;}
    if (qemu_mutex_trylock(&pg->lock)) {qemu_mutex_unlock(&pg->renderer_lock);reason=5;goto finish;}
    locked=true;
    v->pending_mask=x263_pending_mask(pg->waiting_for_nop,pg->waiting_for_flip,
        pg->waiting_for_context_switch,pg->renderer_switch_phase!=PGRAPH_RENDERER_SWITCH_PHASE_IDLE,
        qatomic_read(&pg->flush_pending),qatomic_read(&pg->sync_pending),
        qatomic_read(&r->downloads_pending),qatomic_read(&r->download_dirty_surfaces_pending),
        qatomic_read(&r->shader_cache_writeback_pending));
    if (v->pending_mask) {reason=6;goto finish;}
    if (!x265_collect(d,s)) {reason=7;goto finish;}
    if (!x265_context(&s->ledger,1,v->deadline)) {reason=8;goto finish;}
    glo_set_current(g_nv2a_context_display);
    bool context_ok=x265_context(&s->ledger,2,v->deadline);
    glo_set_current(g_nv2a_context_render);
    if (!context_ok) {reason=9;goto finish;}
    qemu_mutex_unlock(&pg->lock);qemu_mutex_unlock(&pg->renderer_lock);locked=false;
    if (!x260_cpu_boundary(d,v,1)) {reason=10;goto finish;}
    if (v->cpu[0].count!=v->cpu[1].count ||
        memcmp(v->cpu[0].rows,v->cpu[1].rows,v->cpu[0].count*sizeof(v->cpu[0].rows[0]))) {reason=11;goto finish;}
    for (unsigned phase=0;phase<2;phase++) for (unsigned i=0;i<v->cpu[phase].count;i++) {
        uint64_t *row=v->cpu[phase].rows[i];
        if (!x265_add(&s->ledger,17,phase,row[0],row[1],row[2],row[3],v->cpu[phase].thread,v->cpu[phase].epoch)) reason=12;
    }
finish:
    if (locked) {qemu_mutex_unlock(&pg->lock);qemu_mutex_unlock(&pg->renderer_lock);}
    if (!x260_alive(d,v) && !reason) reason=13;
    v->reason=reason;v->finished=qemu_clock_get_ns(QEMU_CLOCK_REALTIME);
    /* Read-only capture. Failure is quarantined, never a disposal/ownership grant. */
    if (!reason) qatomic_set(&d->pfifo.halt,v->old_halt);
    qatomic_store_release(&v->state,reason?6:5);
    return true;
}

void pgraph_gl_ledger265_request(NV2AState *d,const char *value,Error **errp)
{
    if (strcmp(value,"capture,1") || runstate_is_running() || !xwn_frontend246_closed() ||
        !d->pgraph.renderer || d->pgraph.renderer->type!=CONFIG_DISPLAY_RENDERER_OPENGL ||
        qatomic_load_acquire(&d->ledger265) || qatomic_load_acquire(&d->pattern260) ||
        qatomic_load_acquire(&d->worker247.state) || qatomic_load_acquire(&d->preserve227.state)) {
        error_setg(errp,"265 requires fresh stopped CPU, closed UI, OpenGL and unused actors");return;
    }
    if (qemu_mutex_trylock(&d->pfifo.lock)) {error_setg(errp,"265 FIFO busy; not accepted");return;}
    X265State *s=g_new0(X265State,1);X260Slot *v=&s->boundary;
    s->ledger.rows=g_malloc0_n(X265_ROWS,sizeof(*s->ledger.rows));s->ledger.capacity=X265_ROWS;
    v->stage=1;v->started=qemu_clock_get_ns(QEMU_CLOCK_REALTIME);v->deadline=v->started+10000000000LL;
    v->old_halt=qatomic_read(&d->pfifo.halt);qatomic_set(&d->pfifo.halt,true);
    qatomic_store_release(&v->state,1);qatomic_store_release(&d->ledger265,s);
    qemu_cond_broadcast(&d->pfifo.fifo_cond);qemu_mutex_unlock(&d->pfifo.lock);
}
void pgraph_gl_ledger265_page(NV2AState *d,const char *value,Error **errp)
{
    X265State *s=qatomic_load_acquire(&d->ledger265);uint64_t page=0;const char *end=NULL;
    unsigned state=s?qatomic_load_acquire(&s->boundary.state):0;
    if (!s || (state!=5 && state!=6) || qemu_strtou64(value,&end,10,&page) || !end || *end ||
        page>=x265_page_count(s->ledger.count)) {error_setg(errp,"265 invalid immutable page");return;}
    s->page=page; /* Monitor-only read cursor, not an actor epoch reset. */
}
char *pgraph_gl_ledger265_report(NV2AState *d)
{
    X265State *s=qatomic_load_acquire(&d->ledger265);if (!s) return g_strdup("version=265 state=0");
    unsigned state=qatomic_load_acquire(&s->boundary.state);
    if (state!=5 && state!=6) return g_strdup_printf("version=265 state=%u",state);
    X260Slot *v=&s->boundary;
    unsigned cpu0=qatomic_load_acquire(&v->cpu[0].done);
    unsigned cpu1=qatomic_load_acquire(&v->cpu[1].done);
    return g_strdup_printf("version=265 state=%u reason=%u rows=%u overflow=%u pages=%u bindings=%u accounting=%u shader_jobs_unknown=%u worker=%"PRIu64" started=%"PRIu64" finished=%"PRIu64" cpu0_done=%u cpu0_reason=%u cpu1_done=%u cpu1_reason=%u pending=%u native_grant=0 retirement=0",
        state,v->reason,s->ledger.count,s->ledger.overflow,x265_page_count(s->ledger.count),
        s->binding_count,s->accounting_error,s->shader_jobs_unknown,v->worker_thread,
        v->started,v->finished,cpu0,cpu0?v->cpu[0].reason:UINT_MAX,
        cpu1,cpu1?v->cpu[1].reason:UINT_MAX,v->pending_mask);
}
char *pgraph_gl_ledger265_data(NV2AState *d)
{
    X265State *s=qatomic_load_acquire(&d->ledger265);
    unsigned state=s?qatomic_load_acquire(&s->boundary.state):0;
    if (state!=5 && state!=6) return g_strdup("version=265 unavailable=1");
    return x265_rows_page(&s->ledger,s->page,1);
}
