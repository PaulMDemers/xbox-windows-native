#include <assert.h>
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <sched.h>
#include "publication.h"
static uint64_t ids[4]={100,101,102,103},names[4]={10,11,12,13},sizes[4]={32,32,32,32};
static uint8_t keys[4][G284_KEY];
static P285 *fresh(unsigned mode)
{
 P285 *p=calloc(1,sizeof(*p));assert(p);assert(p285_arm(p,123,mode,ids,names,keys,sizes));return p;
}
static void release_all(P285 *p)
{
 assert(p285_enter(p,123));
 for(unsigned i=0;i<4;i++)assert(g284_decrement(&p->core,123,i,i+1,ids[i],names[i],2));
 p285_leave(p);
}
static void complete(P285 *p,unsigned mode)
{
 release_all(p);assert(p285_enter(p,123));
 if(mode)for(unsigned i=0;i<4;i++)assert(g284_decrement(&p->core,123,i,i+1,ids[i],names[i],1));
 for(unsigned i=0;i<4;i++) {
  uint64_t gen=mode?g284_created(&p->core,123,i,ids[i],names[i],1,keys[i],32):i+1;
  assert(gen);assert(g284_bound(&p->core,123,i,gen,ids[i],names[i],2));
 }
 p285_leave(p);
}
typedef struct {P285 *p;atomic_uint step;unsigned mode;} Race;
static void *reader(void *arg)
{
 Race *r=arg;uint8_t bytes[P285_BYTES];
 atomic_store_explicit(&r->step,1,memory_order_release);
 while(atomic_load_explicit(&r->p->terminal,memory_order_acquire)==0) {
  if(p285_read(r->p,bytes,sizeof(bytes)))break;
  sched_yield();
 }
 assert(p285_read(r->p,bytes,sizeof(bytes)));
 assert(memcmp(bytes,r->p->bytes,sizeof(bytes))==0);
 assert(bytes[24]==123 && bytes[56]==1 && bytes[64+64]==1);
 return NULL;
}
static void *busy_callback(void *arg)
{
 Race *r=arg;assert(p285_enter(r->p,123));
 atomic_store_explicit(&r->step,1,memory_order_release);
 while(atomic_load_explicit(&r->step,memory_order_acquire)!=2)sched_yield();
 assert(g284_decrement(&r->p->core,123,0,1,100,10,2));p285_leave(r->p);return NULL;
}
static void *foreign_after_seal(void *arg)
{Race *r=arg;for(unsigned i=0;i<10000;i++)assert(!p285_enter(r->p,999));return NULL;}
static void *foreign_at_seal(void *arg)
{
 Race *r=arg;
 while(!atomic_load_explicit(&r->step,memory_order_acquire))sched_yield();
 assert(!p285_enter(r->p,999));return NULL;
}
static void *entry_at_seal(void *arg)
{
 Race *r=arg;
 while(!atomic_load_explicit(&r->step,memory_order_acquire))sched_yield();
 if(p285_enter(r->p,123)){sched_yield();p285_leave(r->p);}return NULL;
}
static void save(const char *path,const uint8_t *b,unsigned n)
{FILE *f=fopen(path,"wb");assert(f);assert(fwrite(b,n,1,f)==1);assert(fclose(f)==0);}
int main(void)
{
 for(unsigned u=0;u<4;u++)for(unsigned j=0;j<32;j++)keys[u][j]=(uint8_t)(u*31+j);
 uint8_t out[P285_BYTES],sentinel[P285_BYTES];memset(sentinel,0xa5,sizeof(sentinel));
 for(unsigned mode=0;mode<2;mode++) {
  P285 *p=fresh(mode);memcpy(out,sentinel,sizeof(out));assert(!p285_read(p,out,sizeof(out)));assert(!memcmp(out,sentinel,sizeof(out)));
  complete(p,mode);assert(p285_seal(p,123));assert(p285_read(p,out,sizeof(out)));save(mode?"candidate.bin":"control.bin",out,sizeof(out));
  assert(!p285_seal(p,123));assert(!p285_enter(p,123));assert(!p285_arm(p,123,mode,ids,names,keys,sizes));
  for(unsigned n=0;n<P285_BYTES;n++){memcpy(out,sentinel,sizeof(out));assert(!p285_read(p,out,n));assert(!memcmp(out,sentinel,sizeof(out)));}
  Race r={.p=p};pthread_t t;assert(!pthread_create(&t,NULL,foreign_after_seal,&r));assert(!pthread_join(t,NULL));
  assert(p285_read(p,out,sizeof(out)));assert(!memcmp(out,p->bytes,sizeof(out)));assert(atomic_load(&p->gate)==P285_CLOSED);free(p);
 }
 for(unsigned i=0;i<2048;i++) {
  P285 *p=fresh(i&1);Race r={.p=p,.mode=i&1};pthread_t t;assert(!pthread_create(&t,NULL,reader,&r));
  while(!atomic_load_explicit(&r.step,memory_order_acquire))sched_yield();
  complete(p,i&1);assert(p285_seal(p,123));assert(!pthread_join(t,NULL));free(p);
 }
 for(unsigned i=0;i<2048;i++) {
  P285 *p=fresh(1);Race r={.p=p};pthread_t t;assert(!pthread_create(&t,NULL,busy_callback,&r));
  while(!atomic_load_explicit(&r.step,memory_order_acquire))sched_yield();
  assert(!p285_seal(p,123));assert(atomic_load(&p->terminal)==3);memcpy(out,sentinel,sizeof(out));assert(!p285_read(p,out,sizeof(out)));assert(!memcmp(out,sentinel,sizeof(out)));
  atomic_store_explicit(&r.step,2,memory_order_release);assert(!pthread_join(t,NULL));
  assert(atomic_load(&p->gate)==P285_CLOSED);assert(p->core.calls==1);assert(!p285_seal(p,123));assert(!p285_read(p,out,sizeof(out)));free(p);
 }
 for(unsigned i=0;i<4096;i++) {
  P285 *p=fresh(0);complete(p,0);Race r={.p=p};pthread_t t;
  assert(!pthread_create(&t,NULL,foreign_at_seal,&r));atomic_store_explicit(&r.step,1,memory_order_release);
  bool okay=p285_seal(p,123);assert(!pthread_join(t,NULL));
  unsigned gate=atomic_load_explicit(&p->gate,memory_order_acquire);
  assert(gate==(okay?P285_CLOSED:(P285_CLOSED|P285_FOREIGN)));
  assert(atomic_load(&p->terminal)==(okay?2u:4u));assert(p285_read(p,out,sizeof(out))==okay);free(p);
 }
 for(unsigned i=0;i<4096;i++) {
  P285 *p=fresh(0);complete(p,0);Race r={.p=p};pthread_t t;
  assert(!pthread_create(&t,NULL,entry_at_seal,&r));atomic_store_explicit(&r.step,1,memory_order_release);
  bool okay=p285_seal(p,123);assert(!pthread_join(t,NULL));
  assert(atomic_load(&p->gate)==P285_CLOSED);assert(atomic_load(&p->terminal)==(okay?2u:3u));
  assert(p285_read(p,out,sizeof(out))==okay);free(p);
 }
 P285 *p=fresh(0);assert(!p285_enter(p,999));complete(p,0);assert(!p285_seal(p,123));assert(atomic_load(&p->terminal)==4);save("foreign-failure.bin",p->bytes,P285_BYTES);assert(!p285_read(p,out,sizeof(out)));free(p);
 p=fresh(0);assert(p285_enter(p,123));assert(!p285_enter(p,123));p285_leave(p);complete(p,0);assert(!p285_seal(p,123));assert(atomic_load(&p->terminal)==4);save("busy-failure.bin",p->bytes,P285_BYTES);free(p);
 p=fresh(0);assert(!p285_seal(p,123));assert(atomic_load(&p->terminal)==4);save("incomplete.bin",p->bytes,P285_BYTES);free(p);
 puts("PASS 2048 concurrent publications, 2048 in-flight seal quarantines, 4096 foreign/seal races, 4096 entry/seal races, 20000 closed foreign rejections, 11008 immutable undersized reads; owner/callbacks modeled");
}
