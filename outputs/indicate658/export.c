/* SPDX-License-Identifier: GPL-2.0-or-later
 * Diagnostic only: freeze -> encode -> bounded UDP -> safe reset or hold.
 * No Windows continuation. Source observations are never transport status.
 */
#include "boot.h"
#include "BootEEPROM.h"
#include "packet.h"
#include "nic.h"
#include "indication.h"
#include "xwn_hd_adapter.h"
#include "trace649.h"
#include "readback651.h"
#include "identity657.h"
extern EEPROMDATA eeprom;
extern int NativeSend656(const uint8_t *,unsigned,const uint8_t *,const uint8_t *,uint16_t);
extern struct result656 NativeResult656;
extern unsigned NativeAdmissionError656;
struct signal658 Signal658;
volatile unsigned SignalError658,Slots658[4];
extern void xwn652_bridge(struct xwn652_data *,int,unsigned,const struct xwn_hd_request *,
 const volatile struct xwn_hd_state *,const volatile struct xwn_trace649 *,
 const volatile struct readback651 *,const volatile struct readback651 *);
struct xwn652_data Frozen657;
uint8_t Packet657[XWN655_BYTES];
volatile unsigned ExportPhase657,EncodeError657,SendError657,ResetError657;
struct result656 ResetTimer657;
static uint32_t ticks657(void *p){(void)p;return IoInputDword(0x8008);}
static int pause657(void){
 const struct io656 io={0,0,0,0,ticks657,0};
 return delay656(&io,&ResetTimer657,10);
}
/* One SMC transaction, no retries and no legacy wait_us. Port callbacks and
 * timer reads have finite counts; a physical bus stall is not recoverable here.
 * Returns even after success: caller always holds if reset does not occur.
 */
unsigned Reset657(void){
 unsigned i,status;
 for(i=0;i<1000;i++){
  if(!(IoInputWord(0xc000)&0x0800))break;
  if(pause657())return 1;
 }
 if(i==1000)return 2;
 IoOutputByte(0xc004,0x20);IoOutputByte(0xc008,2);IoOutputWord(0xc006,1);
 status=IoInputWord(0xc000);IoOutputWord(0xc000,status);IoOutputByte(0xc002,0x1a);
 for(i=0;i<1000;i++){
  status=IoInputByte(0xc000);
  if(status&0x36)return ((status&0x10) && !(status&0x26))?0:3;
  if(pause657())return 1;
 }
 return 4;
}
static unsigned in658(void *p,unsigned port,unsigned size){
 (void)p;return size==2?IoInputWord(port):IoInputByte(port);
}
static void out658(void *p,unsigned port,unsigned size,unsigned value){
 (void)p;if(size==2)IoOutputWord(port,value);else IoOutputByte(port,value);
}
static int delay658(void *p,unsigned us){
 const struct io656 io={0,0,0,0,ticks657,0};(void)p;
 return delay656(&io,&ResetTimer657,us);
}
static const struct smc658 Smc658={0,in658,out658,delay658};
static void indicate658(unsigned code,unsigned ms){
 unsigned e=show658(&Smc658,code,ms,&Signal658);
 if(e && !SignalError658)SignalError658=e;
}
__attribute__((noreturn)) void XwnExport657(int result,const struct xwn_hd_request *r,
 const volatile struct xwn_hd_state *s,const volatile struct xwn_trace649 *t,
 const volatile struct readback651 *pre,const volatile struct readback651 *post){
 unsigned slots[4],i;
 ExportPhase657=1;
 xwn652_bridge(&Frozen657,result,result<0?2:1,r,s,t,pre,post);
 EncodeError657=xwn655_encode(&Identity657,&Frozen657,Packet657,sizeof(Packet657));
 indicate658(1,4000); /* entry marker AFTER frozen capture and encode */
 if(!EncodeError657){
  ExportPhase657=2;
  SendError657=NativeSend656(Packet657,sizeof(Packet657),eeprom.MACAddress,SourceIP657,Port657);
  ExportPhase657=3;
 }
 classify658(EncodeError657,NativeAdmissionError656,SendError657,&NativeResult656,slots);
 for(i=0;i<4;i++){Slots658[i]=slots[i];indicate658(slots[i],10000);}
 if(!EncodeError657 && (!NativeResult656.used || NativeResult656.safe_to_continue)){
  ExportPhase657=4;ResetError657=Reset657();
 }
 ExportPhase657=5;
 /* Existing early boot has IF=0. No interrupt/mapping/cache-mode mutation.
  * Static DMA buffers remain live if cleanup failed. Never return to boot.
  */
 for(;;)__asm__ __volatile__("hlt");
}
