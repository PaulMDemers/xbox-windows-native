/* SPDX-License-Identifier: GPL-2.0-or-later
 * Post-capture SMC indications only. Never modifies producer data or NIC state.
 */
#include "indication.h"
static unsigned wait658(const struct smc658 *io,unsigned us,struct signal658 *r){
 r->waits++;if(io->delay(io->p,us)){r->error=1;return 1;}return 0;
}
unsigned write658(const struct smc658 *io,unsigned reg,unsigned value,struct signal658 *r){
 unsigned i,status;
 if(!io || !io->in || !io->out || !io->delay || !r || reg>255 || value>255)return 5;
 r->transactions++;
 for(i=0;i<1000;i++){
  if(!(io->in(io->p,0xc000,2)&0x0800))break;
  if(wait658(io,10,r))return 1;
 }
 if(i==1000){r->error=2;return 2;}
 io->out(io->p,0xc004,1,0x20);io->out(io->p,0xc008,1,reg);io->out(io->p,0xc006,2,value);
 status=io->in(io->p,0xc000,2);io->out(io->p,0xc000,2,status);io->out(io->p,0xc002,1,0x1a);
 for(i=0;i<1000;i++){
  status=io->in(io->p,0xc000,1);
  if(status&0x36){r->error=((status&0x10) && !(status&0x26))?0:3;return r->error;}
  if(wait658(io,10,r))return 1;
 }
 r->error=4;return 4;
}
unsigned show658(const struct smc658 *io,unsigned code,unsigned ms,struct signal658 *r){
 static const unsigned masks[8]={0x0f,0x05,0x50,0x55,0xa5,0xf5,0x5f,0xff};
 unsigned i,e;
 if(code>7 || !ms || ms>10000)return 5;
 e=write658(io,8,0,r);if(e)return e;
 e=write658(io,7,1,r);if(e)return e;
 for(i=0;i<2000;i++)if(wait658(io,1000,r))return 1;
 e=write658(io,8,masks[code],r);if(e)return e;
 for(i=0;i<ms;i++)if(wait658(io,1000,r))return 1;
 return 0;
}
void classify658(unsigned encode,unsigned admission,unsigned send,const struct result656 *r,unsigned *slots){
 unsigned category,code;
 if(encode){category=7;code=15;}
 else if(admission){category=2;code=admission;}
 else if(r->used && !r->safe_to_continue){category=5;code=r->cleanup_error?r->cleanup_error:15;}
 else if(send){category=3;code=send;}
 else if(r->used && r->completed==3){category=0;code=0;}
 else{category=4;code=15;}
 if(code>63)code=63;
 slots[0]=category;slots[1]=code>>3;slots[2]=code&7;slots[3]=r->failed_phase<=7?r->failed_phase:7;
}
