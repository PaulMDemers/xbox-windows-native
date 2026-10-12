/* Bounded observed generations, not a runtime owner/admission authority.
 * An actual adapter must invoke these only from pinned normal creation/bind/free
 * paths on the acknowledged worker. No reset, pointer dereference or allocation. */
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#define G284_KEY 1024
#define G284_BYTES 5440
enum { G284_OWNER=1,G284_STATE=2,G284_ID=4,G284_KEY_ERROR=8,G284_CAP=16,G284_SAT=32 };
typedef struct {uint64_t seq,kind,generation,identity,name,refs,unit;} G284Event;
typedef struct {
 uint64_t key_bytes,old_identity,old_name,old_generation,old_refs,old_free;
 uint64_t new_identity,new_name,new_generation,new_refs,bound;
 uint8_t key[G284_KEY];G284Event event[4];
} G284Unit;
typedef struct {
 uint64_t armed,mode,owner,errors,calls,sequence,sealed,next_generation;
 G284Unit unit[4];
} G284;
static bool g284_fail(G284 *g,unsigned error){g->errors|=error;return false;}
static bool g284_arm(G284 *g,uint64_t owner,unsigned mode,const uint64_t identity[4],
 const uint64_t names[4],const uint8_t keys[4][G284_KEY],const uint64_t sizes[4])
{
 if(g->armed)return g284_fail(g,G284_STATE);
 g->armed=1;g->owner=owner;g->mode=mode;g->next_generation=5;
 if(!owner || mode>1)return g284_fail(g,G284_OWNER);
 for(unsigned i=0;i<4;i++) {
  if(!identity[i] || !names[i] || names[i]>UINT32_MAX || !sizes[i] || sizes[i]>G284_KEY)return g284_fail(g,G284_ID);
  for(unsigned j=0;j<i;j++)if(identity[i]==identity[j] || names[i]==names[j] ||
   (sizes[i]==sizes[j]&&!memcmp(keys[i],keys[j],sizes[i])))return g284_fail(g,G284_ID);
 }
 for(unsigned i=0;i<4;i++) {
  G284Unit *u=&g->unit[i];u->key_bytes=sizes[i];u->old_identity=identity[i];u->old_name=names[i];
  u->old_generation=i+1;u->old_refs=2;memcpy(u->key,keys[i],sizes[i]);
 }
 return true;
}
static bool g284_begin(G284 *g,uint64_t owner,unsigned unit)
{
 if(!g->armed || g->sealed || unit>=4)return g284_fail(g,G284_STATE);
 if(!owner || owner!=g->owner)return g284_fail(g,G284_OWNER);
 if(g->calls==UINT64_MAX)g->errors|=G284_SAT;else g->calls++;
 return true; /* Sticky errors do not discard later actual final-free evidence. */
}
static bool g284_emit(G284 *g,unsigned unit,unsigned kind,uint64_t generation,
 uint64_t identity,uint64_t name,uint64_t refs)
{
 G284Event *e=&g->unit[unit].event[kind-1];
 if(e->kind)return g284_fail(g,G284_STATE);
 uint64_t seq=0;
 if(g->sequence>=16)g->errors|=G284_CAP;
 else seq=++g->sequence;
 *e=(G284Event){seq,kind,generation,identity,name,refs,unit};return true;
}
static bool g284_decrement(G284 *g,uint64_t owner,unsigned slot,uint64_t generation,
 uint64_t identity,uint64_t name,uint64_t refs)
{
 if(!g284_begin(g,owner,slot))return false;
 G284Unit *u=&g->unit[slot];
 if(identity!=u->old_identity || name!=u->old_name || generation!=u->old_generation ||
    u->bound || !u->old_refs || refs!=u->old_refs)return g284_fail(g,G284_ID);
 if(refs==2) {
  if(!g284_emit(g,slot,1,generation,identity,name,refs))return false;
  u->old_refs=1;
 } else if(refs==1 && g->mode==1) {
  if(!g284_emit(g,slot,2,generation,identity,name,refs))return false;
  u->old_refs=0;u->old_free=1;
 } else return g284_fail(g,G284_STATE);
 return !g->errors;
}
static uint64_t g284_created(G284 *g,uint64_t owner,unsigned slot,uint64_t identity,
 uint64_t name,uint64_t refs,const uint8_t *key,uint64_t bytes)
{
 if(!g284_begin(g,owner,slot))return 0;
 G284Unit *u=&g->unit[slot];
 if(g->mode!=1 || !u->old_free || u->old_refs || u->new_generation || u->bound ||
    !identity || !name || name>UINT32_MAX || refs!=1){g284_fail(g,G284_STATE);return 0;}
 if(bytes!=u->key_bytes || !bytes || bytes>G284_KEY || memcmp(key,u->key,bytes)){g284_fail(g,G284_KEY_ERROR);return 0;}
 /* The owned guest may not resume until the entire disposal boundary completed. */
 for(unsigned i=0;i<4;i++)if(!g->unit[i].old_free || g->unit[i].old_refs){g284_fail(g,G284_STATE);return 0;}
 for(unsigned i=0;i<4;i++) {
  G284Unit *v=&g->unit[i];
  if((v->old_refs&&(identity==v->old_identity||name==v->old_name)) ||
     (v->new_refs&&(identity==v->new_identity||name==v->new_name))){g284_fail(g,G284_ID);return 0;}
 }
 if(g->next_generation<5 || g->next_generation==UINT64_MAX){g284_fail(g,G284_SAT);return 0;}
 uint64_t generation=g->next_generation++;
 if(!g284_emit(g,slot,3,generation,identity,name,refs))return 0;
 u->new_generation=generation;u->new_identity=identity;u->new_name=name;u->new_refs=1;
 return generation;
}
static bool g284_bound(G284 *g,uint64_t owner,unsigned slot,uint64_t generation,
 uint64_t identity,uint64_t name,uint64_t refs)
{
 if(!g284_begin(g,owner,slot))return false;
 G284Unit *u=&g->unit[slot];
 if(u->bound || refs!=2)return g284_fail(g,G284_STATE);
 if(g->mode==0) {
  if(u->old_refs!=1 || u->old_free || u->new_generation || generation!=u->old_generation ||
     identity!=u->old_identity || name!=u->old_name)return g284_fail(g,G284_ID);
 } else if(!u->old_free || u->old_refs || u->new_refs!=1 || generation!=u->new_generation ||
           identity!=u->new_identity || name!=u->new_name)return g284_fail(g,G284_ID);
 if(!g284_emit(g,slot,4,generation,identity,name,refs))return false;
 u->bound=1;if(g->mode)u->new_refs=2;else u->old_refs=2;
 return !g->errors;
}
static bool g284_seal(G284 *g,uint64_t owner)
{
 if(g->sealed)return g284_fail(g,G284_STATE);
 g->sealed=1;
 if(owner!=g->owner || !owner || !g->armed)g->errors|=G284_OWNER;
 for(unsigned i=0;i<4;i++) {
  G284Unit *u=&g->unit[i];
  if(!u->bound || (g->mode?(u->new_refs!=2 || !u->old_free || u->old_refs):
      (u->old_refs!=2 || u->old_free || u->new_generation)))g->errors|=G284_STATE;
 }
 if(g->sequence!=(g->mode?16u:8u) || g->calls!=g->sequence)g->errors|=G284_CAP;
 return !g->errors;
}
static void g284_word(uint8_t **p,uint64_t x)
{for(unsigned i=0;i<8;i++)*(*p)++=(uint8_t)(x>>(8*i));}
static unsigned g284_encode(const G284 *g,uint8_t *out,unsigned capacity)
{
 if(capacity<G284_BYTES)return 0;
 for(unsigned i=0;i<4;i++)if(g->unit[i].key_bytes>G284_KEY)return 0;
 uint8_t *p=out;uint64_t h[12]={UINT64_C(0x3438324e5758),284,G284_BYTES,g->mode,g->owner,
  g->errors,g->calls,g->sequence,g->sealed,4,g->next_generation,0};
 for(unsigned i=0;i<12;i++)g284_word(&p,h[i]);
 for(unsigned i=0;i<4;i++) {
  const G284Unit *u=&g->unit[i];uint64_t values[11]={u->key_bytes,u->old_identity,u->old_name,
   u->old_generation,u->old_refs,u->old_free,u->new_identity,u->new_name,u->new_generation,u->new_refs,u->bound};
  for(unsigned j=0;j<11;j++)g284_word(&p,values[j]);
  memcpy(p,u->key,G284_KEY);p+=G284_KEY;
  for(unsigned j=0;j<4;j++) {
   const G284Event *e=&u->event[j];uint64_t fields[7]={e->seq,e->kind,e->generation,e->identity,e->name,e->refs,e->unit};
   for(unsigned n=0;n<7;n++)g284_word(&p,fields[n]);
  }
 }
 return (unsigned)(p-out);
}
