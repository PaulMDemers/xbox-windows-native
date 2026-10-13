/* Actual wrapper body; privileged reads, GDI lifetime/pixels and SEH modeled. */
#define main core_main
#include "host.c"
#undef main
typedef uint32_t ULONG;typedef uintptr_t ULONG_PTR;typedef void*PVOID;typedef int BOOL;
typedef struct {int unused;} SURFOBJ;
typedef struct {int ShadowActive;void *ShadowObject,*hSurfEng,*ShadowBits,*ScreenPtr;ULONG ScreenWidth,ScreenHeight,ScreenDelta,BitsPerPixel;} PDEV,*PPDEV;
#define FL_ZERO_MEMORY 1
#define ALLOC_TAG 1
#define _SEH2_TRY if(1)
#define _SEH2_EXCEPT(x) else if(0)
#define _SEH2_GetExceptionCode() 0
#define _SEH2_END
static MODEL M;static PDEV P;static unsigned warmcalls,allocs,frees,owner_calls;
static int badowner,ownerchange,allocationfail,nonpresent,badpixels;
static PPDEV XwnOwner(SURFOBJ*s){(void)s;owner_calls++;return badowner||(ownerchange&&owner_calls>1)?NULL:&P;}
static void *EngAllocMem(unsigned f,unsigned b,unsigned t){(void)f;(void)t;if(allocationfail)return NULL;allocs++;return calloc(1,b);}
static void EngFreeMem(void*p){frees++;free(p);}
static ULONG XwnCheckScanout(PPDEV p){assert(p==&P);warmcalls++;nonpresent=0;return badpixels;}
static int m354_reg(void*c,unsigned n,uint32_t*v){(void)c;return reg(&M,n,v);}
static int m354_cpuid(void*c,uint32_t n,uint32_t*v){(void)c;return cpuid(&M,n,v);}
static int m354_msr(void*c,uint32_t n,uint32_t*v){(void)c;return msr(&M,n,v);}
static int m354_read(void*c,uint32_t n,uint32_t*v){int ok;(void)c;ok=readword(&M,n,v);if(ok&&nonpresent&&n==0xc0384000)*v&=~1u;return ok;}
#include "actual_wrapper.inc"
static void reset(void){memset(&M,0,sizeof(M));M.features=0x11020;M.count=8;memset(&P,0,sizeof(P));
 P.ShadowActive=1;P.ShadowObject=(void*)0x80003000;P.hSurfEng=(void*)0x1050034;
 P.ShadowBits=(void*)0xe1000123;P.ScreenPtr=(void*)0xfb000000;
 P.ScreenWidth=1920;P.ScreenHeight=1080;P.ScreenDelta=7680;P.BitsPerPixel=32;
 warmcalls=owner_calls=0;badowner=ownerchange=allocationfail=nonpresent=badpixels=0;
}
int main(int argc,char**argv){SURFOBJ s;uint32_t *p=malloc(2*M354_BYTES);unsigned checks=0;assert(p);
 core_main(1,NULL);
 reset();CHECK(XwnMemoryState357(&s,2*M354_BYTES,p)==1);CHECK(warmcalls==1&&!p[3]&&!p[M354_WORDS+3]);CHECK(p[M354_WORDS+1]==357&&p[M354_WORDS+181]==1&&p[M354_WORDS+180]==2073600);
 reset();nonpresent=1;CHECK(XwnMemoryState357(&s,2*M354_BYTES,p)==1);CHECK(p[3]==M354_PAGE&&warmcalls==1&&!p[M354_WORDS+3]);
 if(argc==2){FILE*f=fopen(argv[1],"wb");assert(f);assert(fwrite(p,1,2*M354_BYTES,f)==2*M354_BYTES);assert(!fclose(f));}
 reset();badpixels=1;CHECK(XwnMemoryState357(&s,2*M354_BYTES,p)==1);CHECK(p[M354_WORDS+3]==256&&p[M354_WORDS+179]==1);
 reset();ownerchange=1;CHECK(XwnMemoryState357(&s,2*M354_BYTES,p)==1);CHECK((p[3]&M354_OWNER)&&(p[M354_WORDS+3]&M354_OWNER));
 reset();M.absent=1;CHECK(XwnMemoryState357(&s,2*M354_BYTES,p)==1);CHECK(!warmcalls&&p[3]==M354_PAGE&&p[M354_WORDS+3]==512);
 reset();M.user=1;CHECK(XwnMemoryState357(&s,2*M354_BYTES,p)==1);CHECK(!warmcalls&&p[M354_WORDS+3]==512);
 reset();M.pae=1;CHECK(XwnMemoryState357(&s,2*M354_BYTES,p)==1);CHECK(!warmcalls&&p[3]==M354_CPU&&p[M354_WORDS+3]==512);
 reset();M.fail=1;CHECK(XwnMemoryState357(&s,2*M354_BYTES,p)==1);CHECK(!warmcalls&&p[3]==M354_READ);
 reset();allocationfail=1;CHECK(!XwnMemoryState357(&s,2*M354_BYTES,p));CHECK(!warmcalls);
 reset();badowner=1;CHECK(!XwnMemoryState357(&s,2*M354_BYTES,p));
 reset();CHECK(!XwnMemoryState357(&s,M354_BYTES,p));CHECK(!XwnMemoryState357(&s,2*M354_BYTES,NULL));CHECK(allocs==frees);
 printf("{\"wrapper_checks\":%u,\"allocations\":%u,\"frees\":%u,\"models\":\"CPU/PTE/GDI pixels/SEH\"}\n",checks,allocs,frees);free(p);return 0;
}
