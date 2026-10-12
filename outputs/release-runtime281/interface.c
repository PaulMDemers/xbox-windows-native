static bool x281_request(NV2AState *d,const char *value,Error **errp)
{
    X265State *initial=qatomic_load_acquire(&d->ledger265);
    X280Transaction *t=initial?initial->transaction280:NULL;
    bool control=!strncmp(value,"control281,",11),candidate=!strncmp(value,"candidate281,",13);
    bool finish=!strcmp(value,"finish281");
    if(!control&&!candidate&&!finish&&!t)return false;
    if(runstate_is_running() || !xwn_frontend246_closed() || qatomic_read(&d->exiting) ||
       !d->pgraph.renderer || d->pgraph.renderer->type!=CONFIG_DISPLAY_RENDERER_OPENGL) {
        error_setg(errp,"281 requires stopped guest and acknowledged closed frontend");return true;
    }
    if(finish) {
        if(!t || qatomic_load_acquire(&t->state)!=3 || !pgraph_gl_reuse274_ready(t->pre->boundary.worker_thread) ||
           qemu_mutex_trylock(&d->pfifo.lock)) {error_setg(errp,"281 end unavailable or FIFO busy");return true;}
        if(qatomic_load_acquire(&t->state)!=3 || qatomic_read(&d->pfifo.halt)!=t->old_halt) {
            qemu_mutex_unlock(&d->pfifo.lock);error_setg(errp,"281 stale end state");return true;
        }
        qatomic_set(&d->pfifo.halt,true);qatomic_store_release(&t->state,4);
        qemu_cond_broadcast(&d->pfifo.fifo_cond);qemu_mutex_unlock(&d->pfifo.lock);return true;
    }
    if(t || initial || (!control&&!candidate) || qatomic_load_acquire(&d->pattern260) ||
       qatomic_load_acquire(&d->worker247.state) || qatomic_load_acquire(&d->preserve227.state)) {
        error_setg(errp,"281 refuses reused actors and legacy actions on its transaction");return true;
    }
    char parsed[128];uint64_t allocations[4];
    if(strlen(value)>100){error_setg(errp,"281 request too long");return true;}
    snprintf(parsed,sizeof(parsed),"textures278,%s",value+(candidate?13:11));
    if(!x278_parse(parsed,allocations)){error_setg(errp,"281 invalid four allocation request");return true;}
    t=g_new0(X280Transaction,1);X265State *slots[3];
    for(unsigned i=0;i<3;i++) {
        slots[i]=g_new0(X265State,1);slots[i]->textures278=true;
        memcpy(slots[i]->allocations278,allocations,sizeof(allocations));
        slots[i]->ledger.rows=g_malloc0_n(X265_ROWS,sizeof(*slots[i]->ledger.rows));slots[i]->ledger.capacity=X265_ROWS;
    }
    t->pre=slots[0];t->post=slots[1];t->end=slots[2];t->candidate=candidate;t->page_stage=1;
    slots[0]->transaction280=t;
    if(qemu_mutex_trylock(&d->pfifo.lock)) {
        for(unsigned i=0;i<3;i++){g_free(slots[i]->ledger.rows);g_free(slots[i]);}g_free(t);
        error_setg(errp,"281 FIFO busy, request not accepted");return true;
    }
    if(qatomic_load_acquire(&d->ledger265)) {
        qemu_mutex_unlock(&d->pfifo.lock);
        for(unsigned i=0;i<3;i++){g_free(slots[i]->ledger.rows);g_free(slots[i]);}g_free(t);
        error_setg(errp,"281 initial actor appeared");return true;
    }
    t->old_halt=qatomic_read(&d->pfifo.halt);qatomic_set(&d->pfifo.halt,true);
    qatomic_store_release(&t->state,1);qatomic_store_release(&d->ledger265,slots[0]);
    qemu_cond_broadcast(&d->pfifo.fifo_cond);qemu_mutex_unlock(&d->pfifo.lock);return true;
}
static X265State *x281_slot(X280Transaction *t,unsigned stage)
{return stage==1?t->pre:stage==2?t->post:stage==3?t->end:NULL;}
static bool x281_page(NV2AState *d,const char *value,Error **errp)
{
    X265State *initial=qatomic_load_acquire(&d->ledger265);X280Transaction *t=initial?initial->transaction280:NULL;
    if(!t)return false;
    unsigned state=qatomic_load_acquire(&t->state);uint64_t stage=0,page=0;const char *end=NULL;
    if((state!=3&&state!=5&&state!=6) || strncmp(value,"stage281,",9) ||
       qemu_strtou64(value+9,&end,10,&stage) || !end || *end!=',' || stage<1 || stage>3) {
        error_setg(errp,"281 immutable stage page unavailable");return true;
    }
    const char *p=end+1;end=NULL;X265State *s=x281_slot(t,stage);
    if(qemu_strtou64(p,&end,10,&page) || !end || *end || !s ||
       (state==3&&stage==3) || (s->boundary.state!=5&&s->boundary.state!=6) ||
       page>=x265_page_count(s->ledger.count)) {error_setg(errp,"281 invalid stage/page");return true;}
    t->page_stage=stage;s->page=page;return true;
}
static char *x281_report(X280Transaction *t)
{
    unsigned state=qatomic_load_acquire(&t->state);
    if(state!=3&&state!=5&&state!=6)return g_strdup_printf("version=281 state=%u",state);
    GString *o=g_string_new(NULL);
    g_string_append_printf(o,"version=281 state=%u reason=%u candidate=%u mask=%u armed=%u post=%u sealed=%u native_grant=0",state,t->reason,t->candidate,t->mutated_mask,t->armed,t->post_captured,t->sealed);
    for(unsigned i=0;i<2;i++) {
        g_string_append_printf(o," record%u_present=%u",i,t->published[i]);
        if(t->published[i])for(unsigned j=0;j<16;j++)g_string_append_printf(o," record%u_%u=%"PRIu64,i,j,t->records[i][j]);
    }
    for(unsigned stage=1;stage<=3;stage++) {
        X265State *s=x281_slot(t,stage);unsigned ready=s->boundary.state;
        g_string_append_printf(o," s%u_state=%u",stage,ready);
        if(ready!=5&&ready!=6)continue;
        g_string_append_printf(o," s%u_reason=%u s%u_rows=%u s%u_pages=%u s%u_overflow=%u s%u_accounting=%u s%u_shader_unknown=%u",stage,s->boundary.reason,stage,s->ledger.count,stage,x265_page_count(s->ledger.count),stage,s->ledger.overflow,stage,s->accounting_error,stage,s->shader_jobs_unknown);
    }
    return g_string_free(o,false);
}
static char *x281_data(X280Transaction *t)
{
    unsigned state=qatomic_load_acquire(&t->state);
    if(state!=3&&state!=5&&state!=6)return g_strdup("version=281 unavailable=1");
    unsigned stage=t->page_stage;X265State *s=x281_slot(t,stage);
    if(!s || (state==3&&stage==3) || (s->boundary.state!=5&&s->boundary.state!=6))return g_strdup("version=281 unavailable=1");
    return x265_rows_page(&s->ledger,s->page,stage);
}
