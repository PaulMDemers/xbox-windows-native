/* SPDX-License-Identifier: MIT; complete32KiB allocation and eight alias pages. */
#include "plan.h"
static int span(uint32_t a,uint32_t n,uint32_t lo,uint32_t hi){return n&&a>=lo&&a<hi&&n<=hi-a;}
static int overlap(uint32_t a,uint32_t n,uint32_t b,uint32_t m){return a<b+m&&b<a+n;}
int reservation_contains705(uint32_t requested,uint32_t returned,uint32_t size)
{return !(requested&4095)&&!(returned&4095)&&!(size&4095)&&size>=40960&&size<=131072&&
 returned<=requested&&span(returned,size,0,0x80000000)&&requested-returned<=size-40960;}
uint32_t admit705(const struct plan705 *p)
{
 if(!p)return 31;
 uint32_t e=0;
 if(p->source_size!=0x100000||p->source_allocation<p->source_size||p->source_contiguous!=1||
 (p->source&4095)||!span(p->source,p->source_allocation,0x200000,0x2000000))e|=1;
 if(p->stub_size!=40960||p->stub_allocation<40960||p->stub_contiguous!=1||
 (p->stub&4095)||!span(p->stub,p->stub_allocation,0x1000000,0x2000000))e|=2;
 if(p->status&0x80000000||p->requested!=p->stub||!reservation_contains705(p->requested,p->returned,p->region_size))e|=4;
 for(unsigned i=0;i<10;++i)if((p->alias[i]&4095)||!span(p->alias[i],4096,0,0x4000000)||p->alias_last[i]!=p->alias[i]+4095)e|=4;
 if(p->framebuffer_size!=3686400||p->framebuffer_allocation<p->framebuffer_size||
 (p->framebuffer&4095)||!span(p->framebuffer,p->framebuffer_allocation,0x2000000,0x4000000))e|=16;
 if(!e){
  if(overlap(p->source,p->source_allocation,p->stub,p->stub_allocation)||
   overlap(p->framebuffer,p->framebuffer_allocation,0x2600000,0x200000))e|=8;
  for(unsigned i=0;i<10;++i){
   if(overlap(p->alias[i],4096,p->source,p->source_allocation)||
    overlap(p->alias[i],4096,p->framebuffer,p->framebuffer_allocation)||
    (overlap(p->alias[i],4096,p->stub,p->stub_allocation)&&p->alias[i]!=p->stub+4096*i))e|=8;
   for(unsigned j=0;j<i;++j)if(p->alias[i]==p->alias[j])e|=8;
  }
 }
 return e;
}
