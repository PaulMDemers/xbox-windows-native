/* SPDX-License-Identifier: GPL-2.0-or-later
 * Diagnostic only: SMC7 manual mode, SMC8 four-step colour sequence, as in
 * pinned nxdk lib/hal/led.c and Cromwell drivers/pci/i2cio.c. Byte command2,
 * start8, address20 (write). No legacy retry, bit10 or inherited-status ACK.
 * All four hardware sequence slots have the same colour for software pulses.
 */
#include "led830.h"
int led_write830(const struct xcal_bus *b,uint8_t reg,uint8_t value)
{
 uint16_t s;
 if(!b||!b->r16||!b->w8||!b->w16||!b->poll_limit||b->poll_limit>1000000||
    (reg!=7&&reg!=8)||(reg==7&&value!=1))return XCAL_ARGUMENT;
 s=b->r16(b->ctx,0);
 if(s&0x0808)return XCAL_BUSY;
 if(s&0x0037)return XCAL_DIRTY_STATUS;
 b->w8(b->ctx,4,0x20);b->w8(b->ctx,8,reg);
 b->w16(b->ctx,6,value);b->w8(b->ctx,2,0x0a);
 for(unsigned i=0;i<b->poll_limit;++i){
  s=b->r16(b->ctx,0);
  if((s&0x0808)||!(s&0x0037))continue;
  int e=(s&0x0027)?XCAL_BUS_ERROR:XCAL_OK;
  b->w16(b->ctx,0,s&0x0037);
  if(b->r16(b->ctx,0)&0x083f)return XCAL_FINAL_STATUS;
  return e;
 }
 return XCAL_TIMEOUT;
}
/* Half-second slices, bounded even with stopped or backward PM timer. The
 * admitted board rate is3375000Hz. Unsigned difference handles32-bit wrap. */
int led_wait830(uint32_t (*tick)(void *),void *ctx,unsigned slices)
{
 if(!tick||!slices||slices>8)return XCAL_ARGUMENT;
 for(unsigned j=0;j<slices;++j){
  uint32_t start=tick(ctx);unsigned i;
  for(i=0;i<10000000;++i){
   uint32_t d=tick(ctx)-start;
   if(d>3375000)return XCAL_TIMEOUT;
   if(d>=1687500)break;
  }
  if(i==10000000)return XCAL_TIMEOUT;
 }
 return XCAL_OK;
}
int led_frame832(const struct xcal_bus *b,uint32_t (*tick)(void *),void *ctx,
                 unsigned phase,unsigned error,unsigned long_marker)
{
 int e;
 if(!tick||phase>16||error<1||error>16||long_marker>1)return XCAL_ARGUMENT;
#define DO(expr) do {e=(expr);if(e!=XCAL_OK)return e;} while(0)
#define COLOUR(v) DO(led_write830(b,8,(v)))
#define WAIT(n) DO(led_wait830(tick,ctx,(n)))
 COLOUR(0xff);DO(led_write830(b,7,1));if(long_marker)WAIT(6);WAIT(6); /* orange6s identifier /3s value */
 COLOUR(0);WAIT(4);
 for(unsigned i=0;i<phase;++i){COLOUR(0xf0);WAIT(1);COLOUR(0);WAIT(1);}
 WAIT(4);
 for(unsigned i=0;i<error;++i){COLOUR(0x0f);WAIT(1);COLOUR(0);WAIT(1);}
 WAIT(8);
 return XCAL_OK;
#undef WAIT
#undef COLOUR
#undef DO
}
