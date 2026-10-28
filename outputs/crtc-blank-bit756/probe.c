/* SPDX-License-Identifier: MIT
 * Distinct second CR05 bit7 checkpoint after
 * the preserving prefix, seven horizontal words, and qualified CR04/CR05/CR00/CR02 writes.
 * Recover own saved timing words while blank; refuse output-enable on mismatch.
 */
#include "probe.h"
#define R8(o) (*(volatile uint8_t *)(0xfd000000u+(o)))
#define R32(o) (*(volatile uint32_t *)(0xfd000000u+(o)))
static const uint32_t setup[11][2]={
 {0x680884,0},{0x680888,0},{0x68088c,0x10001000},{0x680890,0x10000000},
 {0x680894,0x10000000},{0x680898,0x10000000},{0x68089c,0x10000000},
 {0x680880,0x21101100},{0x680630,2},{0x68084c,0x00801080},{0x6808c4,0x40801080}};
/* First seven SetGPURegister writes for retained 720x480 Cromwell target.
 * Third column is the admitted 720p baseline, never a replacement recovery value. */
static const uint32_t horizontal[7][3]={
 {0x680820,719,1279},{0x680824,779,1649},{0x680828,719,1279},
 {0x680834,0,0},{0x68082c,738,1389},{0x680830,770,1429},{0x680838,719,1279}};
