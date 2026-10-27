/* SPDX-License-Identifier: MIT
 * Finite indexed/register reads. Only index selectors are written and restored.
 * No GPU data, encoder, ACPI, PCI, clock or interrupt-controller writes.
 */
#include "capture.h"
#define R8(o) (*(volatile uint8_t *)(0xfd000000u+(o)))
#define R32(o) (*(volatile uint32_t *)(0xfd000000u+(o)))
const uint32_t mmio722[MMIO722]={
 0x600800,0x600804,0x100200,0x680508,0x68050c,
 0x680884,0x680888,0x68088c,0x680890,0x680894,0x680898,0x68089c,
 0x680880,0x680630,0x68084c,0x6808c4,
 0x680800,0x680804,0x680808,0x68080c,0x680810,0x680814,0x680818,
 0x680820,0x680824,0x680828,0x68082c,0x680830,0x680834,0x680838
};
const uint8_t crtc722[CRTC722]={0,1,2,3,4,5,6,7,9,0x10,0x11,0x12,0x13,
 0x14,0x15,0x16,0x17,0x18,0x19,0x1a,0x1b,0x1f,0x21,0x22,0x25,
 0x28,0x2d,0x33,0x39,0x44,0x20};
void capture722(struct capture722 *o)
{
 uint32_t flags, restored;
 *o=(struct capture722){0};
 __asm__ volatile("pushfl;popl %0;cli":"=r"(flags)::"memory");
 o->flags_entry=flags;
 __asm__ volatile("pushfl;popl %0":"=r"(o->flags_critical)::"memory");
 __asm__ volatile("mov %%cr0,%0":"=r"(o->cr0));
 __asm__ volatile("mov %%cr3,%0":"=r"(o->cr3));
 __asm__ volatile("mov %%cr4,%0":"=r"(o->cr4));
 o->selectors[0]=R8(0x6013d4);o->selectors[1]=R8(0xc03c4);o->selectors[2]=R8(0xc03ce);
 for(unsigned i=0;i<MMIO722;++i)o->mmio[i]=R32(mmio722[i]);
 for(unsigned i=0;i<CRTC722;++i){R8(0x6013d4)=crtc722[i];o->crtc[i]=R8(0x6013d5);}
 for(unsigned i=0;i<5;++i){R8(0xc03c4)=(uint8_t)i;o->seq[i]=R8(0xc03c5);}
 for(unsigned i=0;i<9;++i){R8(0xc03ce)=(uint8_t)i;o->graphics[i]=R8(0xc03cf);}
 R8(0x6013d4)=(uint8_t)o->selectors[0];R8(0xc03c4)=(uint8_t)o->selectors[1];R8(0xc03ce)=(uint8_t)o->selectors[2];
 o->selectors_after[0]=R8(0x6013d4);o->selectors_after[1]=R8(0xc03c4);o->selectors_after[2]=R8(0xc03ce);
 o->selectors_restored=o->selectors[0]==o->selectors_after[0] &&
  o->selectors[1]==o->selectors_after[1] && o->selectors[2]==o->selectors_after[2];
 __asm__ volatile("pushl %1;popfl;pushfl;popl %0":"=&r"(restored):"r"(flags):"memory","cc");
 o->flags_restored=restored;
}
