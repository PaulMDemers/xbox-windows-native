/* Execute the actual provider. Direct static-state access is used only for
 * unreachable-in-practice overflow setup and post-join invariant checks.
 * Host locks model exclusion, not kernel scheduling or IRQL semantics. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../xwn_fb.c"
static int boot_owns;
BOOLEAN InbvCheckDisplayOwnership(void) { return boot_owns; }
static XWN_FB_VIEW valid = {44,1,0xfced6000,0x03c00000,0x400000,1024*576*4,1024,576,4096,0x380000,0};
static XWN_FB_VIEW request(void) { XWN_FB_VIEW v=valid; v.Address=0; return v; }
static void *device=(void*)1;
static unsigned checks;
#define CHECK(x) do { ++checks; if (!(x)) { fprintf(stderr,"line %d: %s\n",__LINE__,#x); abort(); } } while(0)
static void *worker(void *arg) {
    /* Different owners race for the lease; rejected acquisitions may retry on
     * the next iteration, but every accepted lease must release successfully. */
    uintptr_t id=(uintptr_t)arg; unsigned acquired=0;
    for (unsigned i=0;i<50000;++i) {
        XWN_FB_VIEW v=request(); NTSTATUS s=XwnFbAcquire((void*)id,&v);
        if (s==STATUS_SUCCESS) {
            assert(!memcmp(&v,&valid,sizeof v));
            assert(XwnFbRelease((void*)id,(void*)(uintptr_t)v.Address)==STATUS_SUCCESS);
            ++acquired;
        } else assert(s==STATUS_INVALID_PARAMETER);
    }
    return (void*)(uintptr_t)acquired;
}
int main(void) {
    XWN_FB_VIEW v=request();
    CHECK(XwnFbAcquire(device,&v)==STATUS_DEVICE_NOT_READY);
    CHECK(!XwnFbPublish(NULL));
    /* Invalid publication never claims Ready or mutates the published view. */
    for(unsigned field=0;field<11;++field) {
        v=valid; ((ULONG*)&v)[field]=0xffffffff;
        CHECK(!XwnFbPublish(&v)); CHECK(Ready==0);
    }
    v=valid;v.Address=0;CHECK(!XwnFbPublish(&v));
    v=valid;v.HiddenOffset=v.VisibleBytes-1;CHECK(!XwnFbPublish(&v));
    v=valid;v.Width=1920;v.Height=1080;v.Stride=7680;v.VisibleBytes=8294400;CHECK(!XwnFbPublish(&v));
    CHECK(XwnFbPublish(&valid)); CHECK(!XwnFbPublish(&valid));
    CHECK(XwnFbRelease(device,(void*)(uintptr_t)valid.Address)==STATUS_INVALID_PARAMETER);
    CHECK(XwnFbReleaseOwner(NULL)==STATUS_INVALID_PARAMETER);
    boot_owns=1;v=request();CHECK(XwnFbAcquire(device,&v)==STATUS_DEVICE_BUSY);boot_owns=0;
    test_irql=2;v=request();CHECK(XwnFbAcquire(device,&v)==STATUS_INVALID_PARAMETER);test_irql=0;
    CHECK(XwnFbAcquire(NULL,&v)==STATUS_INVALID_PARAMETER);CHECK(XwnFbAcquire(device,NULL)==STATUS_INVALID_PARAMETER);
    for(unsigned field=0;field<11;++field) {
        if(field==4||field==5||field==9||field==10) continue; /* output-only */
        v=request(); ((ULONG*)&v)[field]^=1;CHECK(XwnFbAcquire(device,&v)==STATUS_INVALID_PARAMETER);
    }
    for(unsigned i=0;i<3;++i) {v=request();CHECK(XwnFbAcquire(device,&v)==0);CHECK(!memcmp(&v,&valid,sizeof v));}
    v=request();CHECK(XwnFbAcquire((void*)2,&v)==STATUS_INVALID_PARAMETER);
    CHECK(XwnFbRelease((void*)2,(void*)(uintptr_t)valid.Address)==STATUS_INVALID_PARAMETER);
    CHECK(XwnFbRelease(device,(void*)(uintptr_t)(valid.Address+4096))==STATUS_INVALID_PARAMETER);
    CHECK(XwnFbReleaseOwner((void*)2)==STATUS_INVALID_PARAMETER);CHECK(References==3);
    References=XWN_FB_MAX_REFS;v=request();CHECK(XwnFbAcquire(device,&v)==STATUS_INVALID_PARAMETER);CHECK(References==XWN_FB_MAX_REFS);
    CHECK(XwnFbReleaseOwner(device)==0);CHECK(References==0&&Owner==NULL);CHECK(!memcmp(&Published,&valid,sizeof valid));
    v=request();CHECK(XwnFbAcquire((void*)2,&v)==0);CHECK(XwnFbRelease((void*)2,(void*)(uintptr_t)v.Address)==0);
    CHECK(XwnFbReleaseOwner(device)==0);
    pthread_t threads[8]; unsigned total=0;
    for(uintptr_t i=0;i<8;++i) CHECK(!pthread_create(&threads[i],NULL,worker,(void*)(1+i%2)));
    for(unsigned i=0;i<8;++i) {void *n;CHECK(!pthread_join(threads[i],&n));total+=(unsigned)(uintptr_t)n;}
    CHECK(total>0);CHECK(References==0&&Owner==NULL&&Ready==1);CHECK(!memcmp(&Published,&valid,sizeof valid));
    printf("{\"passed\":true,\"checks\":%u,\"concurrent_attempts\":400000,\"acquired_and_released\":%u,\"joined\":8}\n",checks,total);
}
