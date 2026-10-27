/* SPDX-License-Identifier: MIT
 * Native-context prefix, not a full-mode replay: stop BEFORE CR22/CR33 writes.
 * Batch all writes, then check in original order. No interleaved readback.
 * CR1b is written05 once; never write85 or pretend its read value is restorable.
 * Compare ALL final bytes with their actual saved values; keep cleanup separate.
 */
#include "probe.h"
#define R8(o) (*(volatile uint8_t *)(0xfd000000u+(o)))
#define R32(o) (*(volatile uint32_t *)(0xfd000000u+(o)))
static const uint32_t setup[11][2]={
 {0x680884,0},{0x680888,0},{0x68088c,0x10001000},{0x680890,0x10000000},
 {0x680894,0x10000000},{0x680898,0x10000000},{0x68089c,0x10000000},
 {0x680880,0x21101100},{0x680630,2},{0x68084c,0x00801080},{0x6808c4,0x40801080}};
static const uint8_t cs[4][2]={{0x14,0},{0x17,0xe3},{0x19,0x10},{0x1b,5}};
static uint8_t cr(uint8_t i){R8(0x6013d4)=i;return R8(0x6013d5);}
static void cw(uint8_t i,uint8_t v){R8(0x6013d4)=i;R8(0x6013d5)=v;}
static uint8_t sr(void){R8(0xc03c4)=1;return R8(0xc03c5);}
static void sw(uint8_t v){R8(0xc03c4)=1;R8(0xc03c5)=v;}
static uint8_t gr4(void){R8(0xc03ce)=4;return R8(0xc03cf);}
static void gate(uint8_t v){__asm__ volatile("outb %0,%w1"::"a"(v),"d"((uint16_t)0x80d3):"memory");}
void probe738(struct result738 *o)
{
 uint32_t flags,restored;*o=(struct result738){0};o->first_mismatch=0xffffffff;
 for(unsigned i=0;i<11;++i)o->mmio_checked[i]=o->mmio_restored[i]=0xffffffff;
 for(unsigned i=0;i<4;++i)o->crtc_checked[i]=o->crtc_restored[i]=0xffffffff;
 __asm__ volatile("pushfl;popl %0;cli":"=r"(flags)::"memory");o->flags_entry=flags;
 __asm__ volatile("pushfl;popl %0":"=r"(o->flags_critical)::"memory");
 __asm__ volatile("mov %%cr0,%0":"=r"(o->cr0));
 __asm__ volatile("mov %%cr3,%0":"=r"(o->cr3));
 __asm__ volatile("mov %%cr4,%0":"=r"(o->cr4));
 o->forward_status=0x7381;
 if((o->cr0&0xe0000001)!=0x40000001 || o->cr3!=0 || (flags&0x200) || (o->cr4&0x20) || (o->flags_critical&0x200))goto done;
 o->saved_index=R8(0x6013d4);o->saved_seq_index=R8(0xc03c4);o->saved_gr_index=R8(0xc03ce);
 o->seq_before=sr();o->cr11_before=cr(0x11);o->gr_before=gr4();
 o->cr22_before=cr(0x22);o->cr33_before=cr(0x33);
 int admitted=o->seq_before==1 && !(o->cr11_before&0x80) && o->gr_before==0 && o->cr22_before==0xfe && o->cr33_before==0x11;
 for(unsigned i=0;i<11;++i){
  o->mmio_before[i]=R32(setup[i][0]);
  if(o->mmio_before[i]!=(i==8?3:setup[i][1]))admitted=0;
 }
 for(unsigned i=0;i<4;++i){
  o->crtc_before[i]=cr(cs[i][0]);
  if(o->crtc_before[i]!=(i==2?0x51:i==3?0x85:cs[i][1]))admitted=0;
 }
 o->forward_status=0x7382;if(!admitted)goto selectors;
 sw(0x21);gate(5);o->forward_status=0x7383;if(sr()!=0x21)goto restore;
 cw(0x1f,0x57);o->unlock_read=cr(0x1f);
 o->forward_status=0x7384;
 if(cr(0x11)!=o->cr11_before || cr(0x22)!=o->cr22_before)goto restore;
 for(unsigned i=0;i<11;++i){o->attempted_mmio=i+1;R32(setup[i][0])=setup[i][1];}
 for(unsigned i=0;i<4;++i){o->attempted_crtc=i+1;cw(cs[i][0],cs[i][1]);}
 o->forward_status=0x7388;
 for(unsigned i=0;i<11;++i){
  uint32_t value=R32(setup[i][0]);o->mmio_checked[i]=value;o->checked=i+1;
  if(value!=setup[i][1]){o->first_mismatch=i;o->expected=setup[i][1];o->observed=value;goto restore;}
 }
 for(unsigned i=0;i<4;++i){
  uint32_t value=cr(cs[i][0]);o->crtc_checked[i]=value;o->checked=12+i;
  if(value!=cs[i][1]){o->first_mismatch=11+i;o->expected=cs[i][1];o->observed=value;goto restore;}
 }
 o->forward_status=0x738;
restore:
 /* Same bounded recovery as723/725: no guessed CR1b or CR22 restoration. */
 if(o->attempted_crtc>=3)cw(0x19,(uint8_t)o->crtc_before[2]);
 if(o->attempted_mmio>=9)R32(0x680630)=o->mmio_before[8];
 gate(4);sw((uint8_t)o->seq_before);o->seq_after=sr();
 o->cr11_after=cr(0x11);o->gr_after=gr4();o->cr22_after=cr(0x22);o->cr33_after=cr(0x33);
 for(unsigned i=0;i<11;++i){o->mmio_restored[i]=R32(setup[i][0]);if(o->mmio_restored[i]!=o->mmio_before[i])o->cleanup_mask|=1u<<i;}
 for(unsigned i=0;i<4;++i){o->crtc_restored[i]=cr(cs[i][0]);if(o->crtc_restored[i]!=o->crtc_before[i])o->cleanup_mask|=1u<<(11+i);}
 if(o->seq_after!=o->seq_before)o->cleanup_mask|=1u<<15;
 if(o->cr11_after!=o->cr11_before)o->cleanup_mask|=1u<<16;
 if(o->gr_after!=o->gr_before)o->cleanup_mask|=1u<<17;
 if(o->cr22_after!=o->cr22_before)o->cleanup_mask|=1u<<18;
 if(o->cr33_after!=o->cr33_before)o->cleanup_mask|=1u<<19;
 o->cleanup_ok=o->cleanup_mask==0;
selectors:
 R8(0x6013d4)=(uint8_t)o->saved_index;R8(0xc03c4)=(uint8_t)o->saved_seq_index;R8(0xc03ce)=(uint8_t)o->saved_gr_index;
 o->selectors_restored=R8(0x6013d4)==o->saved_index && R8(0xc03c4)==o->saved_seq_index && R8(0xc03ce)==o->saved_gr_index;
done:
 o->code=o->forward_status;
 if(o->forward_status!=0x7381 && o->forward_status!=0x7382 && !o->cleanup_ok)o->code=0x7385;
 if(o->forward_status!=0x7381 && !o->selectors_restored)o->code=0x7386;
 __asm__ volatile("pushl %1;popfl;pushfl;popl %0":"=&r"(restored):"r"(flags):"memory","cc");o->flags_restored=restored;
}
