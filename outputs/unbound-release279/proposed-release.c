/*279 Unbound-only unit-reference release. HOST TEST PROPOSAL, not integrated.
 * All callbacks, dirty surfaces, cache entries and source bytes remain owned.
 * Return QUARANTINE after any mutation failure; never fabricate rollback. */
static X279Result x279_release(NV2AState *d,const X279Proof *p)
{
    X279Result result={X279_REFUSED,0};
    if(x279_admit(p))return result;
    PGRAPHState *pg=&d->pgraph;PGRAPHGLState *r=pg->gl_renderer_state;
    for(unsigned i=0;i<4;i++) {
        const X277Texture *t=&p->observation.textures[i];TextureBinding *b=r->texture_binding[i];
        if(!b || (uintptr_t)b!=t->identity || b->refcnt!=2 || b->gl_texture!=t->name ||
           b->gl_target!=GL_TEXTURE_2D || pgraph_is_texture_enabled(pg,i))return result;
        unsigned edges=0,walked=0,live=0;LruNode *n;
        QTAILQ_FOREACH(n,&r->texture_cache.global,next_global) {
            if(++walked>512)return result;
            if(!lru_is_node_in_use(&r->texture_cache,n))continue;
            live++;TextureLruNode *entry=container_of(n,TextureLruNode,node);
            if(entry->binding==b) {
                edges++;
                if(entry->key.texture_vram_offset!=t->source || entry->key.texture_length!=t->source_bytes ||
                   entry->key.palette_vram_offset!=t->palette || entry->key.palette_length!=t->palette_bytes)return result;
            }
        }
        if(edges!=1 || live!=p->cache_count || r->texture_cache.num_used!=(int)live)return result;
    }
    GLint active=0;glGetIntegerv(GL_ACTIVE_TEXTURE,&active);bool valid=true;
    for(unsigned i=0;i<4;i++) {
        GLint bound=0;glActiveTexture(GL_TEXTURE0+i);glGetIntegerv(GL_TEXTURE_BINDING_2D,&bound);
        if(bound)valid=false; /* This candidate intentionally refuses all bindings. */
    }
    glActiveTexture(active);
    if(!valid || glGetError()!=GL_NO_ERROR || pgraph_gl_reuse269_error())return result;
    for(unsigned i=0;i<4;i++) {
        TextureBinding *b=r->texture_binding[i];
        texture_binding_destroy(b); /* Actual original counted release + observer. */
        r->texture_binding[i]=NULL;pg->texture_dirty[i]=true;
        result.mutated_mask|=1u<<i;
        /* Cache retains the only remaining ref. No object deletion is expected. */
        if(b->refcnt!=1 || glGetError()!=GL_NO_ERROR || pgraph_gl_reuse269_error()) {
            result.status=X279_QUARANTINE;return result;
        }
    }
    result.status=X279_OK;return result;
}
