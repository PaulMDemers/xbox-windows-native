#include "framebuf.h"
#include <stdlib.h>
#include <assert.h>
#include <stdio.h>
#include <sys/mman.h>
#include "ownership.c"
#include "semaphore-shim.inc"
static void init(PDEV *p,SURFOBJ *s) {
 memset(p,0,sizeof(*p));memset(s,0,sizeof(*s));
 p->hSurfEng=p;p->hDevEng=p;p->ShadowObject=s;
 s->iType=STYPE_DEVICE;s->dhpdev=p;s->dhsurf=p;s->hsurf=p;s->hdev=p;
}
static void *worker(void *arg) {
 PDEV p;SURFOBJ s;unsigned i; (void)arg;init(&p,&s);
 for(i=0;i<10000;i++) {
  assert(XwnRegisterPrimary(&p));assert(XwnOwner(&s)==&p);
  assert(!XwnRegisterPrimary(&p));XwnUnregisterPrimary(&p);
  assert(!XwnOwner(&s));XwnUnregisterPrimary(&p);
 }
 return NULL;
}
int main(void) {
 PDEV p[33],duplicate,*chosen;SURFOBJ s[33],bad;pthread_t threads[8];unsigned i;
 void *guard=mmap(NULL,4096,PROT_NONE,MAP_PRIVATE|MAP_ANONYMOUS,-1,0);assert(guard!=MAP_FAILED);
 for(i=0;i<33;i++)init(&p[i],&s[i]);
 assert(!XwnRegisterPrimary(&p[0]));assert(!XwnOwner(&s[0]));
 SemFail=1;assert(!XwnOwnershipInit());SemFail=0;
 assert(XwnOwnershipInit());assert(!XwnOwnershipInit());
 /* Foreign private data may be unreadable. Equality is not ownership. */
 bad=s[0];bad.dhsurf=guard;bad.dhpdev=guard;
 assert(!XwnOwner(&bad));chosen=NULL;assert(!XwnSelectOwner(&chosen,&bad)&&!chosen);
 for(i=0;i<32;i++)assert(XwnRegisterPrimary(&p[i]));
 assert(!XwnRegisterPrimary(&p[32]));
 for(i=0;i<32;i++)assert(XwnOwner(&s[i])==&p[i]);
 duplicate=p[0];assert(!XwnRegisterPrimary(&duplicate));
 bad=s[0];bad.hdev=guard;assert(!XwnOwner(&bad));
 bad=s[0];bad.hsurf=guard;assert(!XwnOwner(&bad));
 bad=s[0];bad.dhsurf=guard;assert(!XwnOwner(&bad));
 bad=s[0];bad.iType=2;assert(!XwnOwner(&bad));
 chosen=NULL;assert(XwnSelectOwner(&chosen,&s[0])&&chosen==&p[0]);
 assert(!XwnSelectOwner(&chosen,&s[1])&&chosen==&p[0]);
 bad=s[0];bad.iType=STYPE_BITMAP;assert(XwnSelectOwner(&chosen,&bad)&&chosen==&p[0]);
 XwnUnregisterPrimary(&p[0]);assert(!XwnOwner(&s[0]));
 assert(XwnRegisterPrimary(&p[32]));assert(XwnOwner(&s[32])==&p[32]);
 for(i=0;i<33;i++)XwnUnregisterPrimary(&p[i]);
 /* Stale membership never outlives unregister, even after PDEV is freed. */
 {PDEV *heap=malloc(sizeof(*heap));SURFOBJ stale;init(heap,&stale);
  assert(XwnRegisterPrimary(heap));XwnUnregisterPrimary(heap);free(heap);assert(!XwnOwner(&stale));}
 for(i=0;i<8;i++)assert(!pthread_create(&threads[i],NULL,worker,NULL));
 for(i=0;i<8;i++)assert(!pthread_join(threads[i],NULL));
 for(i=0;i<32;i++)assert(!XwnOwners[i].Owner);
 XwnOwnershipDisable();XwnOwnershipDisable();assert(!XwnOwner(&s[0]));
 assert(XwnOwnershipInit());XwnOwnershipDisable();assert(!munmap(guard,4096));
 puts("{\"passed\":true,\"threads\":8,\"register_lookup_remove_cycles\":80000,\"limit\":32,\"foreign_guard_page\":true,\"mixed_pdev_rejected\":true,\"scope\":\"Membership concurrency; GDI call lifetime remains required, no racing render/destruction claim\"}");return 0;
}
