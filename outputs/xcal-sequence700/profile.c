/* SPDX-License-Identifier: GPL-2.0-or-later */
#include "profile.h"
#include "xcal_table.h"
static uint32_t swap(uint32_t n)
{return (n>>24)|((n>>8)&0xff00)|((n<<8)&0xff0000)|(n<<24);}
static int transfer(const struct xcal_bus *b,struct xcal_progress *p,
 unsigned reg,uint32_t value,int read)
{
 ++p->attempted;p->reg=reg;p->is_read=(unsigned)read;
 p->error=(unsigned)(read?xcal_read32(b,(uint8_t)reg,&value,&p->bus):
                            xcal_write32(b,(uint8_t)reg,value,&p->bus));
 if(p->error)return 0;
 if(read)p->read_value=value;
 ++p->completed;return 1;
}
int xcal_program700(const struct xcal_bus *b,const struct xcal_request *r,
 uint32_t (*tick)(void *),void *ctx,struct xcal_progress *p)
{
 if(!p)return 0;
 *p=(struct xcal_progress){0};
 if(!b||!r||!tick||!b->r8||!b->r16||!b->w8||!b->w16||
    !b->poll_limit||b->poll_limit>1000000||r->mode!=3||r->confirmed_xcalibur!=1||
    r->cable!=3||!(r->flags&8)||r->ram!=(64u<<20)||r->fb!=(55u<<20)||
    r->reserved!=(9u<<20)||r->hidden!=316160||r->clock_qualified!=1)return 0;
 p->phase=1;
 if(!transfer(b,p,4,0,1)||!transfer(b,p,4,0x0f000000,0)||
    !transfer(b,p,0,0,1)||!transfer(b,p,0,0,0))return -1;
 p->phase=2;
 for(unsigned reg=0;reg<144;++reg){
  if(!transfer(b,p,reg,swap(xcal_table[reg]),0))return -1;
  ++p->table_completed;
  unsigned d=delay500_candidate(tick,ctx,r->clock_qualified,&p->delay);
  if(d!=DELAY_OK){p->error=100+d;return -1;}
  ++p->delay_completed;
 }
 p->phase=3;return 1;
}
