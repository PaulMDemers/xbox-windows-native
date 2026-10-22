/* SPDX-License-Identifier: GPL-2.0-or-later */
#include "classify.h"
unsigned mask661(unsigned encode,unsigned entry,unsigned show,unsigned admission,unsigned send,const struct result656 *r){
 if(encode)return 0x10; /* one red slot in four: encoding failure */
 if(entry || show)return 0xff; /* solid amber: indication failure */
 if(r->used && !r->safe_to_continue)return 0xf0; /* solid red: unsafe cleanup */
 switch(admission){
 case 0:break;
 case 1:return 0x50; /* CPU: red/off */
 case 2:return 0x55; /* segments: amber/off */
 case 3:return 0xa5; /* cache: red/green */
 case 4:return 0x5f; /* PCI: green/amber */
 case 5:return 0xf5; /* DMA: red/amber */
 default:return 0x05; /* unexpected admission code: green/off */
 }
 if(send)return 0x33; /* two amber slots then two off: sender error */
 if(r->used && r->safe_to_continue && r->completed==3)return 0x0f; /* local completion */
 return 0x01; /* one green slot in four: incomplete/unexpected */
}
