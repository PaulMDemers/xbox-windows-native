/* Proposed actual-source hooks. x286_active must be supplied by a future
 * one-shot proven owner worker. No QOM provider/arm authority is provided here. */
#include "publication.h"
static P285 *x286_active(void);
typedef struct {
 P285 *p;unsigned slot;uint64_t generation,identity,name,refs;bool held;
} X286Saved;
static X286Saved x286_before_destroy(TextureBinding *b)
{
 X286Saved saved={0};P285 *p=x286_active();
 if(!p || !p285_enter(p,qemu_get_thread_id()))return saved;
 uint64_t identity=(uint64_t)(uintptr_t)b;
 for(unsigned i=0;i<4;i++) {
  G284Unit *u=&p->core.unit[i];
  if(u->old_refs && u->old_identity==identity) {
   saved=(X286Saved){p,i,u->old_generation,identity,b->gl_texture,b->refcnt,true};return saved;
  }
  if(u->new_refs && u->new_identity==identity)p->core.errors|=G284_STATE;
 }
 p285_leave(p);return saved;
}
static void x286_after_destroy(X286Saved saved)
{
 if(!saved.held)return;
 /* Original decrement and, if final, glDeleteTextures/g_free returned. This
  * accesses only saved scalars and stable observer storage, never the binding. */
 g284_decrement(&saved.p->core,qemu_get_thread_id(),saved.slot,saved.generation,
  saved.identity,saved.name,saved.refs);
 p285_leave(saved.p);
}
static void x286_created(unsigned unit,TextureLruNode *node)
{
 P285 *p=x286_active();if(!p || !p285_enter(p,qemu_get_thread_id()))return;
 TextureBinding *b=node->binding;
 _Static_assert(sizeof(TextureKey)<=G284_KEY,"TextureKey exceeds fixed observer capacity");
 if(!b)p->core.errors|=G284_ID;
 else g284_created(&p->core,qemu_get_thread_id(),unit,(uint64_t)(uintptr_t)b,
  b->gl_texture,b->refcnt,(const uint8_t*)&node->key,sizeof(node->key));
 p285_leave(p);
}
static void x286_bound(unsigned unit,TextureBinding *b)
{
 P285 *p=x286_active();if(!p || !p285_enter(p,qemu_get_thread_id()))return;
 if(unit>=4 || !b)p->core.errors|=G284_ID;
 else {
  G284Unit *u=&p->core.unit[unit];
  g284_bound(&p->core,qemu_get_thread_id(),unit,p->core.mode?u->new_generation:u->old_generation,
   (uint64_t)(uintptr_t)b,b->gl_texture,b->refcnt);
 }
 p285_leave(p);
}
