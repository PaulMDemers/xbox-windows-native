/* SPDX-License-Identifier: MIT. Deterministic builder, no API/device accesses. */
#include "page.h"
#include <string.h>
static void w16(uint8_t *p,uint32_t o,uint32_t v){p[o]=(uint8_t)v;p[o+1]=(uint8_t)(v>>8);}
static void w32(uint8_t *p,uint32_t o,uint32_t v){w16(p,o,v);w16(p,o+2,v>>16);}
static uint32_t r32(const uint8_t *p,uint32_t o){return (uint32_t)p[o]|((uint32_t)p[o+1]<<8)|((uint32_t)p[o+2]<<16)|((uint32_t)p[o+3]<<24);}
int page705(uint8_t *p,const uint8_t *code,const uint32_t *m,const uint8_t *payload,
 uint32_t size,const struct reloc705 *rel,uint32_t count,uint32_t base,uint32_t fb)
{
 if(!p||!code||!m||!payload||!rel||!m[0]||m[0]>0x800||m[1]>=m[0]||m[2]>=m[0]||m[3]>=m[0]||
 size!=9916||m[4]>=size||count!=26||(base&4095)||base<0x1000000||base>0x1ff8000||
 (fb&4095)||fb<0x2000000||fb>0x4000000-3686400||
 (fb<0x2800000&&fb+3686400>0x2600000))return 0;
 for(unsigned i=0;i<count;++i){
  if(rel[i].offset>size-4||rel[i].value<0x100000||rel[i].value>=0x100000+size||
   r32(payload,rel[i].offset)!=rel[i].value)return 0;
  for(unsigned j=0;j<i;++j)if(rel[i].offset<rel[j].offset+4&&rel[j].offset<rel[i].offset+4)return 0;
 }
 /* No caller output changes until all argument/relocation checks have passed. */
 memset(p,0xa5,32768);memcpy(p,code,4096);memcpy(p+4096,payload,size);
 for(unsigned i=0;i<count;++i)w32(p,4096+rel[i].offset,rel[i].value+base+4096-0x100000);
 memset(p+0x800,0,0x800);memset(p+0x5000,0,0x200);
 /* Own descriptors start with accessed bits set; the CPU may otherwise set
  * these during segment loads, invalidating an identity-copy checksum. */
 w32(p,0x808,0xffff);w32(p,0x80c,0xcf9b00);
 w32(p,0x810,0xffff);w32(p,0x814,0xcf9b00);
 w32(p,0x818,0xffff);w32(p,0x81c,0xcf9300);
 w16(p,0x820,31);w32(p,0x822,base+0x800);
 w32(p,0x828,base+m[1]);w16(p,0x82c,0x10);
 w16(p,0x830,2047);w32(p,0x832,base+0x4800);
 w32(p,0x840,0x584e0705);w32(p,0x844,base);w32(p,0x848,fb);w32(p,0x84c,3686400);
 w32(p,0x850,base+4096+m[4]);
 for(unsigned i=0;i<256;++i){uint32_t at=0x4800+8*i,target=base+m[2];
  w16(p,at,target);w16(p,at+2,0x10);w16(p,at+4,0x8e00);w16(p,at+6,target>>16);
 }
 /* request704: physical FB; booleans remain independently checked obligations. */
 const uint32_t request[]={0x4000000,fb,3686400,3686400,1,1,1280,720,5120,32,1,1,0x80000,3375000,1};
 for(unsigned i=0;i<15;++i)w32(p,0x5000+4*i,request[i]);
 uint32_t sum=0;
 for(unsigned i=0;i<0x6000;i+=4)if(i!=0x854&&(i<0x880||i>=0x900))sum+=r32(p,i);
 w32(p,0x854,sum);
 return 1;
}
