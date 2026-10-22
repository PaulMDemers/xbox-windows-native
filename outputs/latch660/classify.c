/* SPDX-License-Identifier: GPL-2.0-or-later */
#include "classify.h"
unsigned mask660(unsigned encode,unsigned entry,unsigned show,unsigned admission,unsigned send,const struct result656 *r){
 if(encode)return 0xf0; /* solid red: encode error; no network */
 if(entry || show)return 0xa5; /* red/green: indication error; no network */
 if(r->used && !r->safe_to_continue)return 0xf5; /* red/amber: unsafe cleanup */
 if(admission)return 0x50; /* red/off: native admission rejected */
 if(send)return 0x55; /* amber/off: sender returned error, no unsafe cleanup */
 if(r->used && r->safe_to_continue && r->completed==3)return 0x0f; /* local completions only */
 return 0x5f; /* green/amber: unexpected/incomplete result */
}
