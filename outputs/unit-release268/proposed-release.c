/*268 Not installed in xemu. Harness compiles this beside exact owned functions.
 * Real integration additionally needs the actual immutable before/after ledger,
 * context/CPU acknowledgments and bounded worker admission described in DESIGN.
 */
static bool x268_release(NV2AState *d,const X268Proof *proof)
{
    if(x268_admit(proof)) return false;
    PGRAPHState *pg=&d->pgraph;PGRAPHGLState *r=pg->gl_renderer_state;
    /* Recheck live identities and counts before the first mutation. */
    for(unsigned i=0;i<4;i++) {
        TextureBinding *b=r->texture_binding[i];
        if(!b || (uintptr_t)b!=proof->units[i].binding || b->refcnt!=2 ||
           b->gl_texture!=proof->units[i].texture || b->gl_target!=GL_TEXTURE_2D ||
           pgraph_is_texture_enabled(pg,i)) return false;
        unsigned cache=0,walked=0,live=0;LruNode *node;
        QTAILQ_FOREACH(node,&r->texture_cache.global,next_global) {
            if(++walked>512) return false;
            if(lru_is_node_in_use(&r->texture_cache,node)) {
                live++;
                if(container_of(node,TextureLruNode,node)->binding==b) cache++;
            }
        }
        if(cache!=1 || live!=proof->cache_count || r->texture_cache.num_used!=(int)live) return false;
    }
    GLint active=0,bound[4];glGetIntegerv(GL_ACTIVE_TEXTURE,&active);
    /* Re-read actual render unit bindings before any unbind or counted release. */
    bool okay=true;
    for(unsigned i=0;i<4;i++) {
        glActiveTexture(GL_TEXTURE0+i);glGetIntegerv(GL_TEXTURE_BINDING_2D,&bound[i]);
        unsigned expected=0;
        for(unsigned j=0;j<proof->edge_count;j++) if(proof->edges[j].role==1 &&
            proof->edges[j].unit==i && proof->edges[j].target==GL_TEXTURE_2D) {
            if(expected) okay=false;
            expected=proof->edges[j].texture;
        }
        if((unsigned)bound[i]!=expected) okay=false;
    }
    glActiveTexture(active);
    if(!okay || glGetError()!=GL_NO_ERROR) return false;
    /* Cache refs remain, so these decrements cannot delete a GL object. */
    for(unsigned i=0;i<4;i++) {
        TextureBinding *b=r->texture_binding[i];
        if((unsigned)bound[i]==b->gl_texture) {
            glActiveTexture(GL_TEXTURE0+i);glBindTexture(GL_TEXTURE_2D,0);
        }
        texture_binding_destroy(b);
        r->texture_binding[i]=NULL;
        pg->texture_dirty[i]=true;
    }
    glActiveTexture(active);
    return glGetError()==GL_NO_ERROR;
}
