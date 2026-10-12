static unsigned scenarios,refusals,quarantines;
static X283Proof cache_proof(NV2AState *d,const X279Proof *before)
{
 X283Proof p={.operation=X283_DISPOSE,.complete_graph=1,.locks_held=1,.owner_current=1,
  .contexts_current=1,.observer_armed=1,.post_snapshots=1,.cache_count=(unsigned)d->pgraph.gl_renderer_state->texture_cache.num_used};
 p.observation=before->observation;p.observation.stage=2;
 p.observation.device=(uintptr_t)d;p.observation.region=(uintptr_t)d->vram;
 for(unsigned phase=0;phase<2;phase++) {
  p.observation.cpu[phase].epoch=3+phase;
  for(unsigned j=0;j<p.observation.cpu[phase].count;j++) {
   p.observation.cpu[phase].callbacks[j].opaque=(uintptr_t)d;
   p.observation.cpu[phase].callbacks[j].region=(uintptr_t)d->vram;
  }
 }
 for(unsigned i=0;i<4;i++){p.observation.textures[i].refs=1;p.observation.textures[i].unit_edges=0;}
 assert(!x283_admit(&p));return p;
}
static X279Proof prepare_case(NV2AState *d,PGRAPHGLState *r,uint8_t *memory,bool unrelated)
{
 setup(d,r,memory,false);d->vram=memory;
 if(unrelated) {
  /* Original binder creates a fifth, unrelated cached texture before the interval. */
  d->pgraph.offset[0]=5*4096+256;d->pgraph.texture_dirty[0]=true;pgraph_gl_bind_textures(d);
  d->pgraph.offset[0]=256;d->pgraph.texture_dirty[0]=true;pgraph_gl_bind_textures(d);
 }
 for(unsigned i=0;i<4;i++)d->pgraph.enabled[i]=false;
 pgraph_gl_bind_textures(d);
 X279Proof p={.operation=X279_RELEASE,.complete_graph=1,.locks_held=1,.owner_current=1,
  .contexts_current=1,.observer_armed=1,.cache_count=(unsigned)r->texture_cache.num_used};
 p.observation=fixture;
 for(unsigned phase=0;phase<2;phase++)for(unsigned j=0;j<4;j++)p.observation.graph[phase].surfaces[j].name=100000+j;
 for(unsigned i=0;i<4;i++) {
  TextureBinding *b=r->texture_binding[i];
  p.observation.textures[i]=(X277Texture){(uintptr_t)b,b->gl_texture,i*4096,4096,i*4096+256,512,0,0,2,1,1};p.target[i]=GL_TEXTURE_2D;
 }
 event_count=inject_event=inject_gl=inject_observer=observer_error=ignore_name=0;gl_error=0;
 assert(!x279_admit(&p));X279Result a=x279_release(d,&p);assert(a.status==X279_OK&&a.mutated_mask==15);
 event_count=0;return p;
}
static void run_case(bool unrelated,bool change)
{
 NV2AState d;PGRAPHGLState *r=calloc(1,sizeof(*r));uint8_t *memory=malloc(65536);assert(r&&memory);
 X279Proof before=prepare_case(&d,r,memory,unrelated);X283Proof p=cache_proof(&d,&before);
 unsigned de=deletes,fr=frees,up=uploads,free_nodes=r->texture_cache.num_free;TextureLruNode *other=NULL;
 LruNode *n;QTAILQ_FOREACH(n,&r->texture_cache.global,next_global) {
  if(!lru_is_node_in_use(&r->texture_cache,n))continue;
  TextureLruNode *v=container_of(n,TextureLruNode,node);if(v->key.texture_vram_offset==5*4096+256)other=v;
 }
 uintptr_t other_identity=other?(uintptr_t)other->binding:0;unsigned other_name=other?other->binding->gl_texture:0;
 TextureKey other_key={0};if(other)other_key=other->key;
 active=3;X283Result result=x283_dispose(&d,&p);
 assert(result.status==X283_OK&&result.evicted_mask==15&&result.deleted_mask==15&&active==3);
 assert(deletes==de+4&&frees==fr+4&&uploads==up&&event_count==4);
 assert(r->texture_cache.num_used==(int)unrelated && r->texture_cache.num_free==(int)free_nodes+4);
 for(unsigned i=0;i<4;i++)assert(!r->texture_binding[i]&&!objects[p.observation.textures[i].name].alive&&event_refs[i]==1);
 if(other)assert((uintptr_t)other->binding==other_identity&&other->binding->gl_texture==other_name&&other->binding->refcnt==1&&objects[other_name].alive&&!memcmp(&other_key,&other->key,sizeof(other_key)));
 if(change)for(unsigned i=0;i<4;i++)memory[i*4096+256+13]^=0x7d;
 for(unsigned i=0;i<4;i++)d.pgraph.enabled[i]=true;
 pgraph_gl_bind_textures(&d);assert(uploads==up+4);
 for(unsigned i=0;i<4;i++) {
  TextureBinding *b=r->texture_binding[i];assert(b&&b->refcnt==2&&objects[b->gl_texture].alive);
  /* Pointer equality is deliberately irrelevant after final free. */
  for(unsigned j=0;j<512;j++)assert(objects[b->gl_texture].bytes[j]==memory[i*4096+256+j]);
 }
 finish(r);free(r);free(memory);scenarios++;
}
static bool veto(Lru *lru,LruNode *node){(void)lru;(void)node;return false;}
static void failure_cases(void)
{
 NV2AState d;PGRAPHGLState *r=calloc(1,sizeof(*r));uint8_t *memory=malloc(65536);assert(r&&memory);
 X279Proof before=prepare_case(&d,r,memory,true);X283Proof p=cache_proof(&d,&before);
 for(unsigned test=0;test<26;test++) {
  X283Proof q=p;
  switch(test) {
  case 0:q.operation=0;break;case 1:q.complete_graph=0;break;case 2:q.complete_graph=2;break;
  case 3:q.unknown_edges=1;break;case 4:q.selected_gl_edges=1;break;case 5:q.selected_ui_edges=1;break;
  case 6:q.locks_held=0;break;case 7:q.owner_current=0;break;case 8:q.contexts_current=0;break;
  case 9:q.observer_armed=0;break;case 10:q.cache_count=513;break;case 11:q.cache_count=3;break;
  case 12:q.post_snapshots=0;break;case 13:q.post_snapshots=2;break;
  case 14:q.observation.release_requested=1;break;case 15:q.observation.cpu[1].clock++;break;
  case 16:q.observation.cpu[0].done=0;break;case 17:q.observation.graph[1].surfaces[0].flags=3;break;
  case 18:q.observation.textures[0].source_bytes=511;break;case 19:q.observation.textures[0].refs=2;break;
  case 20:q.observation.stage=1;break;case 21:q.observation.cpu[0].callbacks[0].function++;break;
  case 22:q.observation.cpu_stopped=0;break;case 23:q.observation.frontend_closed=0;break;
  case 24:q.observation.pending=1;break;case 25:q.observation.unknown_owners=1;break;
  }
  X283Result a=x283_dispose(&d,&q);assert(a.status==X283_REFUSED&&!a.evicted_mask&&!a.deleted_mask&&!event_count);refusals++;
 }
 TextureLruNode *selected=NULL;LruNode *n;QTAILQ_FOREACH(n,&r->texture_cache.global,next_global)if(lru_is_node_in_use(&r->texture_cache,n)) {
  TextureLruNode *v=container_of(n,TextureLruNode,node);if((uintptr_t)v->binding==p.observation.textures[0].identity)selected=v;
 }
 assert(selected);unsigned used=r->texture_cache.num_used;
 for(unsigned test=0;test<8;test++) {
  if(test==0)r->texture_cache.pre_node_evict=veto;
  if(test==1)r->texture_cache.post_node_evict=NULL;
  if(test==2)selected->possibly_dirty=true;
  if(test==3)selected->binding->refcnt++;
  if(test==4)r->texture_cache.num_used++;
  if(test==5)gl_names[1][1]=selected->binding->gl_texture;
  if(test==6)d.pgraph.enabled[1]=true;
  if(test==7)d.pgraph.texture_dirty[1]=false;
  X283Result a=x283_dispose(&d,&p);assert(a.status==X283_REFUSED&&!a.evicted_mask&&!event_count);refusals++;
  r->texture_cache.pre_node_evict=NULL;r->texture_cache.post_node_evict=texture_cache_entry_post_evict;
  selected->possibly_dirty=false;selected->binding->refcnt=1;r->texture_cache.num_used=used;
  gl_names[1][1]=0;d.pgraph.enabled[1]=false;d.pgraph.texture_dirty[1]=true;
 }
 finish(r);free(r);free(memory);
 for(unsigned kind=0;kind<3;kind++)for(unsigned step=1;step<=4;step++) {
  r=calloc(1,sizeof(*r));memory=malloc(65536);assert(r&&memory);before=prepare_case(&d,r,memory,true);p=cache_proof(&d,&before);
  unsigned de=deletes,fr=frees;inject_event=step;inject_gl=kind==0;inject_observer=kind==1;
  if(kind==2)ignore_name=p.observation.textures[step-1].name;
  X283Result a=x283_dispose(&d,&p);assert(a.status==X283_QUARANTINE&&a.evicted_mask==((1u<<step)-1)&&event_count==step);
  assert(a.deleted_mask==((1u<<(step-(kind==2)))-1));assert(frees==fr+step&&deletes==de+step-(kind==2));
  /* Host harness cleanup after recorded quarantine; never guest rollback/resume. */
  unsigned ignored=ignore_name;ignore_name=inject_event=inject_gl=inject_observer=observer_error=0;gl_error=0;
  if(ignored)glDeleteTextures(1,&ignored);
  finish(r);free(r);free(memory);quarantines++;
 }
}
int main(void)
{
 for(unsigned other=0;other<2;other++)for(unsigned change=0;change<2;change++)run_case(other,change);
 failure_cases();assert(uploads==deletes&&deletes==frees);
 printf("PASS %u original-LRU/destructor/replacement cases, %u pre-mutation refusals, %u exact partial quarantines, %u balanced modeled objects\n",scenarios,refusals,quarantines,uploads);
}
