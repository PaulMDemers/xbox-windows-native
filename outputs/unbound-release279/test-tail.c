static unsigned scenarios,refusals,quarantines;
static X279Proof make_proof(NV2AState *d) {
    X279Proof p={.operation=X279_RELEASE,.complete_graph=1,.locks_held=1,.owner_current=1,
        .contexts_current=1,.observer_armed=1,.cache_count=4};
    p.observation=fixture; /* Explicit modeled CPU/context admission, not runtime proof. */
    /* Distinct modeled GL namespace; do not reuse historical surface names as model objects grow. */
    for(unsigned phase=0;phase<2;phase++)for(unsigned j=0;j<4;j++)p.observation.graph[phase].surfaces[j].name=100000+j;
    for(unsigned i=0;i<4;i++) {
        TextureBinding *b=d->pgraph.gl_renderer_state->texture_binding[i];
        p.observation.textures[i]=(X277Texture){(uintptr_t)b,b->gl_texture,i*4096,4096,i*4096+256,512,0,0,2,1,1};
        p.target[i]=GL_TEXTURE_2D;
    }
    assert(!x279_admit(&p));return p;
}
static void prepare_case(NV2AState *d,PGRAPHGLState *r,uint8_t *memory) {
    setup(d,r,memory,false);
    for(unsigned i=0;i<4;i++)d->pgraph.enabled[i]=false;
    pgraph_gl_bind_textures(d);
    event_count=0;inject_event=inject_gl=inject_observer=0;observer_error=0;
}
static void run_case(unsigned change,bool release,bool evict) {
    NV2AState d;PGRAPHGLState *r=calloc(1,sizeof(*r));uint8_t *memory=malloc(65536);assert(r&&memory);
    prepare_case(&d,r,memory);X279Proof p=make_proof(&d);
    TextureBinding *old[4];for(unsigned i=0;i<4;i++)old[i]=r->texture_binding[i];
    unsigned de=deletes,fr=frees,up=uploads;
    if(release) {
        X279Result q=x279_release(&d,&p);assert(q.status==X279_OK&&q.mutated_mask==15);
        assert(deletes==de&&frees==fr&&uploads==up&&event_count==4);
        for(unsigned i=0;i<4;i++)assert(!r->texture_binding[i]&&old[i]->refcnt==1&&d.pgraph.texture_dirty[i]);
    }
    if(evict)lru_flush(&r->texture_cache);
    if(change) {d.dirty=true;if(change==2)for(unsigned i=0;i<4;i++)memory[i*4096+256+13]^=0x7d;}
    for(unsigned i=0;i<4;i++)d.pgraph.enabled[i]=true;
    pgraph_gl_bind_textures(&d);
    for(unsigned i=0;i<4;i++) {
        TextureBinding *b=r->texture_binding[i];assert(b&&objects[b->gl_texture].alive);
        if(!evict&&change<2)assert(b==old[i]);
        for(unsigned j=0;j<512;j++)assert(objects[b->gl_texture].bytes[j]==memory[i*4096+256+j]);
        if(release)assert(b->refcnt==2);
    }
    if(!evict&&change<2)assert(uploads==up);
    finish(r);free(r);free(memory);scenarios++;
}
static void failure_cases(void) {
    NV2AState d;PGRAPHGLState *r=calloc(1,sizeof(*r));uint8_t *memory=malloc(65536);assert(r&&memory);
    prepare_case(&d,r,memory);X279Proof p=make_proof(&d);
    for(unsigned test=0;test<26;test++) {
        X279Proof q=p;
        switch(test) {
        case 0:q.operation=0;break;case 1:q.complete_graph=0;break;case 2:q.complete_graph=2;break;
        case 3:q.unknown_edges=1;break;case 4:q.selected_gl_edges=1;break;case 5:q.selected_ui_edges=1;break;
        case 6:q.locks_held=0;break;case 7:q.owner_current=0;break;case 8:q.contexts_current=0;break;
        case 9:q.observer_armed=0;break;case 10:q.cache_count=513;break;case 11:q.cache_count=3;break;
        case 12:q.enabled[0]=1;break;case 13:q.target[0]=GL_TEXTURE_3D;break;
        case 14:q.observation.release_requested=1;break;case 15:q.observation.cpu[1].clock++;break;
        case 16:q.observation.cpu[0].done=0;break;case 17:q.observation.graph[1].surfaces[0].flags=3;break;
        case 18:q.observation.textures[0].source_bytes=511;break;case 19:q.observation.textures[0].refs=1;break;
        case 20:q.observation.stage=2;break;case 21:q.observation.cpu[0].callbacks[0].function++;break;
        case 22:q.observation.cpu_stopped=0;break;case 23:q.observation.frontend_closed=0;break;
        case 24:q.observation.pending=1;break;case 25:q.observation.unknown_owners=1;break;
        }
        X279Result a=x279_release(&d,&q);assert(a.status==X279_REFUSED&&!a.mutated_mask&&!event_count);refusals++;
    }
    for(unsigned test=0;test<5;test++) {
        X279Proof q=p;unsigned saved=r->texture_cache.num_used;
        if(test==0)d.pgraph.enabled[1]=true;
        if(test==1)q.observation.textures[0].identity++;
        if(test==2)r->texture_cache.num_used++;
        if(test==3)gl_names[1][1]=r->texture_binding[1]->gl_texture;
        if(test==4)gl_error=0x502;
        X279Result a=x279_release(&d,&q);assert(a.status==X279_REFUSED&&!a.mutated_mask&&!event_count);refusals++;
        d.pgraph.enabled[1]=false;r->texture_cache.num_used=saved;gl_names[1][1]=0;gl_error=0;
    }
    finish(r);free(r);free(memory);
    for(unsigned kind=0;kind<2;kind++)for(unsigned event=1;event<=4;event++) {
        r=calloc(1,sizeof(*r));memory=malloc(65536);assert(r&&memory);prepare_case(&d,r,memory);p=make_proof(&d);
        TextureBinding *old[4];for(unsigned i=0;i<4;i++)old[i]=r->texture_binding[i];
        unsigned de=deletes,fr=frees;inject_event=event;inject_gl=!kind;inject_observer=kind;
        X279Result a=x279_release(&d,&p);
        assert(a.status==X279_QUARANTINE&&a.mutated_mask==((1u<<event)-1)&&event_count==event);
        assert(deletes==de&&frees==fr);
        for(unsigned i=0;i<4;i++)assert(i<event?(!r->texture_binding[i]&&old[i]->refcnt==1):(r->texture_binding[i]==old[i]&&old[i]->refcnt==2));
        /* Test cleanup after quarantine only; guest is never resumed here. */
        inject_event=inject_gl=inject_observer=observer_error=0;gl_error=0;
        finish(r);free(r);free(memory);quarantines++;
    }
}
int main(void) {
    for(unsigned change=0;change<3;change++)for(unsigned release=0;release<2;release++)for(unsigned evict=0;evict<2;evict++)run_case(change,release,evict);
    failure_cases();assert(uploads==deletes&&deletes==frees);
    printf("PASS %u actual-binder model cases, %u pre-mutation refusals, %u partial-release quarantines, %u balanced model objects\n",scenarios,refusals,quarantines,uploads);
}
