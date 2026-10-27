/* SPDX-License-Identifier: MIT
 * Kernel-context comparator for native720. No API, loop, wait, allocation,
 * paging/cache change or native transition inside the IRQ-off interval.
 * One saved-value CR1b data write maximum. Never retry or repair CR1b.
 */
#include "probe.h"
#define R8(o) (*(volatile uint8_t *)(0xfd000000u+(o)))
static uint8_t cr(uint8_t i){R8(0x6013d4)=i;return R8(0x6013d5);}
static void cw(uint8_t i,uint8_t v){R8(0x6013d4)=i;R8(0x6013d5)=v;}
static uint8_t sr(uint8_t i){R8(0xc03c4)=i;return R8(0xc03c5);}
static void sw(uint8_t i,uint8_t v){R8(0xc03c4)=i;R8(0xc03c5)=v;}
static void gate(uint8_t v){__asm__ volatile("outb %0,%w1"::"a"(v),"d"((uint16_t)0x80d3):"memory");}
void probe721(struct result721 *o)
{
 uint32_t flags, restored;
 /* Zeroing runs before the bounded critical interval. Caller supplies storage. */
 *o=(struct result721){0};
 __asm__ volatile("pushfl;popl %0;cli":"=r"(flags)::"memory");
 o->flags_entry=flags;
 __asm__ volatile("pushfl;popl %0":"=r"(o->flags_critical)::"memory");
 __asm__ volatile("mov %%cr0,%0":"=r"(o->cr0));
 __asm__ volatile("mov %%cr3,%0":"=r"(o->cr3));
 __asm__ volatile("mov %%cr4,%0":"=r"(o->cr4));
 o->code=0x7211;
 if((o->cr0&0x80000001)!=0x80000001 || (o->cr4&0x20) || (o->flags_critical&0x200))goto done;
 o->saved_index=R8(0x6013d4);o->saved_seq_index=R8(0xc03c4);
 o->before=cr(0x1b);o->seq_before=sr(1);o->cr11_before=cr(0x11);
 o->direct_after=o->selected_after=o->restored_after=0xffffffff;
 o->code=0x7212;
 if(o->before!=0x85 || o->seq_before!=1 || (o->cr11_before&0x80))goto selectors;
 sw(1,0x21);gate(5);
 o->code=0x7213;
 if(sr(1)!=0x21)goto restore;
 cw(0x1f,0x57);o->unlock_read=cr(0x1f);
 o->cr11_after=cr(0x11);o->prewrite=cr(0x1b);
 o->index_before_write=R8(0x6013d4);
 o->code=0x7214;
 if(o->prewrite!=o->before || o->cr11_after!=o->cr11_before || o->index_before_write!=0x1b)goto restore;
 o->requested=o->before;o->attempted=1;
 cw(0x1b,(uint8_t)o->requested);
 /* Direct data read first: no index write between data store and this read. */
 o->direct_after=R8(0x6013d5);o->index_after_write=R8(0x6013d4);
 o->selected_after=cr(0x1b);
 o->code=(o->direct_after==o->before && o->selected_after==o->before && o->index_after_write==0x1b)?0x721:0x7218;
restore:
 gate(4);sw(1,(uint8_t)o->seq_before);
 o->restored_after=cr(0x1b);o->seq_restored=sr(1);o->cr11_after=cr(0x11);
 if(o->seq_restored!=o->seq_before || o->cr11_after!=o->cr11_before)o->code=0x7215;
 else if(o->code==0x721 && o->restored_after!=o->before)o->code=0x7218;
selectors:
 R8(0x6013d4)=(uint8_t)o->saved_index;R8(0xc03c4)=(uint8_t)o->saved_seq_index;
 o->selectors_restored=(R8(0x6013d4)==o->saved_index && R8(0xc03c4)==o->saved_seq_index);
 if(!o->selectors_restored)o->code=0x7216;
done:
 __asm__ volatile("pushl %1;popfl;pushfl;popl %0":"=&r"(restored):"r"(flags):"memory","cc");
 o->flags_restored=restored;
}
