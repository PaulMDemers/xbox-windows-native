/* SPDX-License-Identifier: GPL-2.0-or-later
 *700's exact wire sequence/delay, with layout admission in transaction704.
 * This helper is not a standalone physical entry point.
 */
#include "transaction.h"
#include "xcal_table.h"
static uint32_t swap(uint32_t n)
{return (n>>24)|((n>>8)&0xff00)|((n<<8)&0xff0000)|(n<<24);}
static int transfer(const struct xcal_bus *b,struct encoder704 *p,
 unsigned reg,uint32_t value,int read)
{
 ++p->attempted;p->reg=reg;p->is_read=(unsigned)read;
 p->error=(unsigned)(read?xcal_read32(b,(uint8_t)reg,&value,&p->bus):
                            xcal_write32(b,(uint8_t)reg,value,&p->bus));
 if(p->error)return 0;
 if(read)p->read_value=value;
 ++p->completed;return 1;
}
int encoder704(const struct xcal_bus *b,uint32_t (*tick)(void *),void *ctx,struct encoder704 *p)
{
 if(!p)return 0;
 *p=(struct encoder704){0};
 if(!b||!tick||!b->r8||!b->r16||!b->w8||!b->w16||!b->poll_limit||b->poll_limit>1000000)return 0;
 p->phase=1;
 if(!transfer(b,p,4,0,1)||!transfer(b,p,4,0x0f000000,0)||
    !transfer(b,p,0,0,1)||!transfer(b,p,0,0,0))return -1;
 p->phase=2;
 for(unsigned reg=0;reg<144;++reg){
  if(!transfer(b,p,reg,swap(xcal_table[reg]),0))return -1;
  ++p->table_completed;
  unsigned d=delay500_candidate(tick,ctx,1,&p->delay);
  if(d!=DELAY_OK){p->error=100+d;return -1;}
  ++p->delay_completed;
 }
 p->phase=3;return 1;
}
