/* SPDX-License-Identifier: MIT
 * Kernel-context common-setup prefix, stopping before CR22. No native handoff.
 * CR1b05 is deliberately retained if written; no false85 restoration claim.
 * CR19/630 and output/indices restored before kernel report APIs.
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
static void gate(uint8_t v){__asm__ volatile("outb %0,%w1"::"a"(v),"d"((uint16_t)0x80d3):"memory");}
void probe723(struct result723 *o)
{
 uint32_t flags,restored;*o=(struct result723){0};o->first_mismatch=0xffffffff;
 __asm__ volatile("pushfl;popl %0;cli":"=r"(flags)::"memory");o->flags_entry=flags;
 __asm__ volatile("pushfl;popl %0":"=r"(o->flags_critical)::"memory");
 __asm__ volatile("mov %%cr0,%0":"=r"(o->cr0));
 __asm__ volatile("mov %%cr3,%0":"=r"(o->cr3));
 __asm__ volatile("mov %%cr4,%0":"=r"(o->cr4));
 o->code=0x7231;
 if((o->cr0&0x80000001)!=0x80000001 || (o->cr4&0x20) || (o->flags_critical&0x200))goto done;
 o->saved_index=R8(0x6013d4);o->saved_seq_index=R8(0xc03c4);
 o->seq_before=sr();o->cr11_before=cr(0x11);o->cr22_before=cr(0x22);
 int admitted=o->seq_before==1 && !(o->cr11_before&0x80) && o->cr22_before==0xfe;
 for(unsigned i=0;i<11;++i){
  o->mmio_before[i]=R32(setup[i][0]);o->mmio_after[i]=0xffffffff;
  if(o->mmio_before[i]!=(i==8?3:setup[i][1]))admitted=0;
 }
 for(unsigned i=0;i<4;++i){
  o->crtc_before[i]=cr(cs[i][0]);o->crtc_after[i]=0xffffffff;
  if(o->crtc_before[i]!=(i==2?0x51:i==3?0x85:cs[i][1]))admitted=0;
 }
 o->code=0x7232;if(!admitted)goto selectors;
 sw(0x21);gate(5);o->code=0x7233;if(sr()!=0x21)goto restore;
 cw(0x1f,0x57);o->unlock_read=cr(0x1f);
 o->code=0x7234;
 if(cr(0x11)!=o->cr11_before || cr(0x22)!=o->cr22_before)goto restore;
 o->code=0x7238;
 for(unsigned i=0;i<11;++i){
  o->attempted_mmio=i+1;R32(setup[i][0])=setup[i][1];o->mmio_after[i]=R32(setup[i][0]);
  if(o->mmio_after[i]!=setup[i][1]){o->first_mismatch=i+1;goto restore;}
 }
 for(unsigned i=0;i<4;++i){
  o->attempted_crtc=i+1;cw(cs[i][0],cs[i][1]);o->crtc_after[i]=cr(cs[i][0]);
  if(o->crtc_after[i]!=cs[i][1]){o->first_mismatch=101+i;goto restore;}
 }
 o->code=0x723;
restore:
 /* Do not repeat CR1b or attempt85. Restore only the two changed controls. */
 if(o->attempted_crtc>=3)cw(0x19,(uint8_t)o->crtc_before[2]);
 if(o->attempted_mmio>=9)R32(0x680630)=o->mmio_before[8];
 gate(4);sw((uint8_t)o->seq_before);o->seq_after=sr();
 o->cr11_after=cr(0x11);o->cr22_after=cr(0x22);
 o->cleanup_ok=o->seq_after==o->seq_before && o->cr11_after==o->cr11_before && o->cr22_after==o->cr22_before;
 for(unsigned i=0;i<11;++i){o->mmio_restored[i]=R32(setup[i][0]);if(o->mmio_restored[i]!=o->mmio_before[i])o->cleanup_ok=0;}
 for(unsigned i=0;i<4;++i){
  o->crtc_restored[i]=cr(cs[i][0]);
  if(o->crtc_restored[i]!=(i==3 && o->attempted_crtc==4?5:o->crtc_before[i]))o->cleanup_ok=0;
 }
 if(!o->cleanup_ok)o->code=0x7235;
selectors:
 R8(0x6013d4)=(uint8_t)o->saved_index;R8(0xc03c4)=(uint8_t)o->saved_seq_index;
 o->selectors_restored=R8(0x6013d4)==o->saved_index && R8(0xc03c4)==o->saved_seq_index;
 if(!o->selectors_restored)o->code=0x7236;
done:
 __asm__ volatile("pushl %1;popfl;pushfl;popl %0":"=&r"(restored):"r"(flags):"memory","cc");o->flags_restored=restored;
}