static const uint8_t cs[4][2]={{0x14,0},{0x17,0xe3},{0x19,0x10},{0x1b,5}};
static uint8_t cr(uint8_t i){R8(0x6013d4)=i;return R8(0x6013d5);}
static void cw(uint8_t i,uint8_t v){R8(0x6013d4)=i;R8(0x6013d5)=v;}
static uint8_t sr(void){R8(0xc03c4)=1;return R8(0xc03c5);}
static void sw(uint8_t v){R8(0xc03c4)=1;R8(0xc03c5)=v;}
static uint8_t gr4(void){R8(0xc03ce)=4;return R8(0xc03cf);}
static void gate(uint8_t v){__asm__ volatile("outb %0,%w1"::"a"(v),"d"((uint16_t)0x80d3):"memory");}
void probe756(struct result756 *o)
{
 uint32_t flags,restored;*o=(struct result756){0};o->first_mismatch=0xffffffff;o->h_first=0xffffffff;
 o->c4_checked=o->c4_restored=o->c5_checked=o->c5_restored=0xffffffff;
 o->c5_after=o->c4_after=0xffffffff;
 o->c0_after=o->c0_restored=o->c4_after_c0=o->c5_after_c0=0xffffffff;
 o->c2_after=o->c2_restored=o->c0_after_c2=o->c4_after_c2=o->c5_after_c2=0xffffffff;
 o->c3_after=o->c3_restored=o->c0_after_c3=o->c2_after_c3=o->c4_after_c3=o->c5_after_c3=0xffffffff;
 o->c5b_after=o->c5b_restored=o->c0_after_c5b=o->c2_after_c5b=o->c3_after_c5b=o->c4_after_c5b=0xffffffff;
 for(unsigned i=0;i<7;++i)o->h_checked[i]=o->h_restored[i]=0xffffffff;
 for(unsigned i=0;i<11;++i)o->mmio_checked[i]=o->mmio_restored[i]=0xffffffff;
 for(unsigned i=0;i<4;++i)o->crtc_checked[i]=o->crtc_restored[i]=0xffffffff;
 __asm__ volatile("pushfl;popl %0;cli":"=r"(flags)::"memory");o->flags_entry=flags;
 __asm__ volatile("pushfl;popl %0":"=r"(o->flags_critical)::"memory");
 __asm__ volatile("mov %%cr0,%0":"=r"(o->cr0));
 __asm__ volatile("mov %%cr3,%0":"=r"(o->cr3));
 __asm__ volatile("mov %%cr4,%0":"=r"(o->cr4));
 o->forward_status=0x7561;
 if((o->cr0&0x80000001)!=0x80000001 || (o->cr4&0x20) || (o->flags_critical&0x200))goto done;
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
 for(unsigned i=0;i<7;++i){o->h_before[i]=R32(horizontal[i][0]);if(o->h_before[i]!=horizontal[i][2])admitted=0;}
 o->c4_before=cr(4);o->c5_before=cr(5);o->c0_before=cr(0);o->c2_before=cr(2);o->c3_before=cr(3);
 if(o->c4_before!=0xa7 || o->c5_before!=0x31 || o->c0_before!=0xc8 || o->c2_before!=0x9f || o->c3_before!=0x8c)admitted=0;
 o->forward_status=0x7562;if(!admitted)goto selectors;
 sw(0x21);gate(5);o->forward_status=0x7563;if(sr()!=0x21)goto restore;
 cw(0x1f,0x57);o->unlock_read=cr(0x1f);
 o->forward_status=0x7564;
 if(cr(0x11)!=o->cr11_before || cr(0x22)!=o->cr22_before)goto restore;
 for(unsigned i=0;i<11;++i){o->attempted_mmio=i+1;R32(setup[i][0])=setup[i][1];}
 for(unsigned i=0;i<3;++i){o->attempted_crtc=i+1;cw(cs[i][0],cs[i][1]);}
 o->forward_status=0x7568;
 for(unsigned i=0;i<11;++i){
  uint32_t value=R32(setup[i][0]);o->mmio_checked[i]=value;o->checked=i+1;
  if(value!=setup[i][1]){o->first_mismatch=i;o->expected=setup[i][1];o->observed=value;goto restore;}
 }
 for(unsigned i=0;i<4;++i){
  uint32_t value=cr(cs[i][0]);o->crtc_checked[i]=value;o->checked=12+i;
  uint32_t expected=i==3?o->crtc_before[i]:cs[i][1];
  if(value!=expected){o->first_mismatch=11+i;o->expected=expected;o->observed=value;goto restore;}
 }
 /* Only proceed once all fifteen preservation checks matched. */
 for(unsigned i=0;i<7;++i){o->h_attempted=i+1;R32(horizontal[i][0])=horizontal[i][1];}
 o->forward_status=0x7569;
 for(unsigned i=0;i<7;++i){
  uint32_t value=R32(horizontal[i][0]);o->h_checked[i]=value;o->h_count=i+1;
  if(value!=horizontal[i][1]){o->h_first=i;o->h_expected=horizontal[i][1];o->h_observed=value;goto restore;}
 }
 /* Next original SetGPURegister access only: (779-32)/8 == 93. */
 o->c4_attempted=1;cw(4,93);o->forward_status=0x756b;
 o->c4_checked=cr(4);o->c5_checked=cr(5);
 if(o->c4_checked!=93 || o->c5_checked!=o->c5_before)goto restore;
 /* Original next read/modify/write: preserve CR05 upper three bits. */
 o->c5_target=(o->c5_checked&0xe0)|((((779u-32u+16u)/8u)-1u)&0x1f);
 o->c5_attempted=1;cw(5,(uint8_t)o->c5_target);o->forward_status=0x756d;
 o->c5_after=cr(5);o->c4_after=cr(4);
 if(o->c5_after!=o->c5_target || o->c4_after!=93)goto restore;
 /* Next original CRTC total byte: (779/8)-5 == 92. */
 o->c0_target=(779u/8u)-5u;o->c0_attempted=1;cw(0,(uint8_t)o->c0_target);o->forward_status=0x756e;
 o->c0_after=cr(0);o->c4_after_c0=cr(4);o->c5_after_c0=cr(5);
 if(o->c0_after!=o->c0_target || o->c4_after_c0!=93 || o->c5_after_c0!=o->c5_target)goto restore;
 /* Next original horizontal blank-start byte: (720/8)-1 == 89. */
 o->c2_target=(720u/8u)-1u;o->c2_attempted=1;cw(2,(uint8_t)o->c2_target);o->forward_status=0x75610;
 o->c2_after=cr(2);o->c0_after_c2=cr(0);o->c4_after_c2=cr(4);o->c5_after_c2=cr(5);
 if(o->c2_after!=o->c2_target || o->c0_after_c2!=o->c0_target || o->c4_after_c2!=93 || o->c5_after_c2!=o->c5_target)goto restore;
 /* Next original horizontal blank-end byte; preserve own upper three bits. */
 o->c3_target=(o->c3_before&0xe0)|(((779u/8u)-1u)&0x1f);
 o->c3_attempted=1;cw(3,(uint8_t)o->c3_target);o->forward_status=0x75612;
 o->c3_after=cr(3);o->c0_after_c3=cr(0);o->c2_after_c3=cr(2);o->c4_after_c3=cr(4);o->c5_after_c3=cr(5);
 if(o->c3_after!=o->c3_target || o->c0_after_c3!=o->c0_target || o->c2_after_c3!=o->c2_target || o->c4_after_c3!=93 || o->c5_after_c3!=o->c5_target)goto restore;
 /* Original second CR05 write: replace only horizontal blank-end bit7. */
 o->c5b_before=o->c5_after_c3;
 o->c5b_target=(o->c5b_before&0x7f)|((((779u/8u)-1u)&0x20)<<2);
 o->c5b_attempted=1;cw(5,(uint8_t)o->c5b_target);o->forward_status=0x75614;
 o->c5b_after=cr(5);o->c0_after_c5b=cr(0);o->c2_after_c5b=cr(2);o->c3_after_c5b=cr(3);o->c4_after_c5b=cr(4);
 if(o->c5b_after!=o->c5b_target || o->c0_after_c5b!=o->c0_target || o->c2_after_c5b!=o->c2_target || o->c3_after_c5b!=o->c3_target || o->c4_after_c5b!=93)goto restore;
 o->forward_status=0x756;
restore:
 /* Undo only attempted writes, newest first, using own saved full bytes. */
 if(o->c5b_attempted){cw(5,(uint8_t)o->c5b_before);o->c5b_restored=cr(5);if(o->c5b_restored!=o->c5b_before)o->c5b_cleanup_mask=1;}
 if(o->c3_attempted)cw(3,(uint8_t)o->c3_before);
 if(o->c2_attempted)cw(2,(uint8_t)o->c2_before);
 if(o->c0_attempted)cw(0,(uint8_t)o->c0_before);
 if(o->c5_attempted)cw(5,(uint8_t)o->c5_before);
 if(o->c4_attempted)cw(4,(uint8_t)o->c4_before);
 o->c4_restored=cr(4);o->c5_restored=cr(5);o->c0_restored=cr(0);o->c2_restored=cr(2);o->c3_restored=cr(3);
 if(o->c3_restored!=o->c3_before)o->c3_cleanup_mask=1;
 if(o->c2_restored!=o->c2_before)o->c2_cleanup_mask=1;
 if(o->c0_restored!=o->c0_before)o->c0_cleanup_mask=1;
 if(o->c4_restored!=o->c4_before)o->c4_cleanup_mask|=1;
 if(o->c5_restored!=o->c5_before)o->c4_cleanup_mask|=2;
 /* Reverse own attempted writes, then check every horizontal value before enable.
  * A mismatch leaves output blank; the kernel caller persists it and reboots. */
 for(unsigned i=o->h_attempted;i>0;--i)R32(horizontal[i-1][0])=o->h_before[i-1];
 for(unsigned i=0;i<7;++i){o->h_restored[i]=R32(horizontal[i][0]);if(o->h_restored[i]!=o->h_before[i])o->h_cleanup_mask|=1u<<i;}
 /* Same bounded recovery as723/725: no guessed CR1b or CR22 restoration. */
 if(o->attempted_crtc>=3)cw(0x19,(uint8_t)o->crtc_before[2]);
 if(o->attempted_mmio>=9)R32(0x680630)=o->mmio_before[8];
 if(!o->h_cleanup_mask && !o->c4_cleanup_mask && !o->c0_cleanup_mask && !o->c2_cleanup_mask && !o->c3_cleanup_mask && !o->c5b_cleanup_mask){gate(4);sw((uint8_t)o->seq_before);o->output_restored=1;}
 o->seq_after=sr();
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
 if(o->forward_status!=0x7561 && o->forward_status!=0x7562 && !o->cleanup_ok)o->code=0x7565;
 if(o->h_cleanup_mask)o->code=0x756a;
 if(o->c4_cleanup_mask)o->code=0x756c;
 if(o->c0_cleanup_mask)o->code=0x756f;
 if(o->c2_cleanup_mask)o->code=0x75611;
 if(o->c3_cleanup_mask)o->code=0x75613;
 if(o->c5b_cleanup_mask)o->code=0x75615;
 if(o->forward_status!=0x7561 && !o->selectors_restored)o->code=0x7566;
 __asm__ volatile("pushl %1;popfl;pushfl;popl %0":"=&r"(restored):"r"(flags):"memory","cc");o->flags_restored=restored;
}
