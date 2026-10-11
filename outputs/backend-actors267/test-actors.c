#include <assert.h>
#include <pthread.h>
#include <sched.h>
#include <stdio.h>
#include "actor-core.h"
static X267Actor records[4096];
static unsigned next,overflow;
static void *contender(void *argument)
{
    uintptr_t identity=(uintptr_t)argument;
    for(unsigned j=0;j<1024;j++) {
        unsigned n=x267_reserve(&next,&overflow,4096);
        if(n==4096) continue;
        X267Actor *a=&records[n];
        a->epoch=n+1;a->owner=identity;a->kind=1;
        __atomic_store_n(&a->state,1,__ATOMIC_RELEASE);
        x267_start(a,identity+10);
        x267_finish(a);
    }
    return NULL;
}
int main(void)
{
    pthread_t threads[8];
    for(uintptr_t i=0;i<8;i++) assert(!pthread_create(&threads[i],NULL,contender,(void*)(i+1)));
    unsigned complete=0;
    while(complete<4096) {
        complete=0;
        for(unsigned i=0;i<4096;i++) if(x267_state(&records[i])==3) {
            X267Actor *a=&records[i];
            assert(a->epoch==i+1 && a->owner>=1 && a->owner<=8);
            assert(a->thread==a->owner+10 && a->kind==1);complete++;
        }
        sched_yield();
    }
    for(unsigned i=0;i<8;i++) assert(!pthread_join(threads[i],NULL));
    assert(next==4096 && overflow==1);
    for(unsigned i=0;i<10000;i++) assert(x267_reserve(&next,&overflow,4096)==4096);
    assert(next==4096 && x267_state(NULL)==0);
    unsigned empty=0,over=0;assert(x267_reserve(&empty,&over,0)==0 && empty==0 && over==1);
    X267Actor pending={0};assert(x267_state(&pending)==0);
    __atomic_store_n(&pending.state,1,__ATOMIC_RELEASE);assert(x267_state(&pending)==1);
    x267_start(&pending,77);assert(x267_state(&pending)==2 && pending.thread==77);
    x267_finish(&pending);assert(x267_state(&pending)==3);
    /* Old records stay acknowledged and distinct from later generations. */
    for(unsigned i=0;i<4096;i++) assert(records[i].epoch==i+1 && x267_state(&records[i])==3);
    puts("4096 concurrently published records;8192 contenders;10000 saturated refusals;pending/null/zero-capacity states PASS");
}
