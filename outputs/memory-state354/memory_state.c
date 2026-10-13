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
ULONG XwnMemoryState354(SURFOBJ *s,ULONG bytes,PVOID out)
{
 M354_VIEW v;M354_IO io={m354_reg,m354_cpuid,m354_msr,m354_read,NULL};
 PPDEV p;uint32_t *packet;
 if(bytes!=M354_BYTES||!out)return 0;
 p=XwnOwner(s);if(!p||!p->ShadowActive||!p->ShadowObject)return 0;
 packet=EngAllocMem(FL_ZERO_MEMORY,M354_BYTES,ALLOC_TAG);if(!packet)return 0;
 v.owner=(ULONG_PTR)p;v.surface=(ULONG_PTR)p->hSurfEng;
 v.object=(ULONG_PTR)p->ShadowObject;v.shadow=(ULONG_PTR)p->ShadowBits;
 v.screen=(ULONG_PTR)p->ScreenPtr;v.width=p->ScreenWidth;
 v.height=p->ScreenHeight;v.pitch=p->ScreenDelta;v.bpp=p->BitsPerPixel;
 _SEH2_TRY { m354_capture(&v,&io,packet); }
 _SEH2_EXCEPT(1) { packet[3]|=M354_READ;packet[178]=_SEH2_GetExceptionCode(); }
 _SEH2_END;
 /* GDI retains the submitted surface/PDEV for the DDI call. Membership is not
  * an MM/TLB lock; no lock is held across faultable reads or CPU instructions. */
 if(XwnOwner(s)!=p||!p->ShadowActive||(ULONG_PTR)p->ShadowBits!=v.shadow||
    (ULONG_PTR)p->ScreenPtr!=v.screen||(ULONG_PTR)p->ShadowObject!=v.object||
    (ULONG_PTR)p->hSurfEng!=v.surface||p->ScreenWidth!=v.width||
    p->ScreenHeight!=v.height||p->ScreenDelta!=v.pitch||p->BitsPerPixel!=v.bpp)
  packet[3]|=M354_OWNER;
 memcpy(out,packet,M354_BYTES);EngFreeMem(packet);return 1;
}
