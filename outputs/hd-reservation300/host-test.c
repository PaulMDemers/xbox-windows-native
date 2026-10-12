/* Actual provider and layout code; NT locks/IRQL modeled by the pinned shim. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include SOURCE_PROVIDER
static int boot_owns;
BOOLEAN InbvCheckDisplayOwnership(void) { return boot_owns; }
static unsigned long checks;
#define CHECK(x) do { ++checks; if (!(x)) { fprintf(stderr,"line %d: %s\n",__LINE__,#x); abort(); } } while(0)
static XWN_FB_VIEW valid={44,2,0xe0000000,0x03700000,0x900000,1920*1080*4,1920,1080,7680,XWN_HD_HIDDEN_OFFSET,0};
static XWN_FB_VIEW request(void) { XWN_FB_VIEW v=valid;v.Address=0;return v; }
static void *worker(void *arg) {
    for(unsigned i=0;i<10000;++i) {
        XWN_FB_VIEW v=request(); NTSTATUS s=XwnFbAcquire(arg,&v);
        if(s==STATUS_SUCCESS) { assert(!memcmp(&v,&valid,sizeof v));assert(XwnFbRelease(arg,(void*)(uintptr_t)v.Address)==0); }
        else assert(s==STATUS_INVALID_PARAMETER);
    }
    return NULL;
}
int main(void) {
    CHECK(XWN_HD_FB_PHYSICAL+XWN_HD_FB_BYTES==64u*1024u*1024u);
    CHECK(XWN_HD_BOOT_BACK_BYTES==316160);
    CHECK(1920u*1080u*4u+XWN_HD_BOOT_BACK_BYTES>8u*1024u*1024u);
    const unsigned heights[]={0,1,479,480,576,720,1080,1081,0xffffffffu};
    for(unsigned w=0;w<4097;++w) for(unsigned i=0;i<sizeof heights/sizeof heights[0];++i) {
        unsigned h=heights[i];
        int oracle=w>=640&&w<=1920&&h>=480&&h<=1080&&((uint64_t)w*h*4+316160<=9u*1024u*1024u);
        CHECK(XwnHdLayoutValid(55u*1024u*1024u,9u*1024u*1024u,w,h,w*4,9u*1024u*1024u-316160)==oracle);
    }
    unsigned map[2][6]={{0,0,0,0x03700000,0,1},{1,0x03700000,0,0x900000,0,0}};
    for(unsigned row=0;row<2;++row) {
        unsigned *m=map[row];CHECK(XwnHdMapEntryValid(m[0],m[1],m[2],m[3],m[4],m[5]));
        for(unsigned j=0;j<6;++j) for(unsigned bit=0;bit<32;++bit) {
            unsigned a[6];memcpy(a,m,sizeof a);a[j]^=1u<<bit;
            CHECK(!XwnHdMapEntryValid(a[0],a[1],a[2],a[3],a[4],a[5]));
        }
    }
    XWN_FB_VIEW v=request();CHECK(XwnFbAcquire((void*)1,&v)==STATUS_DEVICE_NOT_READY);
    CHECK(!XwnFbPublish(NULL));
    for(unsigned i=0;i<11;++i) {v=valid;((ULONG*)&v)[i]=0xffffffff;CHECK(!XwnFbPublish(&v));CHECK(Ready==0);}
    v=valid;v.Version=1;CHECK(!XwnFbPublish(&v));
    v=valid;v.Physical=0x03c00000;CHECK(!XwnFbPublish(&v));
    v=valid;v.Physical=0x07700000;CHECK(!XwnFbPublish(&v));
    v=valid;v.ReservedBytes=0x400000;CHECK(!XwnFbPublish(&v));
    v=valid;v.HiddenOffset--;CHECK(!XwnFbPublish(&v));
    CHECK(XwnFbPublish(&valid));CHECK(!XwnFbPublish(&valid));
    v=request();v.Version=1;CHECK(XwnFbAcquire((void*)1,&v)==STATUS_INVALID_PARAMETER);
    v=request();v.ReservedBytes=0;CHECK(XwnFbAcquire((void*)1,&v)==STATUS_INVALID_PARAMETER);
    v=request();boot_owns=1;CHECK(XwnFbAcquire((void*)1,&v)==STATUS_DEVICE_BUSY);boot_owns=0;
    test_irql=2;CHECK(XwnFbAcquire((void*)1,&v)==STATUS_INVALID_PARAMETER);test_irql=0;
    v=request();CHECK(XwnFbAcquire((void*)1,&v)==0);CHECK(!memcmp(&v,&valid,sizeof v));
    CHECK(XwnFbRelease((void*)2,(void*)(uintptr_t)v.Address)==STATUS_INVALID_PARAMETER);
    CHECK(XwnFbRelease((void*)1,(void*)(uintptr_t)v.Address)==0);
    pthread_t t[4];for(uintptr_t i=0;i<4;++i) CHECK(!pthread_create(&t[i],NULL,worker,(void*)(i+1)));
    for(unsigned i=0;i<4;++i) CHECK(!pthread_join(t[i],NULL));
    CHECK(References==0&&Owner==NULL);CHECK(!memcmp(&Published,&valid,sizeof valid));
    printf("checks=%lu concurrent_pairs=40000\n",checks);
}
