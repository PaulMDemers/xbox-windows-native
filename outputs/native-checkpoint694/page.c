/* SPDX-License-Identifier: MIT */
#include "page.h"
#include <string.h>
static void w16(uint8_t *p,uint32_t o,uint32_t v){p[o]=(uint8_t)v;p[o+1]=(uint8_t)(v>>8);}
static void w32(uint8_t *p,uint32_t o,uint32_t v){w16(p,o,v);w16(p,o+2,v>>16);}
int page694(uint8_t *p,const uint8_t *code,uint32_t size,uint32_t end,uint32_t flat,uint32_t fault,uint32_t base,uint32_t fb){
 if(!p || !code || size!=4096 || !end || end>0x400 || flat>=end || fault>=end || (base&4095) || base<0x1000000 || base>0x1fff000 || (fb&4095) || fb>0x4000000-3686400 || (base<fb+3686400 && fb<base+4096))return 0;
 memcpy(p,code,4096);
 /* Two code selectors match native preflight's CS10 / DS18 convention. */
 w32(p,0x400,0);w32(p,0x404,0);
 w32(p,0x408,0xffff);w32(p,0x40c,0x00cf9a00);
 w32(p,0x410,0xffff);w32(p,0x414,0x00cf9a00);
 w32(p,0x418,0xffff);w32(p,0x41c,0x00cf9200);
 w16(p,0x420,31);w32(p,0x422,base+0x400);
 w32(p,0x428,base+flat);w16(p,0x42c,0x10);
 w16(p,0x430,2047);w32(p,0x432,base+0x600);
 w32(p,0x500,0x584e0694);w32(p,0x504,base);w32(p,0x508,fb);w32(p,0x50c,3686400);
 for(unsigned i=0;i<256;i++){
  uint32_t at=0x600+8*i,target=base+fault;
  w16(p,at,target);w16(p,at+2,0x10);w16(p,at+4,0x8e00);w16(p,at+6,target>>16);
 }
 return 1;
}
