/* SPDX-License-Identifier: GPL-2.0-or-later */
#include "framebuf.h"
#include <pseh/pseh2.h>
#include "capture.h"
static int m354_reg(void *ctx,unsigned n,uint32_t *v)
{
 unsigned short cs;(void)ctx;
 switch(n){
 case 0:__asm__ __volatile__("mov %%cr0,%0":"=r"(*v));break;
 case 1:__asm__ __volatile__("mov %%cr3,%0":"=r"(*v));break;
 case 2:__asm__ __volatile__("mov %%cr4,%0":"=r"(*v));break;
 case 3:__asm__ __volatile__("mov %%cs,%0":"=r"(cs));*v=cs;break;
 default:return 0;
 }return 1;
}
static int m354_cpuid(void *ctx,uint32_t leaf,uint32_t *o)
{
 (void)ctx;__asm__ __volatile__("cpuid":"=a"(o[0]),"=b"(o[1]),"=c"(o[2]),"=d"(o[3]):"a"(leaf),"c"(0):"memory");return 1;
}
static int m354_msr(void *ctx,uint32_t index,uint32_t *o)
{
 (void)ctx;__asm__ __volatile__("rdmsr":"=a"(o[0]),"=d"(o[1]):"c"(index):"memory");return 1;
}
static int m354_read(void *ctx,uint32_t address,uint32_t *o)
{
 (void)ctx;*o=*(volatile uint32_t *)(ULONG_PTR)address;return 1;
}

#include "bandwidth.h"
static void b361_ram(B361_CONTEXT *c)
{
 unsigned y;LONGLONG a=-1,b=-1;ULONGLONG ticks;
 EngQueryPerformanceCounter(&a);
 for(y=0;y<B361_ROWS;y++)memmove(c->scratch+y*B361_ROW,
  (void*)(c->shadow+c->offset+y*c->pitch),B361_ROW);
 EngQueryPerformanceCounter(&b);
 b361_q(c->record+16,a);b361_q(c->record+18,b);
 if(!b361_ticks(a,b,&ticks))c->record[2]|=4;
}
static void b361_map(PPDEV p,B361_CONTEXT*c,unsigned after)
{
 M354_VIEW v;M354_IO io={m354_reg,m354_cpuid,m354_msr,m354_read,NULL};
 v.owner=(ULONG_PTR)p;v.surface=(ULONG_PTR)p->hSurfEng;
 v.object=(ULONG_PTR)p->ShadowObject;v.shadow=(ULONG_PTR)c->scratch;
 v.screen=(ULONG_PTR)p->ScreenPtr;v.width=960;v.height=540;v.pitch=3840;v.bpp=32;
 m354_capture(&v,&io,c->record+B361_META+after*M354_WORDS);
 if(c->record[B361_META+after*M354_WORDS+3])c->record[2]|=8;
}
VOID XwnBandwidthBegin(PPDEV p,const RECTL*r,B361_CONTEXT*c)
{
 unsigned i;LONGLONG a=-1,b=-1,f=-1;ULONGLONG ticks,lo=~(ULONGLONG)0,hi=0;
 RtlZeroMemory(c,sizeof(*c));
 if(p->ScreenWidth!=1920||p->ScreenHeight!=1080||p->ScreenDelta!=7680||
    p->BitsPerPixel!=32||!p->ShadowActive||!p->ShadowObject||
    r->left<0||r->top<0||r->right>1920||r->bottom>1080||
    r->right-r->left!=960||r->bottom-r->top!=540)return;
 if(!XwnBandwidthReserve(p,c))return;
 c->record[0]=361;c->record[1]=c->slot;c->record[3]=c->slot&1;
 c->shadow=(ULONG_PTR)p->ShadowBits;c->screen=(ULONG_PTR)p->ScreenPtr;
 c->pitch=p->ScreenDelta;c->offset=r->top*c->pitch+r->left*4;
 c->record[4]=(ULONG_PTR)p;c->record[5]=c->shadow;c->record[6]=c->screen;
 c->record[7]=c->offset;c->record[8]=c->pitch;
 c->record[9]=B361_ROW;c->record[10]=B361_ROWS;c->record[11]=B361_LENGTH;
 _SEH2_TRY {
  c->allocation=EngAllocMem(FL_ZERO_MEMORY,B361_LENGTH+2*B361_GUARD,ALLOC_TAG);
  if(!c->allocation)c->record[2]|=1;
  else {
   c->scratch=c->allocation+B361_GUARD;c->record[12]=(ULONG_PTR)c->scratch;
   for(i=0;i<B361_GUARD;i++) {c->allocation[i]=(BYTE)(i^0xa5);
    c->allocation[B361_GUARD+B361_LENGTH+i]=(BYTE)(i^0x5a);}
   EngQueryPerformanceFrequency(&f);b361_q(c->record+14,f);
   if(f<=0)c->record[2]|=4;
   for(i=0;i<32;i++) {
    EngQueryPerformanceCounter(&a);EngQueryPerformanceCounter(&b);
    if(!b361_ticks(a,b,&ticks))c->record[2]|=4;
    else{if(ticks<lo)lo=ticks;if(ticks>hi)hi=ticks;}
   }
   c->record[24]=32;b361_q(c->record+25,lo);b361_q(c->record+27,hi);
   b361_map(p,c,0);
   if(!c->record[2]&&!(c->slot&1))b361_ram(c);
  }
 } _SEH2_EXCEPT(1) {c->record[2]|=2;c->record[13]=_SEH2_GetExceptionCode();} _SEH2_END;
}
VOID XwnBandwidthEnd(PPDEV p,B361_CONTEXT*c,LONGLONG uploadBegin,LONGLONG uploadEnd)
{
 ULONGLONG ticks;
 if(!c->active)return;
 b361_q(c->record+20,uploadBegin);b361_q(c->record+22,uploadEnd);
 if(!b361_ticks(uploadBegin,uploadEnd,&ticks))c->record[2]|=4;
 _SEH2_TRY {
  if(!c->record[2]) {
   if(c->slot&1)b361_ram(c);
   c->record[29]=b361_compare(c->scratch,(void*)(c->shadow+c->offset),B361_ROW,B361_ROWS,c->pitch);
   c->record[30]=b361_compare(c->scratch,(void*)(c->screen+c->offset),B361_ROW,B361_ROWS,c->pitch);
   c->record[31]=b361_guards(c->allocation);
   if(c->record[29]||c->record[30]||c->record[31])c->record[2]|=16;
   b361_map(p,c,1);
  }
 } _SEH2_EXCEPT(1) {c->record[2]|=2;c->record[13]=_SEH2_GetExceptionCode();} _SEH2_END;
 if((ULONG_PTR)p->ShadowBits!=c->shadow||(ULONG_PTR)p->ScreenPtr!=c->screen||
    p->ScreenDelta!=c->pitch||!p->ShadowActive)c->record[2]|=32;
 if(c->allocation)EngFreeMem(c->allocation);
 c->record[32]=1;XwnBandwidthPublish(p,c);
}
