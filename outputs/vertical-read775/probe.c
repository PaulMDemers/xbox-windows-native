/* SPDX-License-Identifier: MIT
 * Read-only kernel-context MMIO samples. No CLI, selector or timing writes.
 * Repeated agreement is observation, not an atomic snapshot or mode proof.
 */
#include "probe.h"
#define R32(a) (*(volatile uint32_t *)(0xfd000000u+(a)))
static const uint32_t offsets[7]={0x680800,0x680804,0x680808,0x68080c,0x680810,0x680814,0x680818};
void probe775(struct result775 *o)
{
 uint32_t flags;__asm__ volatile("pushfl;popl %0":"=r"(flags)::"memory");
 for(unsigned i=0;i<sizeof(*o)/4;++i)((uint32_t *)o)[i]=0;
 o->flags_entry=flags;
 __asm__ volatile("mov %%cr0,%0":"=r"(o->cr0));
 __asm__ volatile("mov %%cr3,%0":"=r"(o->cr3));
 __asm__ volatile("mov %%cr4,%0":"=r"(o->cr4));
 o->code=0x7751;
 if((o->cr0&0x80000001)!=0x80000001 || (o->cr4&0x20))goto done;
 for(unsigned i=0;i<7;++i){o->first[i]=R32(offsets[i]);++o->count;}
 for(unsigned i=7;i>0;--i){o->second[i-1]=R32(offsets[i-1]);++o->count;}
 for(unsigned i=0;i<7;++i){o->third[i]=R32(offsets[i]);++o->count;}
 for(unsigned i=0;i<7;++i){
  if(o->first[i]!=o->second[i] || o->first[i]!=o->third[i])o->mismatch_mask|=1u<<i;
  if((o->first[i]|o->second[i]|o->third[i])&0xffff0000u)o->invalid_mask|=1u<<i;
 }
 o->code=o->invalid_mask?0x7753:o->mismatch_mask?0x7752:0x775;
done:
 __asm__ volatile("pushfl;popl %0":"=r"(o->flags_exit)::"memory");
}
