/* SPDX-License-Identifier: MIT */
#include "page.h"
#include <string.h>
static void w16(uint8_t *p,uint32_t o,uint32_t v){p[o]=(uint8_t)v;p[o+1]=(uint8_t)(v>>8);}
static void w32(uint8_t *p,uint32_t o,uint32_t v){w16(p,o,v);w16(p,o+2,v>>16);}
int page697(uint8_t *p,const uint8_t *code,uint32_t size,uint32_t end,uint32_t flat,uint32_t fault,uint32_t base,uint32_t fb){
 if(!p || !code || size!=4096 || !end || end>0x4c0 || flat>=end || fault>=end || (base&4095) || base<0x1000000 || base>0x1fff000 || (fb&4095) || fb>0x4000000-3686400 || (base<fb+3686400 && fb<base+4096))return 0;
 memcpy(p,code,4096);
 /* Two code selectors match native preflight's CS10 / DS18 convention. */
 w32(p,0x4c0,0);w32(p,0x4c4,0);
 w32(p,0x4c8,0xffff);w32(p,0x4cc,0xcf9a00);
 w32(p,0x4d0,0xffff);w32(p,0x4d4,0xcf9a00);
 w32(p,0x4d8,0xffff);w32(p,0x4dc,0xcf9200);
 w16(p,0x4e0,31);w32(p,0x4e2,base+0x4c0);
 w32(p,0x4e8,base+flat);w16(p,0x4ec,0x10);
 w16(p,0x4f0,2047);w32(p,0x4f2,base+0x600);
 w32(p,0x500,0x584e0697);w32(p,0x504,base);w32(p,0x508,fb);w32(p,0x50c,3686400);
 for(unsigned i=0;i<256;i++){
  uint32_t at=0x600+8*i,target=base+fault;
  w16(p,at,target);w16(p,at+2,0x10);w16(p,at+4,0x8e00);w16(p,at+6,target>>16);
 }
 return 1;
}
