#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <pthread.h>
#define qemu_build_assert(c) _Static_assert(c,"atomic width")
#include "qemu/atomic.h"
#include "nv2a_regs.h"
#define QEMU_CLOCK_REALTIME 0
#include "row-actual.inc"
typedef struct {
    uint32_t regs_[0x3000],pending_interrupts,enabled_interrupts;
    bool waiting_for_nop,waiting_for_flip,waiting_for_context_switch;
} PGRAPHState;
typedef struct {
    PGRAPHState pgraph;
    struct {uint64_t total;unsigned count,next;NV2AWaitRow233 rows[NV2A_WAIT233_CAPACITY];} wait233;
} NV2AState;
static uint64_t clock_value;
static int64_t qemu_clock_get_ns(int kind) {assert(kind==0);return clock_value++;}
static uint32_t pgraph_reg_r(PGRAPHState *pg,uint32_t offset) {return pg->regs_[offset];}
/* Host-only adapter for already-owned FIFO snapshot, not another lock. */
static void nv2a_preserve231_snapshot(NV2AState *d,uint32_t words[10]) {
    assert(d);for(unsigned i=0;i<10;i++)words[i]=100+i;
}
#include "wait-actual.inc"
static NV2AState d;
static pthread_mutex_t pg_lock=PTHREAD_MUTEX_INITIALIZER;
static unsigned checks;
static void check(bool value) {assert(value);checks++;}
static void *writer(void *v) {
    unsigned kind=(uintptr_t)v;
    for(unsigned i=0;i<50000;i++) {
        pthread_mutex_lock(&pg_lock);nv2a_wait233_record(&d,kind,i,kind==4);
        pthread_mutex_unlock(&pg_lock);
    }return NULL;
}
int main(int argc,char **argv) {
    (void)argv;
    d.pgraph.regs_[NV_PGRAPH_FIFO]=2;
    NV2AWaitRow233 r;nv2a_wait233_fill(&d,&r,9,0,false);
    check(r.waits&1); /* Only ACCESS bit, not other FIFO bits. */
    if(argc>1) {puts("fifo_mask_check=passed");return 0;}
    memset(&d,0,sizeof(d));
    d.pgraph.regs_[NV_PGRAPH_FIFO]=NV_PGRAPH_FIFO_ACCESS;
    for(unsigned waits=0;waits<16;waits++) {
        d.pgraph.regs_[NV_PGRAPH_FIFO]=(waits&1)?0:NV_PGRAPH_FIFO_ACCESS;
        d.pgraph.waiting_for_nop=waits&2;d.pgraph.waiting_for_flip=waits&4;d.pgraph.waiting_for_context_switch=waits&8;
        nv2a_wait233_fill(&d,&r,2,123,false);check(r.waits==waits);
        check(r.kind==2 && r.value==123 && !r.fifo_valid);
        for(unsigned i=0;i<10;i++)check(!r.fifo[i]);
        nv2a_wait233_fill(&d,&r,4,456,true);check(r.fifo_valid);
        for(unsigned i=0;i<10;i++)check(r.fifo[i]==100+i);
    }
    memset(&d,0,sizeof(d));pthread_t a,b;
    assert(!pthread_create(&a,NULL,writer,(void*)2));assert(!pthread_create(&b,NULL,writer,(void*)4));
    assert(!pthread_join(a,NULL));assert(!pthread_join(b,NULL));
    check(d.wait233.total==100000 && d.wait233.count==256 && d.wait233.next==100000%256);
    unsigned start=(d.wait233.next+256-d.wait233.count)%256;
    for(unsigned i=0;i<256;i++) {
        r=d.wait233.rows[(start+i)%256];check(r.seq==100000-256+i+1);
        check(r.kind==2 || r.kind==4);check(r.fifo_valid==(r.kind==4));
        if(i)check(r.when>d.wait233.rows[(start+i-1)%256].when);
    }
    NV2AState old=d;nv2a_wait233_fill(&d,&r,9,0,true);check(!memcmp(&old,&d,sizeof(d)));
    d.wait233.total=UINT64_MAX;old=d;nv2a_wait233_record(&d,2,1,false);check(!memcmp(&old,&d,sizeof(d)));
    printf("checks=%u records=100000 capacity=256 saturation=covered read_only_fill=covered\n",checks);
}
