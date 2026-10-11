/* Real core with host memory/owner/lock substitutes; no guest callback claim. */
#include <assert.h>
#include <pthread.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include "arena.h"
typedef struct { pthread_mutex_t lock; unsigned char *memory; uint64_t physical;
 unsigned allocated,discarded,retained,translate_calls,bad_call; int oom,irql,wait; } Host;
static int passive(void *p){return !((Host *)p)->irql;}
static int enter(void *p){Host *h=p;if(h->wait)return 0;return !pthread_mutex_lock(&h->lock);}
static void leave(void *p){assert(!pthread_mutex_unlock(&((Host *)p)->lock));}
static unsigned char *allocate(void *p){Host *h=p;h->allocated++;if(h->oom)return NULL;assert(!h->memory);return h->memory=malloc(X258_BYTES);}
static uint64_t translate(void *p,unsigned char *v){Host *h=p;return h->physical+(uint64_t)(v-h->memory)+(++h->translate_calls==h->bad_call?4096:0);}
static void discard(void *p,unsigned char *v){Host *h=p;assert(v==h->memory);h->discarded++;free(v);h->memory=NULL;}
static void retain(void *p,void *owner){assert(owner);((Host *)p)->retained++;}
static X258Reply *action(X258Arena *a,X258Ops *o,void *owner,unsigned op,unsigned gen,unsigned seed)
{ X258Reply *r=malloc(sizeof(*r));X258Request q={op,gen,seed,0};assert(r);x258_action(a,o,owner,&q,r);return r; }
static void expect(X258Arena *a,X258Ops *o,void *owner,unsigned op,unsigned gen,unsigned seed,unsigned status)
{ X258Reply *r=action(a,o,owner,op,gen,seed);assert(r->status==status);free(r); }
typedef struct { X258Arena *arena; X258Ops *ops; unsigned id,won; } Thread;
static void *race(void *p){Thread *t=p;X258Reply *r=action(t->arena,t->ops,t,X258_ALLOCATE,0,0);assert(r->status==X258_OK || r->status==X258_BUSY);t->won=r->status==X258_OK;free(r);return NULL;}
int main(void)
{
 Host h={.physical=0x200000};assert(!pthread_mutex_init(&h.lock,NULL));
 X258Ops o={&h,passive,enter,leave,allocate,translate,discard,retain};int owners[2];unsigned checks=0;
 for(unsigned trial=0;trial<256;trial++){
  X258Arena a={0};Thread ts[8];pthread_t ids[8];unsigned winners=0;
  h.allocated=h.discarded=h.retained=h.translate_calls=0;
  for(unsigned j=0;j<8;j++){ts[j]=(Thread){&a,&o,j,0};assert(!pthread_create(&ids[j],NULL,race,&ts[j]));}
  for(unsigned j=0;j<8;j++){assert(!pthread_join(ids[j],NULL));winners+=ts[j].won;}
  assert(winners==1 && h.allocated==1 && h.retained==1 && !h.discarded);
  for(unsigned j=0;j<X258_BYTES;j++){assert(h.memory[j]==(unsigned char)(j*37u+(j/16)*19u+(j/256)*7u));checks++;}
  expect(&a,&o,a.owner,X258_READ,0,0,X258_STALE);
  expect(&a,&o,&owners[0],X258_WRITE,1,1,X258_OWNER);
  for(unsigned j=0;j<8;j++){
   unsigned seed=1+(j&1);expect(&a,&o,a.owner,X258_WRITE,1,seed,X258_OK);
   X258Reply *r=action(&a,&o,a.owner,X258_READ,1,0);assert(r->status==X258_OK);
   for(unsigned n=0;n<X258_BYTES;n++){assert(r->data[n]==(unsigned char)((n*37u+(n/16)*19u+(n/256)*7u)^(seed*83u)));checks++;}
   free(r);
  }
  expect(&a,&o,a.owner,X258_READ,1,0,X258_LIMIT);expect(&a,&o,a.owner,X258_WRITE,1,1,X258_LIMIT);
  expect(&a,&o,a.owner,X258_CLOSE,0,0,X258_OK);assert(a.closed && a.memory==h.memory && !h.discarded && h.retained==1);
  expect(&a,&o,a.owner,X258_READ,1,0,X258_QUARANTINED);expect(&a,&o,a.owner,X258_WRITE,1,1,X258_QUARANTINED);
  expect(&a,&o,&owners[1],X258_ALLOCATE,0,0,X258_BUSY);
  /* Model reboot only after every thread joins; production has no free operation. */
  free(h.memory);h.memory=NULL;
 }
 for(unsigned bad=0;bad<9;bad++){
  X258Arena a={0};h.physical=bad==0?0x100001:bad==1?0x0ff000:bad==2?0x03bfc001:0x200000;
  h.bad_call=bad>=3 && bad<=7?bad-2:0;h.translate_calls=0;h.oom=bad==8;
  expect(&a,&o,&owners[0],X258_ALLOCATE,0,0,h.oom?X258_OOM:X258_TRANSLATION);assert(!h.memory && !a.memory);
  expect(&a,&o,&owners[0],X258_ALLOCATE,0,0,X258_BUSY);
 }
 h.oom=h.bad_call=0;h.physical=0x03bfc000;X258Arena a={0};
 h.irql=1;expect(&a,&o,&owners[0],X258_ALLOCATE,0,0,X258_IRQL);h.irql=0;
 h.wait=1;expect(&a,&o,&owners[0],X258_ALLOCATE,0,0,X258_WAIT);h.wait=0;assert(!a.attempted);
 expect(&a,&o,&owners[0],X258_WRITE,0,3,X258_BAD);expect(&a,&o,&owners[0],X258_ALLOCATE,0,0,X258_OK);
 assert(a.physical==0x03bfc000);free(h.memory);assert(!pthread_mutex_destroy(&h.lock));
 printf("PASS actual_core races=256 contenders=2048 exact_bytes=%u quarantine_and_bounds=1\n",checks);
}
