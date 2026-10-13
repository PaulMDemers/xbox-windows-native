
#include <assert.h>
#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include "bandwidth.h"
#define M354_WORDS 16640u
#define M354_META 256u
typedef uint32_t ULONG;typedef uintptr_t ULONG_PTR;typedef void*PVOID;typedef int BOOL;
typedef unsigned char BYTE;typedef int64_t LONGLONG;typedef uint64_t ULONGLONG;
#define VOID void
#define FL_ZERO_MEMORY 1
#define ALLOC_TAG 1
#define _SEH2_TRY if(1)
#define _SEH2_EXCEPT(x) else if(0)
#define _SEH2_GetExceptionCode() 0
#define _SEH2_END
#define RtlZeroMemory(p,n) memset(p,0,n)
typedef struct {int left,top,right,bottom;} RECTL;
typedef struct {unsigned ScreenWidth,ScreenHeight,ScreenDelta,BitsPerPixel;int ShadowActive;void*ShadowObject,*hSurfEng,*ShadowBits,*ScreenPtr;B361_STATE Bandwidth;} PDEV,*PPDEV;
typedef struct {uint32_t owner,surface,object,shadow,screen,width,height,pitch,bpp;} M354_VIEW;
typedef struct {void *a,*b,*c,*d,*e;} M354_IO;
#define m354_reg NULL
#define m354_cpuid NULL
#define m354_msr NULL
#define m354_read NULL
static unsigned checks,allocs,frees,maps,failalloc,failmap,failtimer,step;
static int64_t clockvalue=100;
#define CHECK(x) do{checks++;assert(x);}while(0)
static void EngQueryPerformanceCounter(LONGLONG*p){clockvalue+=step;*p=failtimer?-1:clockvalue;}
static void EngQueryPerformanceFrequency(LONGLONG*p){*p=1000000;}
static void*EngAllocMem(unsigned f,unsigned b,unsigned t){(void)f;(void)t;if(failalloc)return NULL;allocs++;return calloc(1,b);}
static void EngFreeMem(void*p){frees++;free(p);}
static void m354_capture(const M354_VIEW*v,M354_IO*io,uint32_t*o){(void)io;CHECK(v->width==960&&v->height==540&&v->pitch==3840);maps++;o[3]=failmap;}
static int XwnBandwidthReserve(PPDEV p,B361_CONTEXT*c){if(p->Bandwidth.issued>=4)return 0;c->slot=p->Bandwidth.issued++;c->active=1;c->record=p->Bandwidth.words[c->slot];return 1;}
static void XwnBandwidthPublish(PPDEV p,B361_CONTEXT*c){p->Bandwidth.published|=1u<<c->slot;}
#include "actual.inc"
static void reset(PPDEV p){memset(&p->Bandwidth,0,sizeof(p->Bandwidth));failalloc=failmap=failtimer=0;step=1;maps=0;}
int main(void){unsigned i,j;uint64_t n;PDEV*p=calloc(1,sizeof(*p));B361_CONTEXT c;RECTL r={32,18,992,558};
 CHECK(p);p->ScreenWidth=1920;p->ScreenHeight=1080;p->ScreenDelta=7680;p->BitsPerPixel=32;p->ShadowActive=1;p->ShadowObject=p;p->hSurfEng=p;
 p->ShadowBits=malloc(8294400);p->ScreenPtr=malloc(8294400);CHECK(p->ShadowBits&&p->ScreenPtr);
 for(i=0;i<8294400;i++)((BYTE*)p->ShadowBits)[i]=(BYTE)(i*37+(i>>11));
 memcpy(p->ScreenPtr,p->ShadowBits,8294400);
 reset(p);
 for(i=0;i<4;i++){XwnBandwidthBegin(p,&r,&c);CHECK(c.active&&c.slot==i);XwnBandwidthEnd(p,&c,100,200);CHECK(!c.record[2]&&c.record[32]&&c.record[24]==32);CHECK(p->Bandwidth.published==((1u<<(i+1))-1));}
 XwnBandwidthBegin(p,&r,&c);CHECK(!c.active);CHECK(maps==8);
 reset(p);failalloc=1;XwnBandwidthBegin(p,&r,&c);XwnBandwidthEnd(p,&c,100,200);CHECK(c.record[2]==1&&c.record[32]);
 reset(p);failmap=1;XwnBandwidthBegin(p,&r,&c);XwnBandwidthEnd(p,&c,100,200);CHECK(c.record[2]==8&&c.record[32]);
 reset(p);failtimer=1;XwnBandwidthBegin(p,&r,&c);XwnBandwidthEnd(p,&c,100,200);CHECK(c.record[2]==4&&c.record[32]);
 for(j=0;j<2;j++)for(i=0;i<64;i++){reset(p);XwnBandwidthBegin(p,&r,&c);c.allocation[j?(64+B361_LENGTH+i):i]^=1;XwnBandwidthEnd(p,&c,100,200);CHECK(c.record[31]==1&&(c.record[2]&16));}
 reset(p);XwnBandwidthBegin(p,&r,&c);c.scratch[25]^=1;XwnBandwidthEnd(p,&c,100,200);CHECK(c.record[29]==1&&c.record[30]==1&&(c.record[2]&16));
 reset(p);XwnBandwidthBegin(p,&r,&c);((BYTE*)p->ScreenPtr)[c.offset+17]^=1;XwnBandwidthEnd(p,&c,100,200);CHECK(c.record[29]==0&&c.record[30]==1&&(c.record[2]&16));((BYTE*)p->ScreenPtr)[c.offset+17]^=1;
 reset(p);XwnBandwidthBegin(p,&r,&c);XwnBandwidthEnd(p,&c,100,-1);CHECK(c.record[2]==4&&c.record[32]);
 reset(p);r.left=-1;XwnBandwidthBegin(p,&r,&c);CHECK(!c.active);r.left=32;
 for(i=0;i<1000;i++){CHECK(b361_ticks(i,i+1,&n)&&n==1);CHECK(!b361_ticks(i+1,i,&n));}
 CHECK(!b361_ticks(-1,0,&n));CHECK(b361_ticks(0,INT64_MAX,&n)&&n==INT64_MAX);CHECK(allocs==frees);
 printf("{\"checks\":%u,\"allocations\":%u,\"frees\":%u,\"scope\":\"Actual adapter/copy/verification; modeled GDI, clock, PTE, publication and SEH\"}\n",checks,allocs,frees);
 free(p->ShadowBits);free(p->ScreenPtr);free(p);return 0;}
