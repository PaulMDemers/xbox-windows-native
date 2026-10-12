/* Called only after a NEW actual provider has proved the full graph, current
 * contexts/worker/locks and post-unit-release snapshots. HOST proposal only.
 * Never use saved identity as a dereference authority; find current cache edges.
 * No rollback after mutation, and no final-free or GL call is silently ignored. */
static X283Result x283_dispose(NV2AState *d,const X283Proof *p)
{
 X283Result result={X283_REFUSED,0,0};
 if(x283_admit(p))return result;
 PGRAPHState *pg=&d->pgraph;PGRAPHGLState *r=pg->gl_renderer_state;
 if(!r || p->observation.device!=(uintptr_t)d || p->observation.region!=(uintptr_t)d->vram ||
    r->texture_cache.pre_node_evict || r->texture_cache.post_node_evict!=texture_cache_entry_post_evict)return result;
 TextureLruNode *selected[4]={0};GLuint names[4];
 for(unsigned i=0;i<4;i++) {
  const X277Texture *t=&p->observation.textures[i];unsigned walked=0,live=0,edges=0;LruNode *n;
  if(r->texture_binding[i] || pgraph_is_texture_enabled(pg,i) || !pg->texture_dirty[i])return result;
  QTAILQ_FOREACH(n,&r->texture_cache.global,next_global) {
   if(++walked>512)return result;
   if(!lru_is_node_in_use(&r->texture_cache,n))continue;
   live++;TextureLruNode *entry=container_of(n,TextureLruNode,node);
   if((uintptr_t)entry->binding!=t->identity)continue;
   edges++;selected[i]=entry;
   if(!entry->binding || entry->binding->refcnt!=1 || entry->binding->gl_texture!=t->name ||
      entry->binding->gl_target!=GL_TEXTURE_2D || entry->possibly_dirty ||
      entry->key.texture_vram_offset!=t->source || entry->key.texture_length!=t->source_bytes ||
      entry->key.palette_vram_offset!=t->palette || entry->key.palette_length!=t->palette_bytes)return result;
  }
  if(edges!=1 || live!=p->cache_count || r->texture_cache.num_used!=(int)live)return result;
  names[i]=t->name;
  for(unsigned j=0;j<i;j++)if(selected[i]==selected[j] || names[i]==names[j])return result;
 }
 GLint active=0;glGetIntegerv(GL_ACTIVE_TEXTURE,&active);bool valid=true;
 for(unsigned i=0;i<4;i++) {
  GLint bound=0;glActiveTexture(GL_TEXTURE0+i);glGetIntegerv(GL_TEXTURE_BINDING_2D,&bound);
  if(bound || !glIsTexture(names[i]))valid=false;
 }
 glActiveTexture(active);
 if(!valid || glGetError()!=GL_NO_ERROR || pgraph_gl_reuse269_error())return result;
 for(unsigned i=0;i<4;i++) {
  /* Original LRU updates its bin/counters and invokes the original final counted
   * destructor. selected[] points to persistent cache nodes, not freed bindings. */
  lru_evict_node(&r->texture_cache,&selected[i]->node);
  result.evicted_mask|=1u<<i;
  bool deleted=!glIsTexture(names[i]);
  if(deleted)result.deleted_mask|=1u<<i;
  if(selected[i]->binding || lru_is_node_in_use(&r->texture_cache,&selected[i]->node) ||
     r->texture_cache.num_used!=(int)(p->cache_count-i-1) || !deleted ||
     glGetError()!=GL_NO_ERROR || pgraph_gl_reuse269_error()) {
   result.status=X283_QUARANTINE;return result;
  }
 }
 result.status=X283_OK;return result;
}
