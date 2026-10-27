/* SPDX-License-Identifier: MIT */
#include "plan.h"
static int span(uint32_t a,uint32_t n,uint32_t lo,uint32_t hi){return n && a>=lo && a<hi && n<=hi-a;}
static int overlap(uint32_t a,uint32_t n,uint32_t b,uint32_t m){return a<b+m && b<a+n;}
int reservation_contains694(uint32_t requested,uint32_t returned,uint32_t size){
 return !(requested&4095) && !(returned&4095) && !(size&4095) &&
 size>=4096 && size<=65536 && returned<=requested &&
 span(returned,size,0,0x80000000) && requested-returned<=size-4096;
}
uint32_t admit694(const struct plan694 *p){
 if(!p)return 31;
 uint32_t e=0;
 if(p->source_size!=0x100000 || p->source_allocation<p->source_size || !p->source_contiguous || p->source%4096 || !span(p->source,p->source_size,0x200000,0x2000000))e|=1;
 if(p->stub_size!=4096 || p->stub_allocation<4096 || !p->stub_contiguous || p->stub%4096 || !span(p->stub,4096,0x1000000,0x2000000))e|=2;
 if(p->status&0x80000000 || p->requested!=p->stub || !reservation_contains694(p->requested,p->returned,p->region_size) || p->alias_physical%4096 || !span(p->alias_physical,4096,0,0x4000000) || p->alias_last!=p->alias_physical+4095)e|=4;
 if(p->framebuffer_size!=3686400 || p->framebuffer%4096 || !span(p->framebuffer,p->framebuffer_size,0,0x4000000))e|=16;
 if(!e && (overlap(p->source,p->source_size,p->stub,4096) || overlap(p->source,p->source_size,p->alias_physical,4096) || overlap(p->source,p->source_size,p->framebuffer,p->framebuffer_size) || overlap(p->stub,4096,p->framebuffer,p->framebuffer_size) || overlap(p->alias_physical,4096,p->framebuffer,p->framebuffer_size)))e|=8;
 return e;
}
