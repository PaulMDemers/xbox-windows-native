/* SPDX-License-Identifier: GPL-2.0-or-later
 * HOST-ONLY integration candidate. No display/boot hook or XBE in this kit.
 */
#include "integration.h"
#include "signal672.h"
#include "nic.h"
#include "admission.h"
#include "indication.h"
extern int NativeSend656(const uint8_t *,unsigned,const uint8_t *,const uint8_t *,uint16_t);
extern struct result656 NativeResult656;
extern unsigned NativeAdmissionError656;
struct record669 Record670;
struct emission672 Entry672,Final672;
struct code672 Code672;
unsigned EntryError672;
struct result656 SignalTimer670;
unsigned SignalError670;
unsigned prepare670(const struct xwn655_identity *id,const struct xwn652_data *data){
 uint8_t packet[XWN655_BYTES];
 if(xwn655_encode(id,data,packet,sizeof(packet)))return ARG669;
 return seal669(&Record670,packet,sizeof(packet),1);
}
static int native670(void *p,const uint8_t *packet,unsigned n,struct outcome669 *out){
 const struct config670 *cfg=p;int e;
 if(!cfg)return N656_ARGUMENT;
 e=NativeSend656(packet,n,cfg->mac,cfg->ip,cfg->port);
 out->admission=NativeAdmissionError656;out->used=NativeResult656.used;
 out->safe=NativeResult656.safe_to_continue;out->completed=NativeResult656.completed;
 out->error=NativeResult656.error;out->cleanup_error=NativeResult656.cleanup_error;
 return e;
}
static unsigned signal_in(void *p,unsigned port,unsigned width){
 uint32_t v;(void)p;
 if(width==1){uint8_t b;__asm__ __volatile__("inb %1,%0":"=a"(b):"d"((uint16_t)port));v=b;}
 else{uint16_t w;__asm__ __volatile__("inw %1,%0":"=a"(w):"d"((uint16_t)port));v=w;}
 return v;
}
static void signal_out(void *p,unsigned port,unsigned width,unsigned v){
 (void)p;
 if(width==1)__asm__ __volatile__("outb %0,%1"::"a"((uint8_t)v),"d"((uint16_t)port));
 else __asm__ __volatile__("outw %0,%1"::"a"((uint16_t)v),"d"((uint16_t)port));
}
static uint32_t signal_ticks(void *p){
 uint32_t v;(void)p;__asm__ __volatile__("inl %1,%0":"=a"(v):"d"((uint16_t)0x8008));return v;
}
static int signal_delay(void *p,unsigned us){
 const struct io656 io={p,0,0,0,signal_ticks,0};return delay656(&io,&SignalTimer670,us);
}
unsigned entry672(void){
 const struct smc658 smc={0,signal_in,signal_out,signal_delay};
 if((irq_flags669(0)&0x200u) || Record670.phase!=READY669)return 5;
 EntryError672=marker672(&smc,&Entry672);return EntryError672;
}
void terminal670(const struct config670 *cfg){
 const struct ops669 ops={(void *)cfg,irq_enter669,irq_flags669,native670};
 const struct smc658 smc={0,signal_in,signal_out,signal_delay};
 unsigned status;
 /* Physical export must finish its distinct entry signal first. */
 if(!Entry672.complete || EntryError672)irq_hold669();
 status=run669(&Record670,&ops);
 if(status==BUSY669 || status==ARG669)irq_hold669();
 if(irq_flags669(0)&0x200u)irq_hold669();
 Code672=classify672(&Record670);
 SignalError670=report672(&smc,&Final672,Code672);
 irq_hold669();
}
