/* SPDX-License-Identifier: GPL-2.0-or-later
 * Bounded native wrapper; retained framebuffer/context contract from704.
 * New prefix stops before CR22; no encoder/timing code linked.
 */
#include "transaction.h"
static uint32_t r32(volatile uint8_t *g,unsigned o){return *(volatile uint32_t *)(g+o);}
static uint8_t cr(volatile uint8_t *g,uint8_t i){g[0x6013d4]=i;return g[0x6013d5];}
static uint32_t pitch(volatile uint8_t *g){return (cr(g,0x13)|((cr(g,0x19)&0xe0)<<3)|((cr(g,0x25)&0x20)<<6))<<3;}
int bounds704(const struct request704 *r)
{
 if(!r||r->ram!=0x4000000||r->base<0x2000000||r->base>=r->ram||
 (r->base&4095)||r->allocation<3686400||r->allocation>r->ram-r->base||
 r->checked_bytes<3686400||r->checked_bytes>r->allocation||r->contiguous!=1||
 r->alias_checked!=1||r->width!=1280||r->height!=720||r->pitch!=5120||r->depth!=32||
 r->confirmed_xcalibur!=1||r->cable_byte!=1||!(r->flags&0x80000)||
 r->timer_hz!=3375000||r->tv_path_confirmed!=1)return 0;
 return !(r->base<0x2800000&&0x2600000<r->base+r->allocation);
}

int native_transaction704(const struct request704 *r,volatile uint8_t *g,volatile uint32_t *fb,struct result704 *o)
{
 if(!o)return 2;
 *o=(struct result704){0};o->first_actual=o->first_expected=0xffffffff;
 o->prefix.code=2;if(!r||!g||!fb)return 2;
 o->prefix.code=3;if(!bounds704(r)||(uint32_t)g!=0xfd000000||(uint32_t)fb!=r->base)return 3;
 uint32_t f;__asm__ volatile("pushfl;popl %0":"=r"(f));o->prefix.code=4;if(f&0x200)return 4;
 uint8_t csel=g[0x6013d4];o->prefix.code=5;
 if(r32(g,0x680508)!=0x3c20d||r32(g,0x68050c)!=0x100a0400||r32(g,0x680880)!=0x21101100||
  r32(g,0x100200)!=0x3070003||r32(g,0x600804)!=3||r32(g,0x600800)!=r->base||
  r32(g,0x680838)!=1279||r32(g,0x680818)!=719||pitch(g)!=5120||cr(g,0x28)!=0x83||cr(g,0x39)!=255||
  (cr(g,0x11)&0x80)||(cr(g,0x21)&0xfa)!=0xfa||cr(g,0x44)!=0||(cr(g,9)&0x80))goto done;
 probe724(&o->prefix);
 uint32_t i=o->prefix.first_mismatch;
 if(i>=1 && i<=11){
  static const uint32_t targets[]={0,0,0x10001000,0x10000000,0x10000000,0x10000000,0x10000000,0x21101100,2,0x00801080,0x40801080};
  o->first_actual=o->prefix.mmio_after[i-1];o->first_expected=targets[i-1];
 }else if(i>=101 && i<=104){
  static const uint32_t targets[]={0,0xe3,0x10,5};o->first_actual=o->prefix.crtc_after[i-101];o->first_expected=targets[i-101];
 }
done:
 g[0x6013d4]=csel;return o->prefix.code;
}
