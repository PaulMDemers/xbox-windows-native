/* SPDX-License-Identifier: GPL-2.0-or-later
 * Host callback mocks test the production CPU manager, not GPU ownership.
 */
#include "context.h"
#include <assert.h>
#include <pthread.h>
#include <stdlib.h>
#include <stdio.h>
typedef struct {
    pthread_mutex_t lock; unsigned char *memory; uint64_t physical;
    unsigned allocations,frees,translate_calls,bad_translation;
    unsigned owner_refs,owner_retains,owner_releases;
    int elevated,no_wait,no_memory;
} Host;
static int passive(void *p){return !((Host*)p)->elevated;}
static int enter(void *p){Host *h=p;return !h->no_wait && !pthread_mutex_lock(&h->lock);}
static void leave(void *p){assert(!pthread_mutex_unlock(&((Host*)p)->lock));}
static unsigned char *allocate(void *p){Host *h=p;if(h->no_memory)return NULL;assert(!h->memory);h->memory=malloc(X222_BYTES);assert(h->memory);h->allocations++;h->translate_calls=0;return h->memory;}
static uint64_t translate(void *p,unsigned char *v){Host *h=p;unsigned call=++h->translate_calls;return h->physical+(uint64_t)(v-h->memory)+(call==h->bad_translation?4096:0);}
static void release(void *p,unsigned char *v){Host *h=p;assert(h->memory==v);free(v);h->memory=0;h->frees++;}
static void retain_owner(void *p,void *owner){Host *h=p;assert(owner && !h->owner_refs);h->owner_refs++;h->owner_retains++;}
static void release_owner(void *p,void *owner){Host *h=p;assert(owner && h->owner_refs==1);h->owner_refs--;h->owner_releases++;}
static X222Reply action(X222Manager *m,X222Ops *o,void *owner,unsigned op,unsigned generation)
{ X222Request q={op,generation};X222Reply r;x222_action(m,o,owner,&q,&r);return r; }
static X222Manager Manager;
static X222Ops Ops;
static void *worker(void *owner)
{
    unsigned i,j;
    for(i=0;i<128;i++) {
        X222Reply r;
        do {r=action(&Manager,&Ops,owner,X222_ALLOCATE,0);} while(r.status==X222_BUSY);
        assert(r.status==X222_OK && r.generation && r.owned);unsigned generation=r.generation;
        for(j=0;j<X222_BYTES;j++) {
            unsigned block=j/256,low=j%256;
            unsigned char expected=(unsigned char)((low*29+block*7+(generation%256)*11)^165);
            if(j>=8208 && j<=8211)expected=0;
            assert(Manager.memory[j]==expected);
        }
        assert(action(&Manager,&Ops,owner,X222_QUERY,generation).status==X222_OK);
        assert(action(&Manager,&Ops,owner,X222_EXPOSE,generation).status==X222_HOLD);
        assert(action(&Manager,&Ops,owner,X222_RELEASE,generation).status==X222_OK);
        assert(action(&Manager,&Ops,owner,X222_QUERY,generation).status!=X222_OK);
    }
    return NULL;
}
int main(void)
{
    Host h={.physical=0x200000};assert(!pthread_mutex_init(&h.lock,NULL));
    Ops=(X222Ops){&h,passive,enter,leave,allocate,translate,release,retain_owner,release_owner};x222_initialize(&Manager);
    int owners[4]={0};X222Reply r=action(&Manager,&Ops,&owners[0],X222_ALLOCATE,0);assert(r.status==X222_OK && r.generation==1);
    assert(action(&Manager,&Ops,&owners[1],X222_QUERY,1).status==X222_OWNER);
    assert(action(&Manager,&Ops,&owners[0],X222_QUERY,2).status==X222_STALE);
    assert(action(&Manager,&Ops,&owners[1],X222_CLEANUP,0).status==X222_OWNER);
    assert(Manager.memory && action(&Manager,&Ops,&owners[0],X222_CLEANUP,0).status==X222_OK);
    assert(Manager.cleanup_releases==1 && !Manager.memory);
    /* Every base/page-start/page-end translation failure frees exactly once. */
    for(unsigned bad=1;bad<=9;bad++) {
        h.bad_translation=bad;unsigned frees=h.frees;
        assert(action(&Manager,&Ops,&owners[0],X222_ALLOCATE,0).status==X222_TRANSLATION);
        assert(!Manager.memory && !h.memory && h.frees==frees+1);
    }
    h.bad_translation=0;
    uint64_t rejected[]={0,0xfffff,0x100001,0x03bfd000,0x03c00000,UINT64_MAX-4095};
    for(unsigned i=0;i<sizeof(rejected)/sizeof(*rejected);i++) {
        h.physical=rejected[i];assert(action(&Manager,&Ops,&owners[0],X222_ALLOCATE,0).status==X222_TRANSLATION);assert(!h.memory);
    }
    h.physical=0x03bfc000;r=action(&Manager,&Ops,&owners[0],X222_ALLOCATE,0);assert(r.status==X222_OK && r.pages[3]==0x03bff000);
    assert(action(&Manager,&Ops,&owners[0],X222_RELEASE,r.generation).status==X222_OK);
    h.physical=0x200000;h.no_memory=1;unsigned next=Manager.next_generation;
    assert(action(&Manager,&Ops,&owners[0],X222_ALLOCATE,0).status==X222_OOM && Manager.next_generation==next+1);h.no_memory=0;
    h.elevated=1;assert(action(&Manager,&Ops,&owners[0],X222_ALLOCATE,0).status==X222_IRQL);h.elevated=0;
    h.no_wait=1;assert(action(&Manager,&Ops,&owners[0],X222_ALLOCATE,0).status==X222_WAIT);h.no_wait=0;
    r=action(&Manager,&Ops,&owners[0],X222_ALLOCATE,0);assert(r.status==X222_OK && h.owner_refs==1);
    h.no_wait=1;
    assert(action(&Manager,&Ops,&owners[0],X222_CLEANUP,0).status==X222_WAIT);
    assert(Manager.memory && Manager.owner==&owners[0] && h.owner_refs==1);
    h.no_wait=0;
    assert(action(&Manager,&Ops,&owners[1],X222_CLEANUP,0).status==X222_OWNER && h.owner_refs==1);
    assert(action(&Manager,&Ops,&owners[0],X222_CLEANUP,0).status==X222_OK && !h.owner_refs);
    r=action(&Manager,&Ops,&owners[0],X222_ALLOCATE,0);Manager.memory[8192]^=1;
    assert(action(&Manager,&Ops,&owners[0],X222_QUERY,r.generation).status==X222_CORRUPT);
    assert(action(&Manager,&Ops,&owners[0],X222_RELEASE,r.generation).status==X222_CORRUPT && !h.memory);
    pthread_t threads[4];for(unsigned i=0;i<4;i++)assert(!pthread_create(&threads[i],NULL,worker,&owners[i]));
    for(unsigned i=0;i<4;i++)assert(!pthread_join(threads[i],NULL));
    assert(!h.memory && Manager.allocations==Manager.releases && h.allocations==h.frees);
    /* Last legal token is never reused, even at an identical physical address. */
    Manager.next_generation=UINT32_MAX;r=action(&Manager,&Ops,&owners[0],X222_ALLOCATE,0);assert(r.status==X222_OK && r.generation==UINT32_MAX);
    Manager.exposure_refusals=UINT32_MAX;Manager.verified_bytes=UINT32_MAX-100;
    assert(action(&Manager,&Ops,&owners[0],X222_EXPOSE,r.generation).status==X222_HOLD);
    assert(Manager.exposure_refusals==UINT32_MAX && Manager.verified_bytes==UINT32_MAX);
    assert(action(&Manager,&Ops,&owners[0],X222_RELEASE,r.generation).status==X222_OK);
    assert(action(&Manager,&Ops,&owners[0],X222_ALLOCATE,0).status==X222_EXHAUSTED);
    assert(Manager.allocations==Manager.releases && h.allocations==h.frees);
    assert(!h.owner_refs && h.owner_retains==h.owner_releases && h.owner_retains==Manager.allocations);
    assert(!pthread_mutex_destroy(&h.lock));printf("PASS concurrent_leases=512 allocated=%u freed=%u\n",h.allocations,h.frees);
    return 0;
}
