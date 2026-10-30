/* SPDX-License-Identifier: GPL-2.0-or-later
 * Fresh full-loader entry. Stops before all legacy C startup and Windows.
 * Retains actual CPU/PCI/config/transaction observations in owned loader BSS.
 * Does not clear inherited SMBus status or adjust CPU/mapping state.
 */
#include "transaction.h"
#include "memory_layout.h"
_Static_assert(RAMSIZE==0x04000000 && FB_SIZE==0x00900000 &&
 (FB_START&0x0fffffff)==0x03700000 && MAX_INITRD_END==0x03700000 &&
 MEMORYMANAGEREND==0x02600000 && STACK_TOP==0x02800000,"loader reservation");
struct entry826 {
 uint32_t magic,phase,error,flags,cr0,cr3,cr4,cs,ds,ss,selector,pci[10];
 uint32_t incoming,start_tick,end_tick,delta,polls,cable,standard,video_flags;
 uint32_t encoder_value,status,completed;
 struct request704 request;
 struct result704 result;
 struct xcal_trace trace;
};
volatile struct entry826 XcalState826;
static uint32_t in32(uint16_t p){uint32_t v;__asm__ volatile("inl %w1,%0":"=a"(v):"d"(p):"memory");return v;}
static uint16_t in16(void *c,unsigned o){uint16_t v;(void)c;__asm__ volatile("inw %w1,%0":"=a"(v):"d"((uint16_t)(0xc000+o)):"memory");return v;}
static uint8_t in8(void *c,unsigned o){uint8_t v;(void)c;__asm__ volatile("inb %w1,%0":"=a"(v):"d"((uint16_t)(0xc000+o)):"memory");return v;}
static void out32(uint16_t p,uint32_t v){__asm__ volatile("outl %0,%w1"::"a"(v),"d"(p):"memory");}
static void out8(void *c,unsigned o,uint8_t v){(void)c;__asm__ volatile("outb %0,%w1"::"a"(v),"d"((uint16_t)(0xc000+o)):"memory");}
static void out16(void *c,unsigned o,uint16_t v){(void)c;__asm__ volatile("outw %0,%w1"::"a"(v),"d"((uint16_t)(0xc000+o)):"memory");}
static const struct xcal_bus bus={0,in8,in16,out8,out16,100000};
static uint32_t mm(unsigned o){return *(volatile uint32_t *)(0xfd000000+o);}
/* Same owned-transaction rules as825 block helper, applied to byte command2.
 * Output published only after terminal ownership and final cleanliness. */
