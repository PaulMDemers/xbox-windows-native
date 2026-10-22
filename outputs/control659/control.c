/* SPDX-License-Identifier: GPL-2.0-or-later */
#include "control.h"
static unsigned write659(const struct smc658 *io,unsigned reg,unsigned value,struct latch659 *r){
 unsigned i,status;
 r->transactions++;
 for(i=0;i<POLLS659;i++){
  status=io->in(io->p,0xc000,2);r->reads++;r->last_status=status;
  if(!(status&0x800))break;
 }
 if(i==POLLS659)return 2;
 io->out(io->p,0xc004,1,0x20);io->out(io->p,0xc008,1,reg);io->out(io->p,0xc006,2,value);r->writes+=3;
 status=io->in(io->p,0xc000,2);r->reads++;r->last_status=status;
 io->out(io->p,0xc000,2,status);io->out(io->p,0xc002,1,0x1a);r->writes+=2;
 for(i=0;i<POLLS659;i++){
  status=io->in(io->p,0xc000,1);r->reads++;r->last_status=status;
  if(status&0x36)return ((status&0x10)&&!(status&0x26))?0:3;
 }
 return 4;
}
unsigned latch659(const struct smc658 *io,unsigned mask,struct latch659 *r){
 unsigned e;
 if(!io || !io->in || !io->out || !r || mask>255)return 1;
 e=write659(io,8,mask,r);
 if(!e)e=write659(io,7,1,r);
 r->error=e;return e;
}
unsigned mask659(unsigned encode,unsigned entry,unsigned show){
 if(encode)return 0xf0; /* solid red: encoder failure */
 if(show==1)return 0x50; /* red/off: original indication delay failed */
 if(show==2)return 0xa5; /* red/green: original indication busy timeout */
 if(show==3)return 0xf5; /* red/amber: original indication completion error */
 if(show==4)return 0x5f; /* green/amber: original indication completion timeout */
 if(show)return 0xf0;
 return entry?0x55:0x0f; /* amber/off: entry latch failed; green: both passed */
}
