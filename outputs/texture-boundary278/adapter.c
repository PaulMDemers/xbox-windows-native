/*278 Opt-in adapter. Called only by the actual PFIFO worker under renderer/PG
 * locks. It follows current live objects, never acknowledged callback pointers. */
static bool x278_parse(const char *text,uint64_t allocations[4])
{
    if(strncmp(text,"textures278,",12) || strlen(text)>100) return false;
    const char *p=text+12;
    for(unsigned i=0;i<4;i++) {
        const char *end=NULL;
        if(*p<'0' || *p>'9' || (*p=='0' && p[1]>='0' && p[1]<='9') ||
           qemu_strtou64(p,&end,10,&allocations[i]) || !end ||
           (i==3?*end!=0:*end!=',')) return false;
        if((allocations[i]&4095) || allocations[i]>UINT64_C(67108864)-4096) return false;
        for(unsigned j=0;j<i;j++) if(allocations[j]==allocations[i]) return false;
        p=end+(i!=3);
    }
    return true;
}
static void x278_cpu_copy(X265State *s,unsigned phase)
{
    X260CPU *a=&s->boundary.cpu[phase];X277CPU *c=&s->proof278.cpu[phase];
    if(!qatomic_load_acquire(&a->done)) return;
    c->done=a->done;c->error=a->reason;c->epoch=a->epoch;c->thread=a->thread;c->when=a->when;
    c->clock=a->clock278;c->clock_error=a->clock_error278;c->count=a->count;
    for(unsigned i=0;i<a->count && i<X277_MAX;i++) {
        uint64_t *r=a->rows[i],*e=a->detail276[i];
        c->callbacks[i]=(X277Callback){r[0],r[1],r[2],r[3],e[0],e[1],e[2]};
    }
}
static bool x278_graph(NV2AState *d,X265State *s,unsigned phase)
{
    X277Proof *p=&s->proof278;X277Graph *g=&p->graph[phase];
    PGRAPHState *pg=&d->pgraph;PGRAPHGLState *r=pg->gl_renderer_state;
    if(g->complete || g->count) return false;
    SurfaceBinding *surface;
    QTAILQ_FOREACH(surface,&r->surfaces,entry) {
        if(g->count==X277_MAX){g->error=1;return false;}
        g->surfaces[g->count++]=(X277Surface){(uintptr_t)surface,(uintptr_t)surface->access_cb,
            surface->vram_addr,surface->size,surface->gl_buffer,
            (surface->draw_dirty?1:0)|(surface->download_pending?2:0)|(surface->cpu_write_evict_pending?4:0)|(surface->upload_pending?8:0),
            (surface==r->color_binding?1:0)|(surface==r->zeta_binding?2:0)};
    }
    for(unsigned i=0;i<4;i++) {
        TextureBinding *b=r->texture_binding[i];if(!b)return false;
        TextureLruNode *found=NULL;unsigned walked=0,edges=0;LruNode *node;
        QTAILQ_FOREACH(node,&r->texture_cache.global,next_global) {
            if(++walked>512)return false;
            if(!lru_is_node_in_use(&r->texture_cache,node))continue;
            TextureLruNode *t=container_of(node,TextureLruNode,node);
            if(t->binding==b){found=t;edges++;}
        }
        if(edges!=1 || !found || b->gl_target!=GL_TEXTURE_2D)return false;
        unsigned units=0;
        for(unsigned j=0;j<4;j++)units+=r->texture_binding[j]==b;
        X277Texture t={(uintptr_t)b,b->gl_texture,s->allocations278[i],4096,
            found->key.texture_vram_offset,found->key.texture_length,
            found->key.palette_vram_offset,found->key.palette_length,b->refcnt,edges,units};
        if(phase && memcmp(&t,&p->textures[i],sizeof(t)))return false;
        if(!phase)p->textures[i]=t;
    }
    g->complete=1;return true;
}
static bool x278_quiescent(NV2AState *d,X265State *initial,X265State *s,bool ending)
{
    PGRAPHState *pg=&d->pgraph;PGRAPHGLState *r=pg->gl_renderer_state;
    X260Slot *v=&s->boundary;
    if(!x260_alive(d,v) || !qatomic_read(&d->pfifo.halt) || pg->framebuffer_in_use ||
       d->pfifo.regs[NV_PFIFO_CACHE1_DMA_GET]!=d->pfifo.regs[NV_PFIFO_CACHE1_DMA_PUT] ||
       (d->pfifo.regs[NV_PFIFO_CACHE1_DMA_STATE]&
       (NV_PFIFO_CACHE1_DMA_STATE_METHOD_COUNT|NV_PFIFO_CACHE1_DMA_STATE_ERROR)) ||
       x274_pending(d) || pg->primitive_mode!=PRIM_TYPE_INVALID || pg->draw_arrays_length ||
       pg->inline_array_length || pg->inline_elements_length || pg->inline_buffer_length ||
       !QSIMPLEQ_EMPTY(&r->report_queue) || r->gl_zpass_pixel_count_query_count) return false;
    if(ending && (initial->boundary.worker_thread!=v->worker_thread ||
       !pgraph_gl_reuse274_ready(initial->boundary.worker_thread))) return false;
    return true;
}
static bool x278_validate(NV2AState *d,X265State *s)
{
    X277Proof *p=&s->proof278;X260Slot *v=&s->boundary;
    p->stage=v->stage;p->worker=v->worker_thread;p->device=(uintptr_t)d;p->region=(uintptr_t)d->vram;
    p->function=p->cpu[0].count?p->cpu[0].callbacks[0].function:0;
    p->ram_base=memory_region_get_ram_addr(d->vram);p->ram_bytes=memory_region_size(d->vram);
    p->started=v->started;p->finished=qemu_clock_get_ns(QEMU_CLOCK_REALTIME);p->deadline=v->deadline;
    p->cpu_stopped=qatomic_read(&qemu_get_cpu(0)->stopped);p->frontend_closed=xwn_frontend246_closed();
    p->pfifo_halted=qatomic_read(&d->pfifo.halt);p->render_fenced=v->admission.render_fenced;
    p->display_fenced=v->admission.display_fenced;p->pending=x274_pending(d);
    p->get_equals_put=d->pfifo.regs[NV_PFIFO_CACHE1_DMA_GET]==d->pfifo.regs[NV_PFIFO_CACHE1_DMA_PUT];
    p->method_error=d->pfifo.regs[NV_PFIFO_CACHE1_DMA_STATE]&
        (NV_PFIFO_CACHE1_DMA_STATE_METHOD_COUNT|NV_PFIFO_CACHE1_DMA_STATE_ERROR);
    p->unknown_owners=s->accounting_error || s->shader_jobs_unknown;
    unsigned contexts=0;
    for(unsigned i=0;i<s->ledger.count;i++) {
        uint64_t *row=s->ledger.rows[i];if(row[0]!=51)continue;
        if(row[1]<1 || row[1]>2 || !row[7] || row[3]!=row[4] || row[5]!=row[6] ||
           (contexts&(1u<<row[1])))return false;
        contexts|=1u<<row[1];
        if(row[1]==1)p->render_context=row[3];else p->display_context=row[3];
    }
    if(contexts!=6)return false;
    s->admission278=x277_validate(p);return s->admission278==X277_OK;
}
/* Bounded immutable transport; rows carry actual tuples even on refusal. */
static bool x278_publish(X265State *s)
{
    X277Proof *p=&s->proof278;X265Rows *o=&s->ledger;
    x278_cpu_copy(s,0);x278_cpu_copy(s,1);
    bool ok=x265_add(o,64,s->boundary.stage,s->admission278,p->cpu[0].clock,p->cpu[1].clock,
        p->cpu[0].clock_error,p->cpu[1].clock_error,1);
    ok &= x265_add(o,69,p->stage,p->ram_base,p->ram_bytes,p->device,p->region,p->function,s->admission278);
    for(unsigned phase=0;phase<2;phase++) {
        X277CPU *c=&p->cpu[phase];X277Graph *g=&p->graph[phase];
        ok &= x265_add(o,70,phase,c->done,c->error,c->count,g->complete,g->error,g->count);
        for(unsigned i=0;i<c->count && i<X277_MAX;i++) {
            X277Callback *b=&c->callbacks[i];
            ok &= x265_add(o,17,phase,b->identity,b->begin,b->bytes,b->opaque,c->thread,c->epoch);
            ok &= x265_add(o,65,phase,b->identity,b->function,b->region,b->absolute,0,0);
        }
        for(unsigned i=0;i<g->count && i<X277_MAX;i++) {
            X277Surface *b=&g->surfaces[i];
            ok &= x265_add(o,66,phase,b->identity,b->callback,b->begin,b->bytes,b->name,b->flags|(b->roles<<8));
        }
    }
    for(unsigned i=0;i<4;i++) {
        X277Texture *t=&p->textures[i];
        ok &= x265_add(o,67,i,t->identity,t->name,t->allocation,t->allocation_bytes,t->source,t->source_bytes);
        ok &= x265_add(o,68,i,t->palette,t->palette_bytes,t->refs,t->cache_edges,t->unit_edges,0);
    }
    return ok;
}
static bool x278_worker(NV2AState *d)
{
    X265State *initial=qatomic_load_acquire(&d->ledger265);
    X265State *end=qatomic_load_acquire(&initial->end274);
    bool ending=end!=NULL;X265State *s=ending?end:initial;X260Slot *v=&s->boundary;
    if(qatomic_cmpxchg(&v->state,1,2)!=1)return false;
    PGRAPHState *pg=&d->pgraph;PGRAPHGLState *r=pg->gl_renderer_state;
    unsigned reason=0;bool locked=false;s->admission278=UINT_MAX;
    v->worker_thread=qemu_get_thread_id();
    if(!r || !s->textures278 || !x260_alive(d,v) || bql_locked() || pg->framebuffer_in_use){reason=1;goto finish;}
    if(!x260_cpu_boundary(d,v,0)){reason=2;goto finish;}
    x278_cpu_copy(s,0);
    qemu_mutex_unlock(&d->pfifo.lock);
    bool render=x260_context_fence(d,v,g_nv2a_context_render);
    bool display=render && x260_context_fence(d,v,g_nv2a_context_display);
    glo_set_current(g_nv2a_context_render);qemu_mutex_lock(&d->pfifo.lock);
    if(!render || !display){reason=3;goto finish;}
    v->admission.render_fenced=render;v->admission.display_fenced=display;
    if(qemu_mutex_trylock(&pg->renderer_lock)){reason=4;goto finish;}
    if(qemu_mutex_trylock(&pg->lock)){qemu_mutex_unlock(&pg->renderer_lock);reason=5;goto finish;}
    locked=true;v->pending_mask=x274_pending(d);
    if(!x278_quiescent(d,initial,s,ending)){reason=6;goto finish;}
    if(!x265_collect(d,s) || !x278_graph(d,s,0)){reason=7;goto finish;}
    if(s->accounting_error || s->shader_jobs_unknown){reason=14;goto finish;}
    if(!x265_context(&s->ledger,1,v->deadline) || !x267_context(&s->ledger,r,1,v->deadline)){reason=8;goto finish;}
    glo_set_current(g_nv2a_context_display);
    bool context_ok=x265_context(&s->ledger,2,v->deadline) && x267_context(&s->ledger,r,2,v->deadline);
    glo_set_current(g_nv2a_context_render);
    if(!context_ok){reason=9;goto finish;}
    qemu_mutex_unlock(&pg->lock);qemu_mutex_unlock(&pg->renderer_lock);locked=false;
    if(!x260_cpu_boundary(d,v,1)){reason=10;goto finish;}
    x278_cpu_copy(s,1);
    if(qemu_mutex_trylock(&pg->renderer_lock)){reason=22;goto finish;}
    if(qemu_mutex_trylock(&pg->lock)){qemu_mutex_unlock(&pg->renderer_lock);reason=23;goto finish;}
    locked=true;
    if(!x278_quiescent(d,initial,s,ending) || !x278_graph(d,s,1)){reason=28;goto finish;}
    if(!x278_validate(d,s)){reason=29;goto finish;}
    uintptr_t actual[4];
    if(!glo_context_observe267(g_nv2a_context_render,actual) || actual[0]!=s->proof278.render_context){reason=25;goto finish;}
    if(ending) {
        s->contexts274=x274_context_match(initial,s);
        if(!s->contexts274){reason=21;goto finish;}
    } else if(!pgraph_gl_reuse269_arm(d)){reason=30;goto finish;}
    qemu_mutex_unlock(&pg->lock);qemu_mutex_unlock(&pg->renderer_lock);locked=false;
    if(ending) {
        qemu_mutex_unlock(&d->pfifo.lock);s->seal274=pgraph_gl_reuse269_seal();qemu_mutex_lock(&d->pfifo.lock);
        if(!s->seal274 || pgraph_gl_reuse269_error())reason=26;
    }
finish:
    if(locked){qemu_mutex_unlock(&pg->lock);qemu_mutex_unlock(&pg->renderer_lock);}
    if(!x278_publish(s) && !reason)reason=12;
    if(!x260_alive(d,v) && !reason)reason=13;
    v->reason=reason;v->finished=qemu_clock_get_ns(QEMU_CLOCK_REALTIME);
    if(!reason)qatomic_set(&d->pfifo.halt,v->old_halt);
    qatomic_store_release(&v->state,reason?6:5);return true;
}
