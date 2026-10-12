/* Actual immutable record writer, modeled atomic caller/getter protocol. */
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <string.h>
#include <pthread.h>
#include <sched.h>
#include <stdio.h>
#include "release.h"
typedef struct {struct {unsigned stage;uint64_t worker_thread,started,finished;struct{uint64_t epoch;}cpu[2];}boundary;} X265State;
#include "transaction.h"
#include "publish.c"
static X280Transaction tx;
static X265State post,end;
static unsigned winners;
static unsigned cas(unsigned from,unsigned to)
{return __atomic_compare_exchange_n(&tx.state,&from,to,0,__ATOMIC_ACQ_REL,__ATOMIC_ACQUIRE);}
static void *writer(void *unused)
{
    (void)unused;if(!cas(1,2))return NULL;
    __atomic_fetch_add(&winners,1,__ATOMIC_RELAXED);
    tx.armed=tx.post_captured=1;tx.mutated_mask=15;tx.finished=30;
    assert(x280_publish(&tx,&post,1));
    __atomic_store_n(&tx.state,3,__ATOMIC_RELEASE);
    while(__atomic_load_n(&tx.state,__ATOMIC_ACQUIRE)!=4)sched_yield();
    assert(cas(4,2));tx.sealed=1;tx.finished=50;
    assert(x280_publish(&tx,&end,4));
    __atomic_store_n(&tx.state,5,__ATOMIC_RELEASE);return NULL;
}
static void *reader(void *unused)
{
    (void)unused;
    while(__atomic_load_n(&tx.state,__ATOMIC_ACQUIRE)!=3)sched_yield();
    const uint64_t a[16]={280,1,1,3,0,1,15,1,0,2,91,3,4,30,10,20};
    assert(tx.published[0]==1&&!memcmp(tx.records[0],a,sizeof(a)));
    assert(cas(3,4));
    while(__atomic_load_n(&tx.state,__ATOMIC_ACQUIRE)!=5)sched_yield();
    const uint64_t b[16]={280,4,1,5,0,1,15,1,1,3,91,5,6,50,35,45};
    assert(tx.published[1]==1&&!memcmp(tx.records[1],b,sizeof(b)));
    assert(!memcmp(tx.records[0],a,sizeof(a)));return NULL;
}
int main(void)
{
    for(unsigned i=0;i<512;i++) {
        memset(&tx,0,sizeof(tx));winners=0;tx.state=1;tx.candidate=1;
        post=(X265State){.boundary={.stage=2,.worker_thread=91,.started=10,.finished=20,.cpu={{3},{4}}}};
        end=(X265State){.boundary={.stage=3,.worker_thread=91,.started=35,.finished=45,.cpu={{5},{6}}}};
        pthread_t a,b,c;assert(!pthread_create(&a,NULL,writer,NULL));assert(!pthread_create(&b,NULL,writer,NULL));assert(!pthread_create(&c,NULL,reader,NULL));
        assert(!pthread_join(a,NULL));assert(!pthread_join(b,NULL));assert(!pthread_join(c,NULL));
        assert(winners==1&&tx.state==5);
        uint64_t saved[2][16];memcpy(saved,tx.records,sizeof(saved));
        assert(!x280_publish(&tx,&post,1)&&!x280_publish(&tx,&end,4)&&!x280_publish(&tx,&end,2));
        assert(!memcmp(saved,tx.records,sizeof(saved)));
    }
    puts("PASS 512 release/acquire publication races, 1024 competing writers; immutable original record and no repeated publication; modeled caller/getter");
    return 0;
}
