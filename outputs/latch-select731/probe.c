/* SPDX-License-Identifier: MIT
 * CR22 is READ ONLY in this diagnostic. No inference about write semantics.
 * Only GR04 read-plane selection is varied, then its full saved byte restored.
 * No framebuffer/legacy aperture access, timing, blanking, unlock or gate writes.
 */
#include "probe.h"
#define R8(o) (*(volatile uint8_t *)(0xfd000000u+(o)))
#define R32(o) (*(volatile uint32_t *)(0xfd000000u+(o)))
static uint8_t cr(uint8_t i){R8(0x6013d4)=i;return R8(0x6013d5);}
static uint8_t gr4(void){R8(0xc03ce)=4;return R8(0xc03cf);}
static void setgr4(uint8_t v){R8(0xc03ce)=4;R8(0xc03cf)=v;}
void probe731(struct result731 *o)
{
 uint32_t flags,restored;*o=(struct result731){0};
 for(unsigned i=0;i<4;++i)o->requested[i]=o->gr_read[i]=o->cr22_first[i]=o->cr22_direct[i]=o->cr22_reselected[i]=0xffffffff;
 __asm__ volatile("pushfl;popl %0;cli":"=r"(flags)::"memory");o->flags_entry=flags;
 __asm__ volatile("pushfl;popl %0":"=r"(o->flags_critical)::"memory");
 __asm__ volatile("mov %%cr0,%0":"=r"(o->cr0));
 __asm__ volatile("mov %%cr3,%0":"=r"(o->cr3));
 __asm__ volatile("mov %%cr4,%0":"=r"(o->cr4));
 o->code=0x7311;
 if((o->cr0&0x80000001)!=0x80000001 || (o->cr4&0x20) || (o->flags_critical&0x200))goto done;
 o->saved_cr_index=R8(0x6013d4);o->saved_gr_index=R8(0xc03ce);
 o->gr_before=gr4();o->cr22_before=cr(0x22);o->cr33_before=cr(0x33);
 o->mmio630_before=R32(0x680630);o->cr1b_before=cr(0x1b);
 o->code=0x7312;
 /* Refuse any unreviewed high bits instead of inventing their writable mask. */
 if(o->gr_before>3)goto selectors;
 o->code=0x731;
 for(unsigned p=0;p<4;++p){
  o->requested[p]=p;o->attempts++;setgr4((uint8_t)p);o->gr_read[p]=gr4();
  if(o->gr_read[p]!=p){o->code=0x7313;break;}
  o->cr22_first[p]=cr(0x22);
  o->cr22_direct[p]=R8(0x6013d5);
  o->cr22_reselected[p]=cr(0x22);o->completed++;
 }
 /* One saved-value restore on every admitted path, including a failed selection. */
 o->attempts++;setgr4((uint8_t)o->gr_before);o->gr_after=gr4();
 o->cr22_after=cr(0x22);o->cr33_after=cr(0x33);
 o->mmio630_after=R32(0x680630);o->cr1b_after=cr(0x1b);
 o->cleanup_ok=o->gr_before==o->gr_after && o->cr22_before==o->cr22_after &&
  o->cr33_before==o->cr33_after && o->mmio630_before==o->mmio630_after && o->cr1b_before==o->cr1b_after;
 if(!o->cleanup_ok)o->code=0x7315;
selectors:
 R8(0x6013d4)=(uint8_t)o->saved_cr_index;R8(0xc03ce)=(uint8_t)o->saved_gr_index;
 o->selectors_restored=R8(0x6013d4)==o->saved_cr_index && R8(0xc03ce)==o->saved_gr_index;
 if(!o->selectors_restored)o->code=0x7316;
done:
 __asm__ volatile("pushl %1;popfl;pushfl;popl %0":"=&r"(restored):"r"(flags):"memory","cc");o->flags_restored=restored;
}
