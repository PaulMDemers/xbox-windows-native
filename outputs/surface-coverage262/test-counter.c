#include <assert.h>
#include <pthread.h>
#include <stdio.h>
#include <stdint.h>
#include <limits.h>
#define qatomic_read(p) __atomic_load_n((p),__ATOMIC_SEQ_CST)
static unsigned cas(unsigned *p,unsigned old,unsigned next) {
    __atomic_compare_exchange_n(p,&old,next,0,__ATOMIC_SEQ_CST,__ATOMIC_SEQ_CST);
    return old;
}
#define qatomic_cmpxchg(p,o,n) cas(p,o,n)
#include "telemetry-counter.c"
static unsigned count,limit,hits[4098];
static void *worker(void *unused) {
    (void)unused;
    for(unsigned i=0;i<8192;i++) {
        unsigned n=surface262_claim(&count,limit);
        assert(n<=limit+1);
        __atomic_fetch_add(&hits[n],1,__ATOMIC_SEQ_CST);
    }
    return NULL;
}
int main(void) {
    unsigned checks=0;
    for(unsigned l=256;l<=4096;l*=16) {
        unsigned c=0;
        for(unsigned i=0;i<l+1024;i++) {
            unsigned n=surface262_claim(&c,l);
            assert(n==(i<=l?i:l+1));checks++;
        }
        assert(c==l+1);
        c=UINT_MAX;assert(surface262_claim(&c,l)==l+1 && c==UINT_MAX);checks++;
        for(unsigned round=0;round<16;round++) {
            count=0;limit=l;
            for(unsigned i=0;i<4098;i++)hits[i]=0;
            pthread_t threads[8];
            for(unsigned i=0;i<8;i++)assert(!pthread_create(&threads[i],0,worker,0));
            for(unsigned i=0;i<8;i++)assert(!pthread_join(threads[i],0));
            assert(count==l+1);
            for(unsigned i=0;i<=l;i++){assert(hits[i]==1);checks++;}
            assert(hits[l+1]==8*8192-l-1);checks++;
        }
    }
    printf("%u checks; 32 races; 2097152 concurrent calls; one overflow ticket per race\n",checks);
}
