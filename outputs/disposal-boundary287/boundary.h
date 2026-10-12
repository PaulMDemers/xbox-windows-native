/* Explicit four-stage scalar contract. Actual collectors/worker are NOT present.
 * Historical anchors are not current objects; absence is a distinct state. */
#include <stdbool.h>
#include "admission.h"
#include "common.h"
typedef struct {
 X277Texture anchor,current;
 uint64_t old_generation,generation,old_completed_free,old_gl_deleted,current_gl_alive;
 uint64_t key_bytes;
 uint8_t old_key[1024],current_key[1024];
} X287Slot;
typedef struct {
 X277Proof boundary; /* textures[] must be zero; selected objects live below. */
 unsigned candidate,inventory_complete,inventory_error;
 X287Slot selected[4];
} X287Proof;
static unsigned x287_validate(const X287Proof *p)
{
 unsigned error=x287_common(&p->boundary);if(error)return error;
 X277Texture empty={0};
 for(unsigned i=0;i<4;i++)if(memcmp(&p->boundary.textures[i],&empty,sizeof(empty)))return X277_SCOPE;
 if(p->candidate>1 || p->inventory_complete!=1 || p->inventory_error)return X277_SCOPE;
 unsigned stage=p->boundary.stage;bool absent=p->candidate&&stage==3;
 for(unsigned i=0;i<4;i++) {
  const X287Slot *s=&p->selected[i];const X277Texture *a=&s->anchor,*t=&s->current;
  if(!a->identity || !a->name || a->name>UINT32_MAX || a->refs!=2 || a->cache_edges!=1 || a->unit_edges!=1 ||
     a->allocation_bytes!=4096 || (a->allocation&4095) ||
     !x277_range(a->allocation,4096,p->boundary.ram_bytes) ||
     a->source!=a->allocation+256 || a->source_bytes!=512 || a->palette || a->palette_bytes ||
     s->old_generation!=i+1 || !s->key_bytes || s->key_bytes>1024)return X277_TEXTURE;
  for(unsigned j=s->key_bytes;j<1024;j++)if(s->old_key[j] || s->current_key[j])return X277_TEXTURE;
  unsigned destroyed=p->candidate&&stage>=3;
  if(s->old_completed_free!=destroyed || s->old_gl_deleted!=destroyed)return X277_LIFETIME;
  if(absent) {
   if(memcmp(t,&empty,sizeof(empty)) || s->generation || s->current_gl_alive)return X277_TEXTURE;
   for(unsigned j=0;j<1024;j++)if(s->current_key[j])return X277_TEXTURE;
  } else {
   unsigned refs=(stage==2 || stage==3)?1:2;
   if(!t->identity || !t->name || t->name>UINT32_MAX || t->refs!=refs || t->cache_edges!=1 || t->unit_edges!=refs-1 ||
      s->current_gl_alive!=1 || t->allocation!=a->allocation || t->allocation_bytes!=a->allocation_bytes ||
      t->source!=a->source || t->source_bytes!=a->source_bytes || t->palette || t->palette_bytes ||
      memcmp(s->old_key,s->current_key,s->key_bytes))return X277_TEXTURE;
   if(p->candidate&&stage==4) {
    if(s->generation<5 || s->generation>8)return X277_LIFETIME;
   } else if(s->generation!=s->old_generation || t->identity!=a->identity || t->name!=a->name)return X277_LIFETIME;
  }
  for(unsigned j=0;j<i;j++) {
   const X287Slot *o=&p->selected[j];
   if(a->identity==o->anchor.identity || a->name==o->anchor.name ||
      x277_overlap(a->allocation,4096,o->anchor.allocation,4096) ||
      (s->key_bytes==o->key_bytes&&!memcmp(s->old_key,o->old_key,s->key_bytes)))return X277_TEXTURE;
   if(!absent && (t->identity==o->current.identity || t->name==o->current.name || s->generation==o->generation))return X277_TEXTURE;
  }
  for(unsigned j=0;j<p->boundary.graph[0].count;j++) {
   const X277Surface *surface=&p->boundary.graph[0].surfaces[j];
   if((!absent&&t->name==surface->name) || x277_overlap(a->allocation,4096,surface->begin,surface->bytes))return X277_OVERLAP;
  }
 }
 return X277_OK;
}
static unsigned x287_chain(const X287Proof *before,const X287Proof *after)
{
 unsigned error=x287_validate(before);if(error)return error;
 error=x287_validate(after);if(error)return error;
 const X277Proof *a=&before->boundary,*b=&after->boundary;
 if(b->stage!=a->stage+1 || before->candidate!=after->candidate ||
    a->worker!=b->worker || a->device!=b->device || a->region!=b->region || a->function!=b->function ||
    a->ram_base!=b->ram_base || a->ram_bytes!=b->ram_bytes ||
    a->render_context!=b->render_context || a->display_context!=b->display_context ||
    a->cpu[0].thread!=b->cpu[0].thread || a->finished>b->started)return X277_BOUNDARY;
 for(unsigned i=0;i<4;i++) {
  const X287Slot *x=&before->selected[i],*y=&after->selected[i];
  if(memcmp(&x->anchor,&y->anchor,sizeof(x->anchor)) || x->old_generation!=y->old_generation ||
     x->key_bytes!=y->key_bytes || memcmp(x->old_key,y->old_key,1024))return X277_LIFETIME;
 }
 if(b->cpu[0].clock<a->cpu[1].clock)return X277_LIFETIME;
 if(b->stage<=3) {
  if(a->cpu[1].clock!=b->cpu[0].clock || a->cpu[1].count!=b->cpu[0].count ||
     memcmp(a->cpu[1].callbacks,b->cpu[0].callbacks,a->cpu[1].count*sizeof(X277Callback)) ||
     a->graph[1].count!=b->graph[0].count ||
     memcmp(a->graph[1].surfaces,b->graph[0].surfaces,a->graph[1].count*sizeof(X277Surface)))return X277_LIFETIME;
 }
 return X277_OK;
}
