#define _XOPEN_SOURCE 700
#include <assert.h>
#include <stdatomic.h>
#include <stdint.h>
#include <stdio.h>
#include <pthread.h>
typedef struct {
 struct { _Atomic unsigned state; int64_t deadline; unsigned old_halt; } preserve227;
 struct { _Atomic unsigned halt; } pfifo;
} NV2AState;
static NV2AState d;
static int64_t now;
static unsigned inject, checks;
static pthread_barrier_t barrier;
static unsigned load(_Atomic unsigned *p) {
 unsigned v=atomic_load(p);
 if(p==&d.preserve227.state && inject==1) {inject=0;atomic_store(p,5);}
 return v;
}
static unsigned cmp(_Atomic unsigned *p,unsigned expected,unsigned value) {
 if(inject==2) {inject=0;atomic_store(p,5);}
 unsigned original=expected;
 atomic_compare_exchange_strong(p,&expected,value);
 if(inject==3 && expected==original) {
  inject=0;
  unsigned seen=atomic_load(p);
  /* Actual report only expires states1/2, never claimed publication7. */
  if(seen==1 || seen==2) atomic_compare_exchange_strong(p,&seen,5);
 }
 return expected;
}
#define qatomic_read(p) load(p)
#define qatomic_cmpxchg(p,e,v) cmp(p,e,v)
#define qatomic_set(p,v) atomic_store(p,v)
#define QEMU_CLOCK_REALTIME 0
static int64_t qemu_clock_get_ns(int clock) { assert(clock==0);return now; }
/* This is extracted byte-for-byte from the compiled xemu candidate source. */
#include "terminal-actual.inc"
static void check(int good) { assert(good);checks++; }
static void *worker(void *unused) {
 (void)unused;
 for(unsigned i=0;i<100000;i++) {
  pthread_barrier_wait(&barrier);nv2a_preserve227_finish(&d,3);
  pthread_barrier_wait(&barrier);
 }
 return 0;
}
static void *timeout_worker(void *unused) {
 (void)unused;
 for(unsigned i=0;i<100000;i++) {
  pthread_barrier_wait(&barrier);
  unsigned expected=atomic_load(&d.preserve227.state);
  if(expected==1 || expected==2) atomic_compare_exchange_strong(&d.preserve227.state,&expected,5);
  pthread_barrier_wait(&barrier);
 }
 return 0;
}
int main(void) {
 for(unsigned start=1;start<=2;start++) for(unsigned result=3;result<=6;result++)
 for(unsigned old=0;old<=1;old++) for(unsigned time=99;time<=101;time++)
 for(unsigned hook=0;hook<=3;hook++) {
  atomic_store(&d.preserve227.state,start);atomic_store(&d.pfifo.halt,1);
  d.preserve227.deadline=100;d.preserve227.old_halt=old;now=time;inject=hook;
  nv2a_preserve227_finish(&d,result);
  unsigned expected=(hook==1 || hook==2 || time>=100)?5:result;
  check(atomic_load(&d.preserve227.state)==expected);
  check(atomic_load(&d.pfifo.halt)==((expected==3 || expected==4)?old:1));
 }
 for(unsigned state=0;state<=7;state++) if(state!=1 && state!=2) {
  atomic_store(&d.preserve227.state,state);atomic_store(&d.pfifo.halt,1);
  inject=0;now=99;nv2a_preserve227_finish(&d,3);
  check(atomic_load(&d.preserve227.state)==state && atomic_load(&d.pfifo.halt)==1);
 }
 inject=0;now=99;d.preserve227.deadline=100;d.preserve227.old_halt=0;
 assert(!pthread_barrier_init(&barrier,0,3));pthread_t a,b;
 assert(!pthread_create(&a,0,worker,0));assert(!pthread_create(&b,0,timeout_worker,0));
 unsigned finished=0,expired=0;
 for(unsigned i=0;i<100000;i++) {
  atomic_store(&d.preserve227.state,1+i%2);atomic_store(&d.pfifo.halt,1);
  pthread_barrier_wait(&barrier);pthread_barrier_wait(&barrier);
  unsigned state=atomic_load(&d.preserve227.state),halt=atomic_load(&d.pfifo.halt);
  check((state==3 && halt==0) || (state==5 && halt==1));
  finished+=state==3;expired+=state==5;
 }
 assert(!pthread_join(a,0) && !pthread_join(b,0));assert(!pthread_barrier_destroy(&barrier));
 printf("checks=%u concurrent_pairs=100000 completed=%u timed_out=%u native_grants=0\n",checks,finished,expired);
}