static int byte_read(uint8_t a,uint8_t reg,uint8_t *value)
{
 uint16_t s=in16(0,0);unsigned i;
 if(s&0x0808)return XCAL_BUSY;
 if(s&0x0037)return XCAL_DIRTY_STATUS;
 out8(0,4,(uint8_t)(a*2+1));out8(0,8,reg);out8(0,2,0x0a);
 for(i=0;i<100000;++i){
  s=in16(0,0);if((s&0x0808)||!(s&0x37))continue;
  int e=(s&0x27)?XCAL_BUS_ERROR:XCAL_OK;
  uint8_t v=e?0:in8(0,6);out16(0,0,s&0x37);
  if(in16(0,0)&0x083f)return XCAL_FINAL_STATUS;
  if(!e)*value=v;return e;
 }
 return XCAL_TIMEOUT;
}
int XcalCollect826(volatile struct entry826 *s)
{
 uint32_t v;uint16_t seg;uint8_t b;int e;
 static const uint32_t sels[]={0x80010000,0x80010004,0x80010010,
  0x80000900,0x80000904,0x80000914,0x80000800,0x80000804,0x80000810,0x80000884};
 *s=(struct entry826){0};s->magic=0x584e0826;s->phase=1;
 __asm__ volatile("pushfl;popl %0":"=r"(v)::"memory");s->flags=v;
 __asm__ volatile("mov %%cr0,%0":"=r"(v));s->cr0=v;
 __asm__ volatile("mov %%cr3,%0":"=r"(v));s->cr3=v;
 __asm__ volatile("mov %%cr4,%0":"=r"(v));s->cr4=v;
 __asm__ volatile("mov %%cs,%0":"=r"(seg));s->cs=seg;
 __asm__ volatile("mov %%ds,%0":"=r"(seg));s->ds=seg;
 __asm__ volatile("mov %%ss,%0":"=r"(seg));s->ss=seg;
 /* Actual pinned startup keeps CD/NW set, paging off, flat segments.
  * CR3=800 is captured, not interpreted as an active paging structure. */
 if((s->flags&0x200)||(s->cr0&0xe0000001)!=0x60000001||
    (s->cr4&0x20)||s->cs!=16||s->ds!=24||s->ss!=24){s->error=2001;return 0;}
 s->phase=2;s->selector=in32(0xcf8);
 for(unsigned i=0;i<10;++i){out32(0xcf8,sels[i]);s->pci[i]=in32(0xcfc);}
 out32(0xcf8,s->selector);
 if(s->pci[0]!=0x02a010de||!(s->pci[1]&2)||(s->pci[2]&~8u)!=0xfd000000||
 s->pci[3]!=0x01b410de||!(s->pci[4]&1)||s->pci[5]!=0xc001||
 s->pci[6]!=0x01b210de||!(s->pci[7]&1)||s->pci[8]!=0||s->pci[9]!=0x8001){s->error=2002;return 0;}
 s->phase=3;s->incoming=mm(0x600800);
 if(s->incoming<0x02000000||(s->incoming&4095)||s->incoming>0x04000000-3686400||
 mm(0x680838)!=1279||mm(0x680818)!=719){s->error=2003;return 0;}
 s->phase=4;s->start_tick=in32(0x8008);
 for(unsigned i=0;i<100000;++i){s->end_tick=in32(0x8008);s->delta=s->end_tick-s->start_tick;s->polls=i+1;
  if(s->delta>33750){s->error=2004;return 0;}if(s->delta>=1688)break;}
 if(s->delta<1688){s->error=2004;return 0;}
 s->phase=5;
 e=byte_read(0x10,4,&b);if(e){s->error=e;return 0;}s->cable=b;++s->completed;
 for(unsigned i=0;i<4;++i){e=byte_read(0x54,(uint8_t)(0x58+i),&b);if(e){s->error=e;return 0;}
  s->standard|=(uint32_t)b<<(i*8);++s->completed;}
 e=byte_read(0x54,0x96,&b);if(e){s->error=e;return 0;}s->video_flags=b;++s->completed;
 if(s->cable!=1||(s->standard!=0x00400100&&s->standard!=0x00400200)||!(s->video_flags&8)){s->error=2005;return 0;}
 s->phase=6;
 e=xcal_read32(&bus,0,&v,(struct xcal_trace *)&s->trace);if(e){s->error=e;return 0;}
 s->encoder_value=v;++s->completed;s->status=in16(0,0);
 if(s->status&0x083f){s->error=XCAL_FINAL_STATUS;return 0;}
 /* Reservation is established by linked layout and boot ownership, not nxdk
  * allocation. Identity addressing is established by the checked flat CPU.
  * Clock rate is the known board contract; delta proves progress only. */
 s->request=(struct request704){RAMSIZE,0x03700000,FB_SIZE,3686400,1,1,
  1280,720,5120,32,1,s->cable,0x80000,3375000,1,s->incoming};
 s->phase=7;return 1;
}
void XcalEntry826(void)
{
 if(XcalCollect826(&XcalState826)){
  XcalState826.phase=8;
  XcalState826.error=native_transaction704((const struct request704 *)&XcalState826.request,
   (volatile uint8_t *)0xfd000000,(volatile uint32_t *)0x03700000,(struct result704 *)&XcalState826.result);
  XcalState826.phase=9;
 }
 /* Diagnostic-only gate: no hidden fallthrough into legacy video or Windows. */
 for(;;)__asm__ volatile("hlt":::"memory");
}
