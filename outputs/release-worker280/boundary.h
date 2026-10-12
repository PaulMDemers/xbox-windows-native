/*280 New actual-stage validation, derived exactly from277 except explicit stage/ref rules.*/
static inline unsigned x280_validate(const X277Proof *p,unsigned candidate)
{
    if((candidate>1 || p->stage<1 || p->stage>3) || !p->worker || !p->device || !p->region ||
       !p->function || !p->ram_bytes || p->ram_bytes>UINT64_MAX-p->ram_base ||
       p->release_requested) return X277_SCOPE;
    if(p->cpu_stopped!=1 || p->frontend_closed!=1 || p->pfifo_halted!=1 ||
       p->render_fenced!=1 || p->display_fenced!=1 || p->get_equals_put!=1 ||
       !p->render_context || !p->display_context || p->render_context==p->display_context ||
       p->pending || p->method_error || p->unknown_owners ||
       p->started>p->finished || p->finished>=p->deadline) return X277_BOUNDARY;
    for(unsigned phase=0;phase<2;phase++) {
        const X277CPU *c=&p->cpu[phase];const X277Graph *g=&p->graph[phase];
        if(c->done!=1 || c->error || c->clock_error || !c->thread || c->thread==p->worker ||
           c->epoch!=p->stage*2-1+phase || c->when<p->started || c->when>p->finished ||
           g->complete!=1 || g->error) return X277_BOUNDARY;
        if(!c->count || c->count>X277_MAX || g->count!=c->count) return X277_CAPACITY;
        if(!c->clock || c->clock==UINT64_MAX) return X277_LIFETIME;
        for(unsigned i=0;i<c->count;i++) {
            const X277Callback *b=&c->callbacks[i];unsigned matches=0;
            if(!b->identity || b->opaque!=p->device || b->function!=p->function ||
               b->region!=p->region || !x277_range(b->begin,b->bytes,p->ram_bytes) ||
               b->absolute!=p->ram_base+b->begin) return X277_CALLBACK;
            for(unsigned j=0;j<i;j++)
                if(b->identity==c->callbacks[j].identity) return X277_CALLBACK;
            for(unsigned j=0;j<g->count;j++) {
                const X277Surface *s=&g->surfaces[j];
                if(!s->identity || !s->callback || !s->name ||
                   !x277_range(s->begin,s->bytes,p->ram_bytes) ||
                   (s->flags&~UINT64_C(1)) || (s->roles&~UINT64_C(3))) return X277_SURFACE;
                for(unsigned k=0;k<j;k++) {
                    const X277Surface *o=&g->surfaces[k];
                    if(s->identity==o->identity || s->callback==o->callback || s->name==o->name ||
                       (s->roles&o->roles) ||
                       x277_overlap(s->begin,s->bytes,o->begin,o->bytes)) return X277_SURFACE;
                }
                if(s->callback==b->identity) {
                    if(s->begin!=b->begin || s->bytes!=b->bytes) return X277_BIJECTION;
                    matches++;
                }
            }
            if(matches!=1) return X277_BIJECTION;
        }
    }
    const X277CPU *a=&p->cpu[0],*b=&p->cpu[1];
    if(a->thread!=b->thread || a->when>b->when || a->clock!=b->clock || a->count!=b->count ||
       memcmp(a->callbacks,b->callbacks,a->count*sizeof(a->callbacks[0])) ||
       memcmp(p->graph[0].surfaces,p->graph[1].surfaces,p->graph[0].count*sizeof(X277Surface)))
        return X277_LIFETIME;
    for(unsigned i=0;i<4;i++) {
        const X277Texture *t=&p->textures[i];
        if(!t->identity || !t->name || t->refs!=(unsigned)(1+!(candidate && p->stage==2)) || t->cache_edges!=1 || t->unit_edges!=(unsigned)!(candidate && p->stage==2) ||
           t->allocation_bytes!=4096 || (t->allocation&4095) ||
           !x277_range(t->allocation,t->allocation_bytes,p->ram_bytes) ||
           t->source!=t->allocation+256 || t->source_bytes!=512 || t->palette || t->palette_bytes)
            return X277_TEXTURE;
        for(unsigned j=0;j<i;j++) {
            const X277Texture *o=&p->textures[j];
            if(t->identity==o->identity || t->name==o->name ||
               x277_overlap(t->allocation,t->allocation_bytes,o->allocation,o->allocation_bytes))
                return X277_TEXTURE;
        }
        for(unsigned j=0;j<p->graph[0].count;j++) {
            const X277Surface *s=&p->graph[0].surfaces[j];
            if(t->name==s->name || x277_overlap(t->allocation,t->allocation_bytes,s->begin,s->bytes))
                return X277_OVERLAP;
        }
    }
    return X277_OK;
}
