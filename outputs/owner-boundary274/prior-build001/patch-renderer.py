"""New immutable end actor on exact273; no reset, disposal or guest writes."""
from pathlib import Path
k=Path(__file__).resolve().parent
def replace(s,a,b):
    assert s.count(a)==1,(a[:100],s.count(a))
    return s.replace(a,b)
def apply(root):
    header=root/'hw/xbox/nv2a/pgraph/gl/renderer.h'
    s=header.read_text();s+='\n/*274 Admission of an already armed observation on its original owner. */\nbool pgraph_gl_reuse274_ready(uint64_t owner);\n'
    header.write_text(s)
    texture=root/'hw/xbox/nv2a/pgraph/gl/texture.c'
    s=texture.read_text()
    anchor='unsigned pgraph_gl_reuse269_error(void) {'
    s=replace(s,anchor,'''bool pgraph_gl_reuse274_ready(uint64_t owner)
{
    return qatomic_load_acquire(&x269.enabled)==1 &&
        qatomic_load_acquire(&x269.busy)==0 && !qatomic_read(&x269.terminal) &&
        owner && owner==x269.thread && !pgraph_gl_reuse269_error();
}
'''+anchor)
    texture.write_text(s)
    file=root/'hw/xbox/nv2a/pgraph/gl/renderer.c';s=file.read_text()
    s=replace(s,'    unsigned shader_jobs_unknown;\n} X265State;', '''    unsigned shader_jobs_unknown;
    /*274 Separate never-reset end capture. Published once under FIFO lock. */
    struct X265State *end274;
    unsigned end_page274,contexts274,seal274;
} X265State;''')
    helper=(k/'boundary.h').read_text()+'''
static unsigned x274_pending(NV2AState *d)
{
    PGRAPHState *pg=&d->pgraph;PGRAPHGLState *r=pg->gl_renderer_state;
    return x263_pending_mask(pg->waiting_for_nop,pg->waiting_for_flip,
        pg->waiting_for_context_switch,pg->renderer_switch_phase!=PGRAPH_RENDERER_SWITCH_PHASE_IDLE,
        qatomic_read(&pg->flush_pending),qatomic_read(&pg->sync_pending),
        qatomic_read(&r->downloads_pending),qatomic_read(&r->download_dirty_surfaces_pending),
        qatomic_read(&r->shader_cache_writeback_pending));
}
/* Called by the actual worker with FIFO, renderer and PGRAPH locks held. */
static unsigned x274_check(NV2AState *d,X265State *initial,X265State *end,unsigned complete)
{
    X260Slot *v=&end->boundary;PGRAPHState *pg=&d->pgraph;PGRAPHGLState *r=pg->gl_renderer_state;
    X274Evidence e={
        .original_owner=initial->boundary.worker_thread,.actual_owner=v->worker_thread,
        .get=d->pfifo.regs[NV_PFIFO_CACHE1_DMA_GET],.put=d->pfifo.regs[NV_PFIFO_CACHE1_DMA_PUT],
        .method_error=d->pfifo.regs[NV_PFIFO_CACHE1_DMA_STATE]&
            (NV_PFIFO_CACHE1_DMA_STATE_METHOD_COUNT|NV_PFIFO_CACHE1_DMA_STATE_ERROR),
        .pending=x274_pending(d),.primitive=pg->primitive_mode!=PRIM_TYPE_INVALID,
        .draw=pg->draw_arrays_length,.inline_array=pg->inline_array_length,
        .inline_elements=pg->inline_elements_length,.inline_buffer=pg->inline_buffer_length,
        .reports=!QSIMPLEQ_EMPTY(&r->report_queue),.queries=r->gl_zpass_pixel_count_query_count,
        .ready=pgraph_gl_reuse274_ready(initial->boundary.worker_thread),
        .cpu0_done=qatomic_load_acquire(&v->cpu[0].done),.cpu1_done=qatomic_load_acquire(&v->cpu[1].done),
        .render_fenced=v->admission.render_fenced,.display_fenced=v->admission.display_fenced,
        .contexts_match=end->contexts274
    };
    if(e.cpu0_done){e.cpu0_reason=v->cpu[0].reason;e.cpu0_count=v->cpu[0].count;}
    if(e.cpu1_done){e.cpu1_reason=v->cpu[1].reason;e.cpu1_count=v->cpu[1].count;}
    return x274_admit(&e,complete);
}
static bool x274_context_match(X265State *initial,X265State *end)
{
    for(unsigned role=1;role<=2;role++) {
        const uint64_t *a=NULL,*b=NULL;unsigned an=0,bn=0;
        for(unsigned i=0;i<initial->ledger.count;i++) {
            const uint64_t *row=initial->ledger.rows[i];if(row[0]==51 && row[1]==role){a=row;an++;}
        }
        for(unsigned i=0;i<end->ledger.count;i++) {
            const uint64_t *row=end->ledger.rows[i];if(row[0]==51 && row[1]==role){b=row;bn++;}
        }
        if(an!=1 || bn!=1 || !a[7] || memcmp(a,b,8*sizeof(uint64_t))) return false;
    }
    return true;
}
'''
    s=replace(s,'bool pgraph_gl_ledger265_worker(NV2AState *d)\n{',helper+'\nbool pgraph_gl_ledger265_worker(NV2AState *d)\n{')
    s=replace(s,'''    X265State *s=qatomic_load_acquire(&d->ledger265);
    if (!s || qatomic_cmpxchg(&s->boundary.state,1,2)!=1) return false;''','''    X265State *initial=qatomic_load_acquire(&d->ledger265);
    if (!initial) return false;
    X265State *end=qatomic_load_acquire(&initial->end274);
    bool ending=end!=NULL;X265State *s=ending?end:initial;
    if (qatomic_cmpxchg(&s->boundary.state,1,2)!=1) return false;''')
    s=replace(s,'''    if (!render || !display) {reason=3;goto finish;}
    if (qemu_mutex_trylock(&pg->renderer_lock))''','''    if (!render || !display) {reason=3;goto finish;}
    v->admission.render_fenced=render;v->admission.display_fenced=display;
    if (qemu_mutex_trylock(&pg->renderer_lock))''')
    s=replace(s,'    if (v->pending_mask) {reason=6;goto finish;}\n    if (!x265_collect(d,s))', '''    if (v->pending_mask) {reason=6;goto finish;}
    if (ending && x274_check(d,initial,s,0)) {reason=20;goto finish;}
    if (!x265_collect(d,s))''')
    s=replace(s,'''    if (s->accounting_error || s->shader_jobs_unknown || v->cpu[0].count ||
        !pgraph_gl_reuse269_arm(d)) {reason=14;goto finish;}''','''    if (s->accounting_error || s->shader_jobs_unknown || v->cpu[0].count) {reason=14;goto finish;}
    if (ending) {
        s->contexts274=x274_context_match(initial,s);
        if (!s->contexts274) {reason=21;goto finish;}
    } else if (!pgraph_gl_reuse269_arm(d)) {reason=14;goto finish;}''')
    a='''finish:
    if (locked) {qemu_mutex_unlock(&pg->lock);qemu_mutex_unlock(&pg->renderer_lock);}
    if (!x260_alive(d,v) && !reason) reason=13;'''
    b='''    if (ending && !reason) {
        if (qemu_mutex_trylock(&pg->renderer_lock)) {reason=22;goto finish;}
        if (qemu_mutex_trylock(&pg->lock)) {qemu_mutex_unlock(&pg->renderer_lock);reason=23;goto finish;}
        locked=true;
        if (x274_check(d,initial,s,1)) {reason=24;goto finish;}
        uintptr_t actual[4];
        if (!glo_context_observe267(g_nv2a_context_render,actual)) {reason=25;goto finish;}
        qemu_mutex_unlock(&pg->lock);qemu_mutex_unlock(&pg->renderer_lock);locked=false;
        /* Exclusive observation publisher on the original worker. Host I/O has
         * the outer watchdog; never hold FIFO/renderer/PG locks across it. */
        qemu_mutex_unlock(&d->pfifo.lock);
        s->seal274=pgraph_gl_reuse269_seal();
        qemu_mutex_lock(&d->pfifo.lock);
        if (!s->seal274 || pgraph_gl_reuse269_error()) reason=26;
    }
finish:
    if (locked) {qemu_mutex_unlock(&pg->lock);qemu_mutex_unlock(&pg->renderer_lock);}
    if (!x260_alive(d,v) && !reason) reason=13;'''
    s=replace(s,a,b)
    a='''    /*269 One-way observation seal; does not reset any existing actor. */'''
    s=replace(s,a,'''    if (!strcmp(value,"finish274")) {
        X265State *initial=qatomic_load_acquire(&d->ledger265);
        if (runstate_is_running() || !xwn_frontend246_closed() || !initial ||
            qatomic_load_acquire(&initial->boundary.state)!=5 || qatomic_load_acquire(&initial->end274) ||
            !d->pgraph.renderer || d->pgraph.renderer->type!=CONFIG_DISPLAY_RENDERER_OPENGL ||
            !pgraph_gl_reuse274_ready(initial->boundary.worker_thread)) {
            error_setg(errp,"274 requires fresh end actor, stopped CPU, closed UI and armed observation");return;
        }
        /* Allocate before locking. Once published, this state and CPU job
         * metadata remain alive even on timeout, until owned process teardown. */
        X265State *end=g_new0(X265State,1);X260Slot *v=&end->boundary;
        end->ledger.rows=g_malloc0_n(X265_ROWS,sizeof(*end->ledger.rows));end->ledger.capacity=X265_ROWS;
        if (qemu_mutex_trylock(&d->pfifo.lock)) {
            g_free(end->ledger.rows);g_free(end);error_setg(errp,"274 FIFO busy; not accepted");return;
        }
        v->stage=2;v->started=qemu_clock_get_ns(QEMU_CLOCK_REALTIME);v->deadline=v->started+10000000000LL;
        v->old_halt=qatomic_read(&d->pfifo.halt);qatomic_set(&d->pfifo.halt,true);
        qatomic_store_release(&v->state,1);qatomic_store_release(&initial->end274,end);
        qemu_cond_broadcast(&d->pfifo.fifo_cond);qemu_mutex_unlock(&d->pfifo.lock);return;
    }
'''+a)
    # Prevent an old monitor-side seal racing the NEW terminal actor.
    s=replace(s,'''        if (runstate_is_running() || !s || qatomic_load_acquire(&s->boundary.state)!=5 ||
            !pgraph_gl_reuse269_seal())''','''        if (runstate_is_running() || !s || qatomic_load_acquire(&s->boundary.state)!=5 ||
            qatomic_load_acquire(&s->end274) || !pgraph_gl_reuse269_seal())''')
    # Explicit terminal read selection; initial pages remain immutable and available.
    s=replace(s,'''    X265State *s=qatomic_load_acquire(&d->ledger265);uint64_t page=0;const char *end=NULL;
    unsigned state=s?qatomic_load_acquire(&s->boundary.state):0;''','''    X265State *initial=qatomic_load_acquire(&d->ledger265);
    bool terminal=!strncmp(value,"end274,",7);if(terminal)value+=7;
    X265State *s=initial?(terminal?qatomic_load_acquire(&initial->end274):initial):NULL;
    uint64_t page=0;const char *end=NULL;
    unsigned state=s?qatomic_load_acquire(&s->boundary.state):0;''')
    s=replace(s,'''    s->page=page; /* Monitor-only read cursor, not an actor epoch reset. */''','''    s->page=page;initial->end_page274=terminal; /* Monitor-only cursor, never actor reset. */''')
    # Existing report now explicitly identifies which actor it reports.
    s=replace(s,'''    X265State *s=qatomic_load_acquire(&d->ledger265);if (!s) return g_strdup("version=265 state=0");
    unsigned state=qatomic_load_acquire(&s->boundary.state);
    if (state!=5 && state!=6) return g_strdup_printf("version=265 state=%u",state);''','''    X265State *initial=qatomic_load_acquire(&d->ledger265);if (!initial) return g_strdup("version=265 epoch=1 state=0");
    X265State *end=qatomic_load_acquire(&initial->end274);X265State *s=end?end:initial;
    unsigned epoch=end?2:1,state=qatomic_load_acquire(&s->boundary.state);
    if (state!=5 && state!=6) return g_strdup_printf("version=265 epoch=%u state=%u",epoch,state);''')
    s=replace(s,'return g_strdup_printf("version=265 state=%u reason=%u rows=', 'return g_strdup_printf("version=265 epoch=%u sealed=%u context_match=%u render_fenced=%u display_fenced=%u cpu0_count=%u cpu1_count=%u state=%u reason=%u rows=')
    s=replace(s,'        state,v->reason,s->ledger.count,s->ledger.overflow,x265_page_count(s->ledger.count),','''        epoch,s->seal274,s->contexts274,v->admission.render_fenced,v->admission.display_fenced,
        cpu0?v->cpu[0].count:UINT_MAX,cpu1?v->cpu[1].count:UINT_MAX,
        state,v->reason,s->ledger.count,s->ledger.overflow,x265_page_count(s->ledger.count),''')
    s=replace(s,'''    X265State *s=qatomic_load_acquire(&d->ledger265);
    unsigned state=s?qatomic_load_acquire(&s->boundary.state):0;
    if (state!=5 && state!=6) return g_strdup("version=265 unavailable=1");
    return x265_rows_page(&s->ledger,s->page,1);''','''    X265State *initial=qatomic_load_acquire(&d->ledger265);
    bool terminal=initial && initial->end_page274;
    X265State *s=initial?(terminal?qatomic_load_acquire(&initial->end274):initial):NULL;
    unsigned state=s?qatomic_load_acquire(&s->boundary.state):0;
    if (state!=5 && state!=6) return g_strdup("version=265 unavailable=1");
    return x265_rows_page(&s->ledger,s->page,terminal?2:1);''')
    file.write_text(s)
