/*280 Actual capture path derived from278; three real stages, no slot reuse. */
static bool x280_capture(NV2AState *d,X280Transaction *tx,X265State *s,unsigned stage)
{
    X265State *initial=tx->pre;X260Slot *v=&s->boundary;bool ending=stage>1;
    if(stage<1 || stage>3 || qatomic_cmpxchg(&v->state,0,2)!=0)return false;
    v->stage=stage;v->started=qemu_clock_get_ns(QEMU_CLOCK_REALTIME);v->deadline=v->started+10000000000LL;
    PGRAPHState *pg=&d->pgraph;PGRAPHGLState *r=pg->gl_renderer_state;
    unsigned reason=0;bool locked=false,published=false;s->admission278=UINT_MAX;
    v->worker_thread=qemu_get_thread_id();
    if(!r || !x260_alive(d,v) || bql_locked() || pg->framebuffer_in_use){reason=1;goto finish;}
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
    if(!x265_collect(d,s) || !x280_graph(d,tx,s,0)){reason=7;goto finish;}
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
    if(!x278_quiescent(d,initial,s,ending) || !x280_graph(d,tx,s,1)){reason=28;goto finish;}
    if(!x280_validate_actual(d,tx,s)){reason=29;goto finish;}
    uintptr_t actual[4];
    if(!glo_context_observe267(g_nv2a_context_render,actual) || actual[0]!=s->proof278.render_context){reason=25;goto finish;}
    if(ending && !x274_context_match(initial,s)){reason=21;goto finish;}
    published=true;
    if(!x280_scalar_publish(s,reason)){reason=12;goto finish;}
    if(!x260_alive(d,v)){reason=13;goto finish;}
    v->reason=0;v->finished=qemu_clock_get_ns(QEMU_CLOCK_REALTIME);
    qatomic_store_release(&v->state,5);return true; /* Caller still owns renderer/PG locks. */
finish:
    if(locked){qemu_mutex_unlock(&pg->lock);qemu_mutex_unlock(&pg->renderer_lock);}
    if(!published)x280_scalar_publish(s,reason);
    v->reason=reason;v->finished=qemu_clock_get_ns(QEMU_CLOCK_REALTIME);
    qatomic_store_release(&v->state,6);return false;
}
