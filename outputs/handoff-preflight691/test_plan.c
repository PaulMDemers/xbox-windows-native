/* SPDX-License-Identifier: MIT */
#include <assert.h>
#include <stdio.h>
#include "plan.h"
int main(void){
 struct plan691 p={0x1e00000,0x100000,0x100000,1,0x1fff000,4096,4096,1,0,0x1fff000,0x1fff000,4096,0x1000000,0x1000fff,0x3c5c000,3686400},q;
 assert(admit691(&p)==0);assert(admit691(0)==31);
 q=p;q.alias_physical=p.stub;q.alias_last=p.stub+4095;assert(admit691(&q)==0);
 q=p;q.status=0xc0000018;assert(admit691(&q)&4);
 q=p;q.returned=0x1ff0000;q.region_size=65536;assert(admit691(&q)&4);
 q=p;q.source=0;assert(admit691(&q)&1);
 q=p;q.stub=0;assert(admit691(&q)&2);
 q=p;q.source=0xfffff000;assert(admit691(&q)&1);
 q=p;q.stub=0xfffff000;assert(admit691(&q)&2);
 q=p;q.alias_physical=0xfffff000;q.alias_last=0xffffffff;assert(admit691(&q)&4);
 q=p;q.source_allocation--;assert(admit691(&q)&1);
 q=p;q.stub_allocation--;assert(admit691(&q)&2);
 q=p;q.source_contiguous=0;assert(admit691(&q)&1);
 q=p;q.stub_contiguous=0;assert(admit691(&q)&2);
 q=p;q.requested--;assert(admit691(&q)&4);
 q=p;q.region_size--;assert(admit691(&q)&4);
 q=p;q.alias_last--;assert(admit691(&q)&4);
 q=p;q.source_size--;assert(admit691(&q)&1);
 q=p;q.stub_size--;assert(admit691(&q)&2);
 q=p;q.alias_physical=p.source;q.alias_last=p.source+4095;assert(admit691(&q)==8);
 q=p;q.stub=p.source;q.requested=q.returned=q.stub;assert(admit691(&q)==8);
 q=p;q.framebuffer=p.stub;assert(admit691(&q)==8);
 q=p;q.framebuffer=p.alias_physical;assert(admit691(&q)==8);
 q=p;q.framebuffer=0xfffff000;assert(admit691(&q)&16);
 q=p;q.framebuffer_size--;assert(admit691(&q)&16);
 for(unsigned i=1;i<4096;i++){
  q=p;q.source+=i;assert(admit691(&q)&1);
  q=p;q.stub+=i;assert(admit691(&q)&2);
  q=p;q.alias_physical+=i;q.alias_last+=i;assert(admit691(&q)&4);
 }
 puts("PASS admission failures, overlap guards, identity/dual mapping acceptance and 12285 unaligned cases");return 0;
}
