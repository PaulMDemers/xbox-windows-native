/* SPDX-License-Identifier: MIT
 * Bounded 630-only control. No CRTC data writes, no guessed writable mask.
 * Full-width 630 and full-byte CR1b restoration checks remain mandatory.
 */
#include "probe.h"
#define R8(o) (*(volatile uint8_t *)(0xfd000000u+(o)))
#define R32(o) (*(volatile uint32_t *)(0xfd000000u+(o)))
static const uint8_t preserved[3]={0x11,0x22,0x19};
static uint8_t cr(uint8_t i){R8(0x6013d4)=i;return R8(0x6013d5);}
static uint8_t sr(void){R8(0xc03c4)=1;return R8(0xc03c5);}
static void sw(uint8_t v){R8(0xc03c4)=1;R8(0xc03c5)=v;}
static void gate(uint8_t v){__asm__ volatile("outb %0,%w1"::"a"(v),"d"((uint16_t)0x80d3):"memory");}
static void sample(struct result726 *o,unsigned n)
{
 uint8_t i=R8(0x6013d4);
 o->mmio630[n]=R32(0x680630);o->cr1b[n]=cr(0x1b);R8(0x6013d4)=i;
 /* Overflow is explicitly unrepresentable optically, never silently truncated. */
 o->packed[n]=o->mmio630[n]<=0xffff?(o->mmio630[n]<<16)|o->cr1b[n]:0xffffffff;
}
void probe726(struct result726 *o)
{
 uint32_t flags,restored;*o=(struct result726){0};
 for(unsigned i=0;i<6;++i)o->mmio630[i]=o->cr1b[i]=o->packed[i]=0xffffffff;
 __asm__ volatile("pushfl;popl %0;cli":"=r"(flags)::"memory");o->flags_entry=flags;
 __asm__ volatile("pushfl;popl %0":"=r"(o->flags_critical)::"memory");
 __asm__ volatile("mov %%cr0,%0":"=r"(o->cr0));
 __asm__ volatile("mov %%cr3,%0":"=r"(o->cr3));
 __asm__ volatile("mov %%cr4,%0":"=r"(o->cr4));
 o->code=0x7261;
 if((o->cr0&0xe0000001)!=0x40000001 || o->cr3!=0 || (flags&0x200) || (o->cr4&0x20) || (o->flags_critical&0x200))goto done;
 o->saved_index=R8(0x6013d4);o->saved_seq_index=R8(0xc03c4);o->seq_before=sr();
 for(unsigned i=0;i<3;++i)o->before[i]=cr(preserved[i]);
 sample(o,0);o->code=0x7262;
 if(o->seq_before!=1 || (o->before[0]&0x80) || o->before[1]!=0xfe || o->before[2]!=0x51 || o->mmio630[0]!=3 || o->cr1b[0]!=0x85)goto selectors;
 sw(0x21);gate(5);o->code=0x7263;
 if(sr()!=0x21)goto restore_output;
 sample(o,1);if(o->mmio630[1]!=3)goto restore_output;
 o->attempts=1;R32(0x680630)=2;sample(o,2);
 o->code=o->mmio630[2]==2?0x726:0x7268;
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
 if(!o->cleanup_ok)o->code=0x7265;
selectors:
 R8(0x6013d4)=(uint8_t)o->saved_index;R8(0xc03c4)=(uint8_t)o->saved_seq_index;
 o->selectors_restored=R8(0x6013d4)==o->saved_index && R8(0xc03c4)==o->saved_seq_index;
 if(!o->selectors_restored)o->code=0x7266;
done:
 o->summary=o->cleanup_ok|(o->selectors_restored<<1)|((o->late_count==32 && !o->late_changes)<<2)|(o->late_count<<8)|(o->attempts<<16);
 __asm__ volatile("pushl %1;popfl;pushfl;popl %0":"=&r"(restored):"r"(flags):"memory","cc");o->flags_restored=restored;
}
