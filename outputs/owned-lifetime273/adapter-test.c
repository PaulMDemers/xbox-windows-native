/* Actual adapter functions are inserted by test-host.py. GL snapshot is a model. */
#define _GNU_SOURCE
#include "wire.h"
#include <assert.h>
#include <stdatomic.h>
#include <pthread.h>
#include <sched.h>
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
typedef struct {unsigned refcnt;int dead;} TextureBinding;
typedef struct {unsigned ignored;} NV2AState;
typedef struct {TextureBinding *identity;uint64_t generation;unsigned name,live,captured;} X269Watch;
static struct {atomic_uint busy,enabled,error,core_error,transport_error,terminal;L270 accounting;uint64_t thread;char *dir;X269Watch watches[4];} x269;
#define qatomic_read(p) atomic_load(p)
#define qatomic_load_acquire(p) atomic_load_explicit((p),memory_order_acquire)
#define qatomic_store_release(p,v) atomic_store_explicit((p),(v),memory_order_release)
#define qatomic_fetch_or(p,v) atomic_fetch_or_explicit((p),(v),memory_order_acq_rel)
#define qatomic_fetch_and(p,v) atomic_fetch_and_explicit((p),(v),memory_order_acq_rel)
static unsigned qatomic_cmpxchg(atomic_uint *p,unsigned expected,unsigned next) {atomic_compare_exchange_strong_explicit(p,&expected,next,memory_order_acq_rel,memory_order_acquire);return expected;}
static uint64_t qemu_get_thread_id(void) {return (uint64_t)pthread_self();}
static unsigned snapshots[4],fail_snapshot,fail_file,fail_write;
static const char *output_file;
static bool x269_snapshot(NV2AState *d,unsigned index,unsigned stage)
{(void)d;assert(stage==1 && index<4 && x269.watches[index].live && !x269.watches[index].identity->dead);snapshots[index]++;return !fail_snapshot;}
static ssize_t broken_write(void *p,const char *b,size_t n) {(void)p;(void)b;(void)n;errno=ENOSPC;return -1;}
static int broken_close(void *p) {(void)p;return 0;}
static FILE *x269_file(const char *leaf)
{
    assert(!strcmp(leaf,"terminal273.bin"));if (fail_file) return NULL;
    if (fail_write) {cookie_io_functions_t io={.write=broken_write,.close=broken_close};return fopencookie(NULL,"w",io);}
    return output_file?fopen(output_file,"wb"):tmpfile();
}
static bool x273_terminal(void);
/* INSERT_ACTUAL_FUNCTIONS */
static TextureBinding bindings[4];
static void setup(void)
{
    memset(&x269,0,sizeof(x269));memset(snapshots,0,sizeof(snapshots));
    fail_snapshot=fail_file=fail_write=0;output_file=NULL;x269.thread=qemu_get_thread_id();
    uint64_t id[4],gen[4];for (unsigned i=0;i<4;i++) {
        bindings[i]=(TextureBinding){2,0};id[i]=(uintptr_t)&bindings[i];gen[i]=i+1;
        x269.watches[i]=(X269Watch){&bindings[i],gen[i],i+10,1,0};
    }
    assert(l270_arm(&x269.accounting,id,gen));atomic_store(&x269.enabled,1);
}
static atomic_uint ready,start;
static void *worker(void *arg)
{
    (void)arg;x269.thread=qemu_get_thread_id();atomic_store(&ready,1);
    while(!atomic_load(&start))sched_yield();
    NV2AState d={0};for(unsigned i=0;i<4;i++)x269_bound(&d,i,&bindings[i],1);
    for(unsigned i=0;i<4;i++)x269_destroying(&bindings[i]);
    return NULL;
}
int main(int argc,char **argv)
{
    assert(argc==2);NV2AState d={0};setup();
    for(unsigned i=0;i<4;i++)x269_bound(&d,i,&bindings[i],2);
    for(unsigned i=0;i<1000000;i++)x269_destroying(&bindings[0]);
    x269_bound(&d,0,&bindings[0],1);bindings[0].refcnt=1;x269_destroying(&bindings[0]);bindings[0].dead=1;
    x269_destroying(&bindings[0]);x269_bound(&d,0,&bindings[0],2); /* tombstone: no dereference/snapshot */
    assert(x269.accounting.sequence==1000006 && x269.accounting.run_count==2);
    assert(x269.accounting.watch[0].has_free && !x269.watches[0].live);
    for(unsigned i=0;i<4;i++)assert(snapshots[i]==1);
    output_file=argv[1];assert(pgraph_gl_reuse269_seal());assert(!pgraph_gl_reuse269_error());
    assert(pgraph_gl_reuse269_seal());assert(atomic_load(&x269.terminal)==2);
    setup();fail_snapshot=1;x269_bound(&d,0,&bindings[0],1);x269_bound(&d,0,&bindings[0],1);
    assert(snapshots[0]==1 && x269.watches[0].captured==2 && pgraph_gl_reuse269_error());
    assert(pgraph_gl_reuse269_seal()); /* transport failure persists in terminal, parser must reject */
    setup();fail_file=1;assert(!pgraph_gl_reuse269_seal());assert(pgraph_gl_reuse269_error());assert(!pgraph_gl_reuse269_seal());
    setup();fail_write=1;assert(!pgraph_gl_reuse269_seal());assert(pgraph_gl_reuse269_error());
    setup();atomic_store(&x269.busy,1);assert(!x269_enter());assert(!pgraph_gl_reuse269_seal());
    atomic_fetch_and(&x269.busy,~1u);assert(pgraph_gl_reuse269_seal());assert(pgraph_gl_reuse269_error());
    setup();x269.thread=0;assert(!x269_enter());assert(pgraph_gl_reuse269_error());assert(pgraph_gl_reuse269_seal());
    for(unsigned n=0;n<4096;n++) {
        setup();atomic_store(&ready,0);atomic_store(&start,0);pthread_t t;
        assert(!pthread_create(&t,NULL,worker,NULL));while(!atomic_load(&ready))sched_yield();atomic_store(&start,1);
        if(n&1)sched_yield();
        while(!pgraph_gl_reuse269_seal())sched_yield();
        L270 sealed=x269.accounting;assert(!pthread_join(t,NULL));assert(!memcmp(&sealed,&x269.accounting,sizeof(sealed)));
        assert(!pgraph_gl_reuse269_error());assert(atomic_load(&x269.busy)==2);assert(!x269_enter());
    }
    puts("PASS actual adapter:1million decrements,4bind snapshots,tombstone,4096seal races,gate and snapshot/open/write/close failures");
}
