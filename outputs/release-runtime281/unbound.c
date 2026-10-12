/* Called only with renderer/PG locks retained by successful x280_capture. */
static bool x280_unbound(NV2AState *d,X265State *s,X279Proof *out)
{
    X277Proof *p=&s->proof278;PGRAPHGLState *r=d->pgraph.gl_renderer_state;
    if(!r || qatomic_load_acquire(&s->boundary.state)!=5 || s->ledger.overflow ||
       s->accounting_error || s->shader_jobs_unknown || x277_validate(p) ||
       p->stage!=1 || p->device!=(uintptr_t)d || p->region!=(uintptr_t)d->vram || p->worker!=qemu_get_thread_id() || !xwn_frontend246_closed())return false;
    uint64_t names[4];for(unsigned i=0;i<4;i++)names[i]=p->textures[i].name;
    uintptr_t context[4];uint64_t ui_context=0;
    if(!glo_context_observe267(g_nv2a_context_render,context) || context[0]!=p->render_context ||
       !x281_edges((const uint64_t (*)[8])s->ledger.rows,s->ledger.count,6,names) ||
       !xwn_ui281_unbound(names,&ui_context) || !ui_context || ui_context==p->render_context || ui_context==p->display_context)return false;
    unsigned cache=0,units=0;X279Proof result={0};
    for(unsigned j=0;j<s->ledger.count;j++) {
        const uint64_t *row=s->ledger.rows[j];
        if(row[0]==2)cache++;
        if(row[0]!=3)continue;
        if(row[1]>=4)return false;
        unsigned i=row[1];
        if(i>=4 || (units&(1u<<i)) || row[2]!=p->textures[i].identity || row[3])return false;
        TextureBinding *b=r->texture_binding[i];
        if(!b || (uintptr_t)b!=row[2] || b->gl_texture!=names[i] || b->gl_target!=GL_TEXTURE_2D ||
           b->refcnt!=2 || pgraph_is_texture_enabled(&d->pgraph,i))return false;
        units|=1u<<i;result.target[i]=b->gl_target;
    }
    if(units!=15 || cache<4 || cache>512 || r->texture_cache.num_used!=(int)cache)return false;
    result.observation=*p;result.operation=X279_RELEASE;result.complete_graph=1;
    result.locks_held=1; /* Private call path retains both locks from capture. */
    result.owner_current=1;result.contexts_current=1;result.cache_count=cache;
    /* observer_armed remains0 until the actual arm returns success. */
    *out=result;return true;
}
