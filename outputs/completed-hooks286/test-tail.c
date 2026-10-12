static unsigned cases,negative_cases;
static TextureLruNode *find_node(PGRAPHGLState *r,TextureBinding *binding)
{
 LruNode *n;QTAILQ_FOREACH(n,&r->texture_cache.global,next_global) {
  TextureLruNode *t=container_of(n,TextureLruNode,node);if(t->binding==binding)return t;
 }
 assert(false);return NULL;
}
static void run(unsigned mode,bool indexed,unsigned negative)
{
 NV2AState d;PGRAPHGLState r;uint8_t *memory=malloc(65536);assert(memory);
 event_count=inject_event=inject_gl=inject_observer=observer_error=0;active285=NULL;thread286=123;
 unsigned before_uploads=uploads,before_frees=frees;
 setup(&d,&r,memory,indexed);
 P285 *p=calloc(1,sizeof(*p));assert(p);active285=p;
 uint64_t ids[4],names[4],sizes[4];uint8_t keys[4][G284_KEY]={{0}};TextureLruNode *nodes[4];
 for(unsigned i=0;i<4;i++) {
  TextureBinding *b=r.texture_binding[i];nodes[i]=find_node(&r,b);
  ids[i]=(uint64_t)(uintptr_t)b;names[i]=b->gl_texture;sizes[i]=sizeof(TextureKey);memcpy(keys[i],&nodes[i]->key,sizeof(TextureKey));
  d.pgraph.enabled[i]=false;
 }
 assert(p285_arm(p,123,mode,ids,names,keys,sizes));
 /* Untracked real allocation/free does not manufacture a selected lifetime. */
 TextureBinding *unrelated=calloc(1,sizeof(*unrelated));assert(unrelated);unrelated->refcnt=1;unrelated->gl_texture=++next_name;objects[next_name].alive=true;
 texture_binding_destroy(unrelated);assert(p->core.calls==0);
 if(negative==1)thread286=999;
 if(negative==2)assert(p285_enter(p,123));
 for(unsigned i=0;i<4;i++) {
  TextureBinding *b=r.texture_binding[i];assert(b->refcnt==2);texture_binding_destroy(b);
  r.texture_binding[i]=NULL;d.pgraph.texture_dirty[i]=true;
 }
 thread286=123;if(negative==2)p285_leave(p);
 for(unsigned i=0;i<4;i++)assert(nodes[i]->binding->refcnt==1);
 if(!negative)for(unsigned i=0;i<4;i++)assert(p->core.unit[i].old_refs==1 && !p->core.unit[i].old_free);
 if(mode) {
  for(unsigned i=0;i<4;i++)lru_evict_node(&r.texture_cache,&nodes[i]->node);
  for(unsigned i=0;i<4;i++){assert(nodes[i]->binding==NULL);assert(!objects[names[i]].alive);}
  if(!negative)for(unsigned i=0;i<4;i++)assert(p->core.unit[i].old_refs==0 && p->core.unit[i].old_free==1);
 }
 if(negative==3)for(unsigned i=0;i<4;i++)d.pgraph.offset[i]+=64;
 for(unsigned i=0;i<4;i++)d.pgraph.enabled[i]=true;
 pgraph_gl_bind_textures(&d);
 for(unsigned i=0;i<4;i++) {
  TextureBinding *b=r.texture_binding[i];assert(b && b->refcnt==2 && objects[b->gl_texture].alive);
  for(unsigned j=0;j<512;j++) {
   uint8_t expected=memory[d.pgraph.offset[i]+j]^(indexed?memory[2048+i*32+j%16]:0);
   assert(objects[b->gl_texture].bytes[j]==expected);
  }
 }
 bool okay=p285_seal(p,123);uint8_t output[P285_BYTES];assert(p285_read(p,output,sizeof(output))==okay);
 if(!negative) {
  assert(okay);assert(p->core.calls==(mode?16u:8u));
  assert(uploads-before_uploads==(mode?8u:4u));
  for(unsigned i=0;i<4;i++)assert(mode?(p->core.unit[i].new_generation>=5):(p->core.unit[i].old_generation==i+1));
  cases++;
 } else {assert(!okay);assert(p->core.errors || (atomic_load(&p->gate)&~3u));negative_cases++;}
 /* Host fixture teardown only, after sealed evidence; no runtime cleanup claim. */
 finish(&r);assert(frees-before_frees==uploads-before_uploads+1);
 active285=NULL;free(p);free(memory);
}
int main(void)
{
 for(unsigned mode=0;mode<2;mode++)for(unsigned indexed=0;indexed<2;indexed++)run(mode,indexed,0);
 for(unsigned negative=1;negative<=3;negative++)for(unsigned indexed=0;indexed<2;indexed++)run(1,indexed,negative);
 assert(deletes==frees);printf("PASS %u original-binder/LRU/destructor lifecycle cases, %u negative cases, %u balanced real host allocations/model GL names; no actual guest/GL/provider\n",cases,negative_cases,frees);
}
