static bool x280_graph(NV2AState *d,X280Transaction *tx,X265State *s,unsigned phase)
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
        TextureBinding *b=r->texture_binding[i];
        bool released=tx->candidate && s->boundary.stage==2;
        uint64_t identity=s->boundary.stage==1?(uint64_t)(uintptr_t)b:tx->pre->proof278.textures[i].identity;
        if(!identity || (released?b!=NULL:(!b || (uint64_t)(uintptr_t)b!=identity)))return false;
        TextureLruNode *found=NULL;unsigned walked=0,edges=0;LruNode *node;
        QTAILQ_FOREACH(node,&r->texture_cache.global,next_global) {
            if(++walked>512)return false;
            if(!lru_is_node_in_use(&r->texture_cache,node))continue;
            TextureLruNode *t=container_of(node,TextureLruNode,node);
            if((uint64_t)(uintptr_t)t->binding==identity){found=t;edges++;}
        }
        if(edges!=1 || !found || !found->binding)return false;
        b=found->binding; /* Follow only a current live cache edge, never a saved owner pointer. */
        if(b->gl_target!=GL_TEXTURE_2D)return false;
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
