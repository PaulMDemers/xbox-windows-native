/* SPDX-License-Identifier: GPL-2.0-or-later
 * Freeze original capture, test original indication, latch result and HOLD.
 * No network call, automatic reset, Windows continuation or pre-capture effect.
 */
#include "boot.h"
#include "packet.h"
#include "control.h"
#include "xwn_hd_adapter.h"
#include "trace649.h"
#include "readback651.h"
#include "identity657.h"
extern void xwn652_bridge(struct xwn652_data *,int,unsigned,const struct xwn_hd_request *,
 const volatile struct xwn_hd_state *,const volatile struct xwn_trace649 *,
 const volatile struct readback651 *,const volatile struct readback651 *);
struct xwn652_data Frozen657;
uint8_t Packet657[XWN655_BYTES];
struct result656 Timer659;
struct signal658 Signal659;
struct latch659 Entry659,Final659;
volatile unsigned Phase659,Encode659,EntryError659,ShowError659,FinalError659,Mask659;
static uint32_t ticks659(void *p){(void)p;return IoInputDword(0x8008);}
static unsigned in659(void *p,unsigned port,unsigned size){
 (void)p;return size==2?IoInputWord(port):IoInputByte(port);
}
static void out659(void *p,unsigned port,unsigned size,unsigned value){
 (void)p;if(size==2)IoOutputWord(port,value);else IoOutputByte(port,value);
}
static int delay659(void *p,unsigned us){
 const struct io656 io={0,0,0,0,ticks659,0};(void)p;
 return delay656(&io,&Timer659,us);
}
static const struct smc658 Smc659={0,in659,out659,delay659};
__attribute__((noreturn)) void XwnExport657(int result,const struct xwn_hd_request *r,
 const volatile struct xwn_hd_state *s,const volatile struct xwn_trace649 *t,
 const volatile struct readback651 *pre,const volatile struct readback651 *post){
 Phase659=1;
 xwn652_bridge(&Frozen657,result,result<0?2:1,r,s,t,pre,post);
 Encode659=xwn655_encode(&Identity657,&Frozen657,Packet657,sizeof(Packet657));
 Phase659=2;EntryError659=latch659(&Smc659,0x55,&Entry659);
 Phase659=3;
 if(!Encode659)ShowError659=show658(&Smc659,1,4000,&Signal659);
 Phase659=4;Mask659=mask659(Encode659,EntryError659,ShowError659);
 FinalError659=latch659(&Smc659,Mask659,&Final659);
 Phase659=5;
 /* Intentional persistent observation. User power-cycle required. */
 for(;;)__asm__ __volatile__("hlt");
}
