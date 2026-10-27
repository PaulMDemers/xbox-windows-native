/* SPDX-License-Identifier: MIT
 * Bounded630/CR1b interaction. One CR1b05 write; no guessed writable mask.
 * Full-width 630 and full-byte CR1b restoration checks remain mandatory.
 */
#include "probe.h"
#define R8(o) (*(volatile uint8_t *)(0xfd000000u+(o)))
#define R32(o) (*(volatile uint32_t *)(0xfd000000u+(o)))
static const uint8_t preserved[3]={0x11,0x22,0x19};
static uint8_t cr(uint8_t i){R8(0x6013d4)=i;return R8(0x6013d5);}
static void cw(uint8_t i,uint8_t v){R8(0x6013d4)=i;R8(0x6013d5)=v;}
static uint8_t sr(void){R8(0xc03c4)=1;return R8(0xc03c5);}
static void sw(uint8_t v){R8(0xc03c4)=1;R8(0xc03c5)=v;}
static void gate(uint8_t v){__asm__ volatile("outb %0,%w1"::"a"(v),"d"((uint16_t)0x80d3):"memory");}
static void sample(struct result727 *o,unsigned n)
{
 uint8_t i=R8(0x6013d4);
 o->mmio630[n]=R32(0x680630);o->cr1b[n]=cr(0x1b);R8(0x6013d4)=i;
 /* Overflow is explicitly unrepresentable optically, never silently truncated. */
 o->packed[n]=o->mmio630[n]<=0xffff?(o->mmio630[n]<<16)|o->cr1b[n]:0xffffffff;
}
void probe727(struct result727 *o)
{
 uint32_t flags,restored;*o=(struct result727){0};
 o->prewrite630=o->prewrite1b=o->prewrite_packed=o->direct=o->indexed=o->write_reads_packed=0xffffffff;
 for(unsigned i=0;i<6;++i)o->mmio630[i]=o->cr1b[i]=o->packed[i]=0xffffffff;
 __asm__ volatile("pushfl;popl %0;cli":"=r"(flags)::"memory");o->flags_entry=flags;
 __asm__ volatile("pushfl;popl %0":"=r"(o->flags_critical)::"memory");
 __asm__ volatile("mov %%cr0,%0":"=r"(o->cr0));
 __asm__ volatile("mov %%cr3,%0":"=r"(o->cr3));
 __asm__ volatile("mov %%cr4,%0":"=r"(o->cr4));
 o->code=0x7271;
 if((o->cr0&0xe0000001)!=0x40000001 || o->cr3!=0 || (flags&0x200) || (o->cr4&0x20) || (o->flags_critical&0x200))goto done;
 o->saved_index=R8(0x6013d4);o->saved_seq_index=R8(0xc03c4);o->seq_before=sr();
 for(unsigned i=0;i<3;++i)o->before[i]=cr(preserved[i]);
 sample(o,0);o->code=0x7272;
 if(o->seq_before!=1 || (o->before[0]&0x80) || o->before[1]!=0xfe || o->before[2]!=0x51 || o->mmio630[0]!=3 || o->cr1b[0]!=0x85)goto selectors;
 sw(0x21);gate(5);o->code=0x7273;
 if(sr()!=0x21)goto restore_output;
 sample(o,1);if(o->mmio630[1]!=3)goto restore_output;
 o->attempts=1;R32(0x680630)=2;sample(o,2);
 o->code=0x7278;if(o->mmio630[2]!=2)goto restore630;
 o->unlock_attempt=1;cw(0x1f,0x57);o->unlock_read=cr(0x1f);
 o->unlock_cr11=cr(0x11);o->prewrite630=R32(0x680630);o->prewrite1b=cr(0x1b);
 o->prewrite_packed=o->prewrite630<=0xffff?(o->prewrite630<<16)|o->prewrite1b:0xffffffff;
 o->code=0x7279;
 if(o->unlock_cr11!=o->before[0] || o->prewrite630!=2 || o->prewrite1b!=o->cr1b[0])goto restore630;
 o->cr1b_attempt=1;cw(0x1b,5);
 /* No selector write or other MMIO read between store and direct data read. */
 o->direct=R8(0x6013d5);o->indexed=cr(0x1b);
 o->write_reads_packed=(o->direct<<16)|o->indexed;
 o->code=(o->direct==5 && o->indexed==5)?0x727:0x7278;
restore630:
 o->attempts=2;R32(0x680630)=o->mmio630[0];sample(o,3);
restore_output:
 gate(4);sw((uint8_t)o->seq_before);o->seq_after=sr();sample(o,4);
 o->late_min=o->late_max=o->cr1b[4];
 {uint32_t last=o->cr1b[4];
  for(unsigned i=0;i<32;++i){sample(o,5);o->late_count++;
   if(o->cr1b[5]!=last)o->late_changes++;
   last=o->cr1b[5];
   if(last<o->late_min)o->late_min=last;
   if(last>o->late_max)o->late_max=last;
  }
 }
 o->cleanup_ok=o->seq_after==o->seq_before && o->mmio630[5]==o->mmio630[0] && o->cr1b[5]==o->cr1b[0];
 for(unsigned i=0;i<3;++i){o->after[i]=cr(preserved[i]);if(o->after[i]!=o->before[i])o->cleanup_ok=0;}
 if(!o->cleanup_ok)o->code=0x7275;
selectors:
 R8(0x6013d4)=(uint8_t)o->saved_index;R8(0xc03c4)=(uint8_t)o->saved_seq_index;
 o->selectors_restored=R8(0x6013d4)==o->saved_index && R8(0xc03c4)==o->saved_seq_index;
 if(!o->selectors_restored)o->code=0x7276;
done:
 o->attempts_packed=o->attempts|(o->cr1b_attempt<<8)|(o->unlock_attempt<<16);
 o->summary=o->cleanup_ok|(o->selectors_restored<<1)|((o->late_count==32 && !o->late_changes)<<2)|(o->late_count<<8)|(o->attempts<<16)|(o->cr1b_attempt<<24);
 __asm__ volatile("pushl %1;popfl;pushfl;popl %0":"=&r"(restored):"r"(flags):"memory","cc");o->flags_restored=restored;
}
