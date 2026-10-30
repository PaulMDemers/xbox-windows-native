/* SPDX-License-Identifier: MIT. Deterministic builder, no API/device accesses. */
#include "page.h"
#include <string.h>
static void w16(uint8_t *p,uint32_t o,uint32_t v){p[o]=(uint8_t)v;p[o+1]=(uint8_t)(v>>8);}
static void w32(uint8_t *p,uint32_t o,uint32_t v){w16(p,o,v);w16(p,o+2,v>>16);}
static uint32_t r32(const uint8_t *p,uint32_t o){return (uint32_t)p[o]|((uint32_t)p[o+1]<<8)|((uint32_t)p[o+2]<<16)|((uint32_t)p[o+3]<<24);}
int page829(uint8_t *p,const uint8_t *code,const uint32_t *m,
 uint32_t base,uint32_t fb,uint32_t source,uint32_t size,uint32_t firmware_sum)
{
 if(!p||!code||!m||!m[0]||m[0]>0x800||m[1]>=m[0]||m[2]>=m[0]||m[3]>=m[0]||
 (base&4095)||base<0x1000000||base>0x1ff6000||
 (fb&4095)||fb<0x2800000||fb>0x4000000-3686400||
 (source&4095)||source<0x210000||source>=0x2000000||size<0x1000||size>0xf0000||
 (size&3)||size>0x2000000-source||(source<base+40960&&base<source+size))return 0;
 memset(p,0xa5,40960);memcpy(p,code,2304);
 memset(p+0x800,0,0x100);memset(p+0x77c0,0,0xe94);
 /* Own descriptors start with accessed bits set; the CPU may otherwise set
  * these during segment loads, invalidating an identity-copy checksum. */
 w32(p,0x808,0xffff);w32(p,0x80c,0xcf9b00);
 w32(p,0x810,0xffff);w32(p,0x814,0xcf9b00);
 w32(p,0x818,0xffff);w32(p,0x81c,0xcf9300);
 w16(p,0x820,31);w32(p,0x822,base+0x800);
 w32(p,0x829,base+m[1]);w16(p,0x82c,0x10);
 w16(p,0x830,2047);w32(p,0x832,base+0x8700);
 w32(p,0x840,0x584e0705);w32(p,0x844,base);w32(p,0x848,fb);w32(p,0x84c,3686400);
 w32(p,0x858,source);w32(p,0x85c,size);w32(p,0x860,firmware_sum);
 for(unsigned i=0;i<256;++i){uint32_t at=0x8700+8*i,target=base+m[2];
  w16(p,at,target);w16(p,at+2,0x10);w16(p,at+4,0x8e00);w16(p,at+6,target>>16);
 }
 uint32_t sum=0;
 for(unsigned i=0;i<0x8f00;i+=4)if(i!=0x854&&(i<0x880||i>=0x900))sum+=r32(p,i);
 w32(p,0x854,sum);
 return 1;
}
