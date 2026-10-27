/* SPDX-License-Identifier: GPL-2.0-or-later
 * Experimental geometry substage only; not a complete mode initializer.
 * Retain exact700 geometry math; validate bounds and inherited context first,
 * set noninterlaced scanout explicitly, use PCRTC_START +0x800, then read back.
 * Never write clocks, memory-controller settings, interrupt status or enables.
 */
#include "geometry.h"
#include "gpu_types.h"
extern void SetGPURegister(const GPU_PARAMETER *,uint8_t *);
static uint32_t r32(volatile uint8_t *g,unsigned off)
{return *(volatile uint32_t *)(g+off);}
static void w32(volatile uint8_t *g,unsigned off,uint32_t n)
{*(volatile uint32_t *)(g+off)=n;}
static uint8_t cr(volatile uint8_t *g,uint8_t i)
{g[0x6013d4]=i;return g[0x6013d5];}
static void cw(volatile uint8_t *g,uint8_t i,uint8_t n)
{g[0x6013d4]=i;g[0x6013d5]=n;}
static uint32_t pitch(volatile uint8_t *g)
{return (cr(g,0x13)|((cr(g,0x19)&0xe0)<<3)|((cr(g,0x25)&0x20)<<6))<<3;}
int bounds702(const struct request702 *r)
{
 if(!r||r->ram!=0x04000000||r->base<0x02000000||r->base>=r->ram||
    (r->base&4095)||r->allocation<3686400||r->allocation>r->ram-r->base||
    r->checked_bytes<3686400||r->checked_bytes>r->allocation||
    r->contiguous!=1||r->alias_checked!=1||r->width!=1280||r->height!=720||
    r->pitch!=5120||r->depth!=32||r->blank_confirmed!=1)return 0;
 /* Source/stub allocations stay below32MiB; preserve legacy diagnostic range.
  * Check the whole allocation, not just the new 1,382,400-byte visible image. */
 if(r->base<0x02800000 && 0x02600000<r->base+r->allocation)return 0;
 return 1;
}
static int clocks_unchanged(volatile uint8_t *g)
{
 /* Exact701 context admission only. These observed values are never written
  * and are not asserted to be a480p clock programming recipe. */
 return r32(g,0x680508)==0x0003c20d && r32(g,0x68050c)==0x100a0400 &&
        r32(g,0x680880)==0x21101100 && r32(g,0x100200)==0x03070003 &&
        r32(g,0x600804)==3;
}
int geometry702(const struct request702 *r,volatile uint8_t *g,struct result702 *o)
{
 uint32_t flags;uint8_t saved;
 if(!o)return G702_ARGUMENT;
 *o=(struct result702){0};
 if(!r||!g){o->error=G702_ARGUMENT;return o->error;}
 if(!bounds702(r)){o->error=G702_LAYOUT;return o->error;}
 __asm__ volatile("pushfl; popl %0":"=r"(flags));
 if(flags&0x200){o->error=G702_IF;return o->error;}
 saved=g[0x6013d4];o->phase=1;
 if(!clocks_unchanged(g)||r32(g,0x600800)!=r->base||
    r32(g,0x680838)!=1279||r32(g,0x680818)!=719||
    pitch(g)!=5120||cr(g,0x28)!=0x83||cr(g,0x39)!=0xff){
  o->error=G702_BASELINE;goto done;
 }
 o->phase=2;
 const GPU_PARAMETER target={720,720,738,779,480,489,489,524,524,4,3};
 SetGPURegister(&target,(uint8_t *)g);
 cw(g,0x39,0xff);
 w32(g,0x600800,r->base);
 o->phase=3;
 o->width=r32(g,0x680838)+1;o->height=r32(g,0x680818)+1;
 o->pitch=pitch(g);o->format=cr(g,0x28);o->start=r32(g,0x600800);
 o->interlace=cr(g,0x39);
 if(o->width!=720||o->height!=480||o->pitch!=2880||o->format!=0x83||
    o->start!=r->base||o->interlace!=0xff||!clocks_unchanged(g)){
  o->error=G702_READBACK;goto done;
 }
 /* PRAMDAC display/total/sync/valid registers, in source order. */
 const uint32_t offsets[]={0x680800,0x680804,0x680808,0x68080c,0x680810,
  0x680814,0x680818,0x680820,0x680824,0x680828,0x68082c,0x680830,0x680834,0x680838};
 const uint32_t values[]={479,524,479,489,492,0,479,719,779,719,738,770,0,719};
 for(unsigned i=0;i<14;++i)if(r32(g,offsets[i])!=values[i]){
  o->error=G702_READBACK;goto done;
 }
 /* Check every CRTC field this substage owns. Preserved bits are deliberately
  * outside these masks; the full initializer still has to qualify them. */
 const uint8_t cv[][3]={{0x00,0xff,0x5c},{0x01,0xff,0x59},{0x02,0xff,0x59},
  {0x03,0x1f,0x00},{0x04,0xff,0x5d},{0x05,0x9f,0x9e},{0x06,0xff,0x0c},
  {0x07,0xff,0x3e},{0x09,0x60,0x40},{0x10,0xff,0xe9},{0x12,0xff,0xdf},
  {0x13,0xff,0x68},{0x15,0xff,0xdf},{0x16,0x7f,0x0c},{0x17,0x80,0x80},
  {0x18,0xff,0xff},{0x19,0xe0,0x20},{0x1a,0xff,0x04},{0x25,0xff,0x10},
  {0x28,0xff,0x83},{0x2d,0x1f,0x00},{0x39,0xff,0xff}};
 for(unsigned i=0;i<sizeof(cv)/sizeof(cv[0]);++i)
  if((cr(g,cv[i][0])&cv[i][1])!=cv[i][2]){
   o->error=G702_READBACK;goto done;
  }
 o->phase=4;o->error=G702_OK;
done:
 g[0x6013d4]=saved;
 return o->error;
}
