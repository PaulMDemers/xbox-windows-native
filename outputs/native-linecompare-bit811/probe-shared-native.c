/* SPDX-License-Identifier: MIT
 * Distinct CR17 bit7 clear checkpoint after
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
static __attribute__((noinline)) uint8_t cr(uint8_t i){R8(0x6013d4)=i;return R8(0x6013d5);}
static __attribute__((noinline)) void cw(uint8_t i,uint8_t v){R8(0x6013d4)=i;R8(0x6013d5)=v;}
static uint8_t sr(void){R8(0xc03c4)=1;return R8(0xc03c5);}
static void sw(uint8_t v){R8(0xc03c4)=1;R8(0xc03c5)=v;}
static uint8_t gr4(void){R8(0xc03ce)=4;return R8(0xc03cf);}
static void gate(uint8_t v){__asm__ volatile("outb %0,%w1"::"a"(v),"d"((uint16_t)0x80d3):"memory");}
static const uint16_t sentinel_offsets[] = {
 (uint16_t)__builtin_offsetof(struct result811,first_mismatch),
 (uint16_t)__builtin_offsetof(struct result811,h_first),
 (uint16_t)__builtin_offsetof(struct result811,c5_restored),
 (uint16_t)__builtin_offsetof(struct result811,c5_checked),
 (uint16_t)__builtin_offsetof(struct result811,c4_restored),
 (uint16_t)__builtin_offsetof(struct result811,c4_checked),
 (uint16_t)__builtin_offsetof(struct result811,c4_after),
 (uint16_t)__builtin_offsetof(struct result811,c5_after),
 (uint16_t)__builtin_offsetof(struct result811,c5_after_c0),
 (uint16_t)__builtin_offsetof(struct result811,c4_after_c0),
 (uint16_t)__builtin_offsetof(struct result811,c0_restored),
 (uint16_t)__builtin_offsetof(struct result811,c0_after),
 (uint16_t)__builtin_offsetof(struct result811,c5_after_c2),
 (uint16_t)__builtin_offsetof(struct result811,c4_after_c2),
 (uint16_t)__builtin_offsetof(struct result811,c0_after_c2),
 (uint16_t)__builtin_offsetof(struct result811,c2_restored),
 (uint16_t)__builtin_offsetof(struct result811,c2_after),
 (uint16_t)__builtin_offsetof(struct result811,c5_after_c3),
 (uint16_t)__builtin_offsetof(struct result811,c4_after_c3),
 (uint16_t)__builtin_offsetof(struct result811,c2_after_c3),
 (uint16_t)__builtin_offsetof(struct result811,c0_after_c3),
 (uint16_t)__builtin_offsetof(struct result811,c3_restored),
 (uint16_t)__builtin_offsetof(struct result811,c3_after),
 (uint16_t)__builtin_offsetof(struct result811,c4_after_c5b),
 (uint16_t)__builtin_offsetof(struct result811,c3_after_c5b),
 (uint16_t)__builtin_offsetof(struct result811,c2_after_c5b),
 (uint16_t)__builtin_offsetof(struct result811,c0_after_c5b),
 (uint16_t)__builtin_offsetof(struct result811,c5b_restored),
 (uint16_t)__builtin_offsetof(struct result811,c5b_after),
 (uint16_t)__builtin_offsetof(struct result811,c5_after_c17),
 (uint16_t)__builtin_offsetof(struct result811,c4_after_c17),
 (uint16_t)__builtin_offsetof(struct result811,c3_after_c17),
 (uint16_t)__builtin_offsetof(struct result811,c2_after_c17),
 (uint16_t)__builtin_offsetof(struct result811,c0_after_c17),
 (uint16_t)__builtin_offsetof(struct result811,c17_restored),
 (uint16_t)__builtin_offsetof(struct result811,c17_after),
 (uint16_t)__builtin_offsetof(struct result811,c17_after_c1),
 (uint16_t)__builtin_offsetof(struct result811,c5_after_c1),
 (uint16_t)__builtin_offsetof(struct result811,c4_after_c1),
 (uint16_t)__builtin_offsetof(struct result811,c3_after_c1),
 (uint16_t)__builtin_offsetof(struct result811,c2_after_c1),
 (uint16_t)__builtin_offsetof(struct result811,c0_after_c1),
 (uint16_t)__builtin_offsetof(struct result811,c1_restored),
 (uint16_t)__builtin_offsetof(struct result811,c1_after),
 (uint16_t)__builtin_offsetof(struct result811,c17_after_c2b),
 (uint16_t)__builtin_offsetof(struct result811,c5_after_c2b),
 (uint16_t)__builtin_offsetof(struct result811,c4_after_c2b),
 (uint16_t)__builtin_offsetof(struct result811,c3_after_c2b),
 (uint16_t)__builtin_offsetof(struct result811,c1_after_c2b),
 (uint16_t)__builtin_offsetof(struct result811,c0_after_c2b),
 (uint16_t)__builtin_offsetof(struct result811,c2b_restored),
 (uint16_t)__builtin_offsetof(struct result811,c2b_after),
 (uint16_t)__builtin_offsetof(struct result811,c5_after_c17b),
 (uint16_t)__builtin_offsetof(struct result811,c4_after_c17b),
 (uint16_t)__builtin_offsetof(struct result811,c3_after_c17b),
 (uint16_t)__builtin_offsetof(struct result811,c2_after_c17b),
 (uint16_t)__builtin_offsetof(struct result811,c1_after_c17b),
 (uint16_t)__builtin_offsetof(struct result811,c0_after_c17b),
 (uint16_t)__builtin_offsetof(struct result811,c17b_restored),
 (uint16_t)__builtin_offsetof(struct result811,c17b_after),
 (uint16_t)__builtin_offsetof(struct result811,c13_restored_c19b),
 (uint16_t)__builtin_offsetof(struct result811,c5_after_c19b),
 (uint16_t)__builtin_offsetof(struct result811,c4_after_c19b),
 (uint16_t)__builtin_offsetof(struct result811,c3_after_c19b),
 (uint16_t)__builtin_offsetof(struct result811,c2_after_c19b),
 (uint16_t)__builtin_offsetof(struct result811,c1_after_c19b),
 (uint16_t)__builtin_offsetof(struct result811,c0_after_c19b),
 (uint16_t)__builtin_offsetof(struct result811,c17_after_c19b),
 (uint16_t)__builtin_offsetof(struct result811,c13_after_c19b),
 (uint16_t)__builtin_offsetof(struct result811,c19b_restored),
 (uint16_t)__builtin_offsetof(struct result811,c19b_after),
 (uint16_t)__builtin_offsetof(struct result811,c19_restored_c13),
 (uint16_t)__builtin_offsetof(struct result811,c5_after_c13),
 (uint16_t)__builtin_offsetof(struct result811,c4_after_c13),
 (uint16_t)__builtin_offsetof(struct result811,c3_after_c13),
 (uint16_t)__builtin_offsetof(struct result811,c2_after_c13),
 (uint16_t)__builtin_offsetof(struct result811,c1_after_c13),
 (uint16_t)__builtin_offsetof(struct result811,c0_after_c13),
 (uint16_t)__builtin_offsetof(struct result811,c17_after_c13),
 (uint16_t)__builtin_offsetof(struct result811,c19_after_c13),
 (uint16_t)__builtin_offsetof(struct result811,c13_restored),
 (uint16_t)__builtin_offsetof(struct result811,c13_after),
 (uint16_t)__builtin_offsetof(struct result811,v_after),
 (uint16_t)__builtin_offsetof(struct result811,v_restored),
 (uint16_t)__builtin_offsetof(struct result811,vtotal_after),
 (uint16_t)__builtin_offsetof(struct result811,vtotal_restored),
 (uint16_t)__builtin_offsetof(struct result811,vsyncstart_after),
 (uint16_t)__builtin_offsetof(struct result811,vsyncstart_restored),
 (uint16_t)__builtin_offsetof(struct result811,vsyncend_after),
 (uint16_t)__builtin_offsetof(struct result811,vsyncend_restored),
 (uint16_t)__builtin_offsetof(struct result811,vvalidend_after),
 (uint16_t)__builtin_offsetof(struct result811,vvalidend_restored),
 (uint16_t)__builtin_offsetof(struct result811,c13_v_after),
 (uint16_t)__builtin_offsetof(struct result811,c13_v_restored),
 (uint16_t)__builtin_offsetof(struct result811,c19_v_after),
 (uint16_t)__builtin_offsetof(struct result811,c19_v_restored),
 (uint16_t)__builtin_offsetof(struct result811,vt_after),
 (uint16_t)__builtin_offsetof(struct result811,vt_restored),
 (uint16_t)__builtin_offsetof(struct result811,vt_disp_after),
 (uint16_t)__builtin_offsetof(struct result811,vt_disp_restored),
 (uint16_t)__builtin_offsetof(struct result811,vt_syncstart_after),
 (uint16_t)__builtin_offsetof(struct result811,vt_syncstart_restored),
 (uint16_t)__builtin_offsetof(struct result811,vt_syncend_after),
 (uint16_t)__builtin_offsetof(struct result811,vt_syncend_restored),
 (uint16_t)__builtin_offsetof(struct result811,vt_validend_after),
 (uint16_t)__builtin_offsetof(struct result811,vt_validend_restored),
 (uint16_t)__builtin_offsetof(struct result811,vt_c13_after),
 (uint16_t)__builtin_offsetof(struct result811,vt_c13_restored),
 (uint16_t)__builtin_offsetof(struct result811,vt_c19_after),
 (uint16_t)__builtin_offsetof(struct result811,vt_c19_restored),
 (uint16_t)__builtin_offsetof(struct result811,vc_after),
 (uint16_t)__builtin_offsetof(struct result811,vc_restored),
 (uint16_t)__builtin_offsetof(struct result811,vc_disp_after),
 (uint16_t)__builtin_offsetof(struct result811,vc_disp_restored),
 (uint16_t)__builtin_offsetof(struct result811,vc_total_after),
 (uint16_t)__builtin_offsetof(struct result811,vc_total_restored),
 (uint16_t)__builtin_offsetof(struct result811,vc_syncstart_after),
 (uint16_t)__builtin_offsetof(struct result811,vc_syncstart_restored),
 (uint16_t)__builtin_offsetof(struct result811,vc_syncend_after),
 (uint16_t)__builtin_offsetof(struct result811,vc_syncend_restored),
 (uint16_t)__builtin_offsetof(struct result811,vc_validstart_after),
 (uint16_t)__builtin_offsetof(struct result811,vc_validstart_restored),
 (uint16_t)__builtin_offsetof(struct result811,vc_validend_after),
 (uint16_t)__builtin_offsetof(struct result811,vc_validend_restored),
 (uint16_t)__builtin_offsetof(struct result811,vc_c13_after),
 (uint16_t)__builtin_offsetof(struct result811,vc_c13_restored),
 (uint16_t)__builtin_offsetof(struct result811,vc_c19_after),
 (uint16_t)__builtin_offsetof(struct result811,vc_c19_restored),
 (uint16_t)__builtin_offsetof(struct result811,vs_after),
 (uint16_t)__builtin_offsetof(struct result811,vs_restored),
 (uint16_t)__builtin_offsetof(struct result811,vs_disp_after),
 (uint16_t)__builtin_offsetof(struct result811,vs_disp_restored),
 (uint16_t)__builtin_offsetof(struct result811,vs_total_after),
 (uint16_t)__builtin_offsetof(struct result811,vs_total_restored),
 (uint16_t)__builtin_offsetof(struct result811,vs_crtc_after),
 (uint16_t)__builtin_offsetof(struct result811,vs_crtc_restored),
 (uint16_t)__builtin_offsetof(struct result811,vs_syncstart_after),
 (uint16_t)__builtin_offsetof(struct result811,vs_syncstart_restored),
 (uint16_t)__builtin_offsetof(struct result811,vs_syncend_after),
 (uint16_t)__builtin_offsetof(struct result811,vs_syncend_restored),
 (uint16_t)__builtin_offsetof(struct result811,vs_validend_after),
 (uint16_t)__builtin_offsetof(struct result811,vs_validend_restored),
 (uint16_t)__builtin_offsetof(struct result811,vs_c13_after),
 (uint16_t)__builtin_offsetof(struct result811,vs_c13_restored),
 (uint16_t)__builtin_offsetof(struct result811,vs_c19_after),
 (uint16_t)__builtin_offsetof(struct result811,vs_c19_restored),
 (uint16_t)__builtin_offsetof(struct result811,sy_after),
 (uint16_t)__builtin_offsetof(struct result811,sy_restored),
 (uint16_t)__builtin_offsetof(struct result811,sy_disp_after),
 (uint16_t)__builtin_offsetof(struct result811,sy_disp_restored),
 (uint16_t)__builtin_offsetof(struct result811,sy_total_after),
 (uint16_t)__builtin_offsetof(struct result811,sy_total_restored),
 (uint16_t)__builtin_offsetof(struct result811,sy_crtc_after),
 (uint16_t)__builtin_offsetof(struct result811,sy_crtc_restored),
 (uint16_t)__builtin_offsetof(struct result811,sy_validstart_after),
 (uint16_t)__builtin_offsetof(struct result811,sy_validstart_restored),
 (uint16_t)__builtin_offsetof(struct result811,sy_syncend_after),
 (uint16_t)__builtin_offsetof(struct result811,sy_syncend_restored),
 (uint16_t)__builtin_offsetof(struct result811,sy_validend_after),
 (uint16_t)__builtin_offsetof(struct result811,sy_validend_restored),
 (uint16_t)__builtin_offsetof(struct result811,sy_c13_after),
 (uint16_t)__builtin_offsetof(struct result811,sy_c13_restored),
 (uint16_t)__builtin_offsetof(struct result811,sy_c19_after),
 (uint16_t)__builtin_offsetof(struct result811,sy_c19_restored),
 (uint16_t)__builtin_offsetof(struct result811,se_after),
 (uint16_t)__builtin_offsetof(struct result811,se_restored),
 (uint16_t)__builtin_offsetof(struct result811,se_disp_after),
 (uint16_t)__builtin_offsetof(struct result811,se_disp_restored),
 (uint16_t)__builtin_offsetof(struct result811,se_total_after),
 (uint16_t)__builtin_offsetof(struct result811,se_total_restored),
 (uint16_t)__builtin_offsetof(struct result811,se_crtc_after),
 (uint16_t)__builtin_offsetof(struct result811,se_crtc_restored),
 (uint16_t)__builtin_offsetof(struct result811,se_validstart_after),
 (uint16_t)__builtin_offsetof(struct result811,se_validstart_restored),
 (uint16_t)__builtin_offsetof(struct result811,se_syncstart_after),
 (uint16_t)__builtin_offsetof(struct result811,se_syncstart_restored),
 (uint16_t)__builtin_offsetof(struct result811,se_validend_after),
 (uint16_t)__builtin_offsetof(struct result811,se_validend_restored),
 (uint16_t)__builtin_offsetof(struct result811,se_c13_after),
 (uint16_t)__builtin_offsetof(struct result811,se_c13_restored),
 (uint16_t)__builtin_offsetof(struct result811,se_c19_after),
 (uint16_t)__builtin_offsetof(struct result811,se_c19_restored),
 (uint16_t)__builtin_offsetof(struct result811,ve_after),
 (uint16_t)__builtin_offsetof(struct result811,ve_restored),
 (uint16_t)__builtin_offsetof(struct result811,ve_disp_after),
 (uint16_t)__builtin_offsetof(struct result811,ve_disp_restored),
 (uint16_t)__builtin_offsetof(struct result811,ve_total_after),
 (uint16_t)__builtin_offsetof(struct result811,ve_total_restored),
 (uint16_t)__builtin_offsetof(struct result811,ve_crtc_after),
 (uint16_t)__builtin_offsetof(struct result811,ve_crtc_restored),
 (uint16_t)__builtin_offsetof(struct result811,ve_validstart_after),
 (uint16_t)__builtin_offsetof(struct result811,ve_validstart_restored),
 (uint16_t)__builtin_offsetof(struct result811,ve_syncstart_after),
 (uint16_t)__builtin_offsetof(struct result811,ve_syncstart_restored),
 (uint16_t)__builtin_offsetof(struct result811,ve_syncend_after),
 (uint16_t)__builtin_offsetof(struct result811,ve_syncend_restored),
 (uint16_t)__builtin_offsetof(struct result811,ve_c13_after),
 (uint16_t)__builtin_offsetof(struct result811,ve_c13_restored),
 (uint16_t)__builtin_offsetof(struct result811,ve_c19_after),
 (uint16_t)__builtin_offsetof(struct result811,ve_c19_restored),
 (uint16_t)__builtin_offsetof(struct result811,c7_after),
 (uint16_t)__builtin_offsetof(struct result811,c7_restored),
 (uint16_t)__builtin_offsetof(struct result811,c7_c6_after),
 (uint16_t)__builtin_offsetof(struct result811,c7_c6_restored),
 (uint16_t)__builtin_offsetof(struct result811,c7_c9_after),
 (uint16_t)__builtin_offsetof(struct result811,c7_c9_restored),
 (uint16_t)__builtin_offsetof(struct result811,c7_c10_after),
 (uint16_t)__builtin_offsetof(struct result811,c7_c10_restored),
 (uint16_t)__builtin_offsetof(struct result811,c7_c12_after),
 (uint16_t)__builtin_offsetof(struct result811,c7_c12_restored),
 (uint16_t)__builtin_offsetof(struct result811,c7_c15_after),
 (uint16_t)__builtin_offsetof(struct result811,c7_c15_restored),
 (uint16_t)__builtin_offsetof(struct result811,c7_c16_after),
 (uint16_t)__builtin_offsetof(struct result811,c7_c16_restored),
 (uint16_t)__builtin_offsetof(struct result811,c7_c18_after),
 (uint16_t)__builtin_offsetof(struct result811,c7_c18_restored),
 (uint16_t)__builtin_offsetof(struct result811,c7_c25_after),
 (uint16_t)__builtin_offsetof(struct result811,c7_c25_restored),
 (uint16_t)__builtin_offsetof(struct result811,c10_after),
 (uint16_t)__builtin_offsetof(struct result811,c10_restored),
 (uint16_t)__builtin_offsetof(struct result811,c10_c6_after),
 (uint16_t)__builtin_offsetof(struct result811,c10_c6_restored),
 (uint16_t)__builtin_offsetof(struct result811,c10_c7_after),
 (uint16_t)__builtin_offsetof(struct result811,c10_c7_restored),
 (uint16_t)__builtin_offsetof(struct result811,c10_c9_after),
 (uint16_t)__builtin_offsetof(struct result811,c10_c9_restored),
 (uint16_t)__builtin_offsetof(struct result811,c10_c12_after),
 (uint16_t)__builtin_offsetof(struct result811,c10_c12_restored),
 (uint16_t)__builtin_offsetof(struct result811,c10_c15_after),
 (uint16_t)__builtin_offsetof(struct result811,c10_c15_restored),
 (uint16_t)__builtin_offsetof(struct result811,c10_c16_after),
 (uint16_t)__builtin_offsetof(struct result811,c10_c16_restored),
 (uint16_t)__builtin_offsetof(struct result811,c10_c18_after),
 (uint16_t)__builtin_offsetof(struct result811,c10_c18_restored),
 (uint16_t)__builtin_offsetof(struct result811,c10_c25_after),
 (uint16_t)__builtin_offsetof(struct result811,c10_c25_restored),
 (uint16_t)__builtin_offsetof(struct result811,ct7_after),
 (uint16_t)__builtin_offsetof(struct result811,ct7_restored),
 (uint16_t)__builtin_offsetof(struct result811,ct7_c6_after),
 (uint16_t)__builtin_offsetof(struct result811,ct7_c6_restored),
 (uint16_t)__builtin_offsetof(struct result811,ct7_c9_after),
 (uint16_t)__builtin_offsetof(struct result811,ct7_c9_restored),
 (uint16_t)__builtin_offsetof(struct result811,ct7_c10_after),
 (uint16_t)__builtin_offsetof(struct result811,ct7_c10_restored),
 (uint16_t)__builtin_offsetof(struct result811,ct7_c12_after),
 (uint16_t)__builtin_offsetof(struct result811,ct7_c12_restored),
 (uint16_t)__builtin_offsetof(struct result811,ct7_c15_after),
 (uint16_t)__builtin_offsetof(struct result811,ct7_c15_restored),
 (uint16_t)__builtin_offsetof(struct result811,ct7_c16_after),
 (uint16_t)__builtin_offsetof(struct result811,ct7_c16_restored),
 (uint16_t)__builtin_offsetof(struct result811,ct7_c18_after),
 (uint16_t)__builtin_offsetof(struct result811,ct7_c18_restored),
 (uint16_t)__builtin_offsetof(struct result811,ct7_c25_after),
 (uint16_t)__builtin_offsetof(struct result811,ct7_c25_restored),
 (uint16_t)__builtin_offsetof(struct result811,ct6_after),
 (uint16_t)__builtin_offsetof(struct result811,ct6_restored),
 (uint16_t)__builtin_offsetof(struct result811,ct6_c7_after),
 (uint16_t)__builtin_offsetof(struct result811,ct6_c7_restored),
 (uint16_t)__builtin_offsetof(struct result811,ct6_c9_after),
 (uint16_t)__builtin_offsetof(struct result811,ct6_c9_restored),
 (uint16_t)__builtin_offsetof(struct result811,ct6_c10_after),
 (uint16_t)__builtin_offsetof(struct result811,ct6_c10_restored),
 (uint16_t)__builtin_offsetof(struct result811,ct6_c12_after),
 (uint16_t)__builtin_offsetof(struct result811,ct6_c12_restored),
 (uint16_t)__builtin_offsetof(struct result811,ct6_c15_after),
 (uint16_t)__builtin_offsetof(struct result811,ct6_c15_restored),
 (uint16_t)__builtin_offsetof(struct result811,ct6_c16_after),
 (uint16_t)__builtin_offsetof(struct result811,ct6_c16_restored),
 (uint16_t)__builtin_offsetof(struct result811,ct6_c18_after),
 (uint16_t)__builtin_offsetof(struct result811,ct6_c18_restored),
 (uint16_t)__builtin_offsetof(struct result811,ct6_c25_after),
 (uint16_t)__builtin_offsetof(struct result811,ct6_c25_restored),
 (uint16_t)__builtin_offsetof(struct result811,ct16_after),
 (uint16_t)__builtin_offsetof(struct result811,ct16_restored),
 (uint16_t)__builtin_offsetof(struct result811,ct16_c6_after),
 (uint16_t)__builtin_offsetof(struct result811,ct16_c6_restored),
 (uint16_t)__builtin_offsetof(struct result811,ct16_c7_after),
 (uint16_t)__builtin_offsetof(struct result811,ct16_c7_restored),
 (uint16_t)__builtin_offsetof(struct result811,ct16_c9_after),
 (uint16_t)__builtin_offsetof(struct result811,ct16_c9_restored),
 (uint16_t)__builtin_offsetof(struct result811,ct16_c10_after),
 (uint16_t)__builtin_offsetof(struct result811,ct16_c10_restored),
 (uint16_t)__builtin_offsetof(struct result811,ct16_c12_after),
 (uint16_t)__builtin_offsetof(struct result811,ct16_c12_restored),
 (uint16_t)__builtin_offsetof(struct result811,ct16_c15_after),
 (uint16_t)__builtin_offsetof(struct result811,ct16_c15_restored),
 (uint16_t)__builtin_offsetof(struct result811,ct16_c18_after),
 (uint16_t)__builtin_offsetof(struct result811,ct16_c18_restored),
 (uint16_t)__builtin_offsetof(struct result811,ct16_c25_after),
 (uint16_t)__builtin_offsetof(struct result811,ct16_c25_restored),
 (uint16_t)__builtin_offsetof(struct result811,cd7_after),
 (uint16_t)__builtin_offsetof(struct result811,cd7_restored),
 (uint16_t)__builtin_offsetof(struct result811,cd7_c6_after),
 (uint16_t)__builtin_offsetof(struct result811,cd7_c6_restored),
 (uint16_t)__builtin_offsetof(struct result811,cd7_c9_after),
 (uint16_t)__builtin_offsetof(struct result811,cd7_c9_restored),
 (uint16_t)__builtin_offsetof(struct result811,cd7_c10_after),
 (uint16_t)__builtin_offsetof(struct result811,cd7_c10_restored),
 (uint16_t)__builtin_offsetof(struct result811,cd7_c12_after),
 (uint16_t)__builtin_offsetof(struct result811,cd7_c12_restored),
 (uint16_t)__builtin_offsetof(struct result811,cd7_c15_after),
 (uint16_t)__builtin_offsetof(struct result811,cd7_c15_restored),
 (uint16_t)__builtin_offsetof(struct result811,cd7_c16_after),
 (uint16_t)__builtin_offsetof(struct result811,cd7_c16_restored),
 (uint16_t)__builtin_offsetof(struct result811,cd7_c18_after),
 (uint16_t)__builtin_offsetof(struct result811,cd7_c18_restored),
 (uint16_t)__builtin_offsetof(struct result811,cd7_c25_after),
 (uint16_t)__builtin_offsetof(struct result811,cd7_c25_restored),
 (uint16_t)__builtin_offsetof(struct result811,cd12_after),
 (uint16_t)__builtin_offsetof(struct result811,cd12_restored),
 (uint16_t)__builtin_offsetof(struct result811,cd12_c6_after),
 (uint16_t)__builtin_offsetof(struct result811,cd12_c6_restored),
 (uint16_t)__builtin_offsetof(struct result811,cd12_c7_after),
 (uint16_t)__builtin_offsetof(struct result811,cd12_c7_restored),
 (uint16_t)__builtin_offsetof(struct result811,cd12_c9_after),
 (uint16_t)__builtin_offsetof(struct result811,cd12_c9_restored),
 (uint16_t)__builtin_offsetof(struct result811,cd12_c10_after),
 (uint16_t)__builtin_offsetof(struct result811,cd12_c10_restored),
 (uint16_t)__builtin_offsetof(struct result811,cd12_c15_after),
 (uint16_t)__builtin_offsetof(struct result811,cd12_c15_restored),
 (uint16_t)__builtin_offsetof(struct result811,cd12_c16_after),
 (uint16_t)__builtin_offsetof(struct result811,cd12_c16_restored),
 (uint16_t)__builtin_offsetof(struct result811,cd12_c18_after),
 (uint16_t)__builtin_offsetof(struct result811,cd12_c18_restored),
 (uint16_t)__builtin_offsetof(struct result811,cd12_c25_after),
 (uint16_t)__builtin_offsetof(struct result811,cd12_c25_restored),
 (uint16_t)__builtin_offsetof(struct result811,cb9_after),
 (uint16_t)__builtin_offsetof(struct result811,cb9_restored),
 (uint16_t)__builtin_offsetof(struct result811,cb9_c6_after),
 (uint16_t)__builtin_offsetof(struct result811,cb9_c6_restored),
 (uint16_t)__builtin_offsetof(struct result811,cb9_c7_after),
 (uint16_t)__builtin_offsetof(struct result811,cb9_c7_restored),
 (uint16_t)__builtin_offsetof(struct result811,cb9_c10_after),
 (uint16_t)__builtin_offsetof(struct result811,cb9_c10_restored),
 (uint16_t)__builtin_offsetof(struct result811,cb9_c12_after),
 (uint16_t)__builtin_offsetof(struct result811,cb9_c12_restored),
 (uint16_t)__builtin_offsetof(struct result811,cb9_c15_after),
 (uint16_t)__builtin_offsetof(struct result811,cb9_c15_restored),
 (uint16_t)__builtin_offsetof(struct result811,cb9_c16_after),
 (uint16_t)__builtin_offsetof(struct result811,cb9_c16_restored),
 (uint16_t)__builtin_offsetof(struct result811,cb9_c18_after),
 (uint16_t)__builtin_offsetof(struct result811,cb9_c18_restored),
 (uint16_t)__builtin_offsetof(struct result811,cb9_c25_after),
 (uint16_t)__builtin_offsetof(struct result811,cb9_c25_restored),
 (uint16_t)__builtin_offsetof(struct result811,cb7_after),
 (uint16_t)__builtin_offsetof(struct result811,cb7_restored),
 (uint16_t)__builtin_offsetof(struct result811,cb7_c6_after),
 (uint16_t)__builtin_offsetof(struct result811,cb7_c6_restored),
 (uint16_t)__builtin_offsetof(struct result811,cb7_c9_after),
 (uint16_t)__builtin_offsetof(struct result811,cb7_c9_restored),
 (uint16_t)__builtin_offsetof(struct result811,cb7_c10_after),
 (uint16_t)__builtin_offsetof(struct result811,cb7_c10_restored),
 (uint16_t)__builtin_offsetof(struct result811,cb7_c12_after),
 (uint16_t)__builtin_offsetof(struct result811,cb7_c12_restored),
 (uint16_t)__builtin_offsetof(struct result811,cb7_c15_after),
 (uint16_t)__builtin_offsetof(struct result811,cb7_c15_restored),
 (uint16_t)__builtin_offsetof(struct result811,cb7_c16_after),
 (uint16_t)__builtin_offsetof(struct result811,cb7_c16_restored),
 (uint16_t)__builtin_offsetof(struct result811,cb7_c18_after),
 (uint16_t)__builtin_offsetof(struct result811,cb7_c18_restored),
 (uint16_t)__builtin_offsetof(struct result811,cb7_c25_after),
 (uint16_t)__builtin_offsetof(struct result811,cb7_c25_restored),
 (uint16_t)__builtin_offsetof(struct result811,cb15_after),
 (uint16_t)__builtin_offsetof(struct result811,cb15_restored),
 (uint16_t)__builtin_offsetof(struct result811,cb15_c6_after),
 (uint16_t)__builtin_offsetof(struct result811,cb15_c6_restored),
 (uint16_t)__builtin_offsetof(struct result811,cb15_c7_after),
 (uint16_t)__builtin_offsetof(struct result811,cb15_c7_restored),
 (uint16_t)__builtin_offsetof(struct result811,cb15_c9_after),
 (uint16_t)__builtin_offsetof(struct result811,cb15_c9_restored),
 (uint16_t)__builtin_offsetof(struct result811,cb15_c10_after),
 (uint16_t)__builtin_offsetof(struct result811,cb15_c10_restored),
 (uint16_t)__builtin_offsetof(struct result811,cb15_c12_after),
 (uint16_t)__builtin_offsetof(struct result811,cb15_c12_restored),
 (uint16_t)__builtin_offsetof(struct result811,cb15_c16_after),
 (uint16_t)__builtin_offsetof(struct result811,cb15_c16_restored),
 (uint16_t)__builtin_offsetof(struct result811,cb15_c18_after),
 (uint16_t)__builtin_offsetof(struct result811,cb15_c18_restored),
 (uint16_t)__builtin_offsetof(struct result811,cb15_c25_after),
 (uint16_t)__builtin_offsetof(struct result811,cb15_c25_restored),
 (uint16_t)__builtin_offsetof(struct result811,cl7_after),
 (uint16_t)__builtin_offsetof(struct result811,cl7_restored),
 (uint16_t)__builtin_offsetof(struct result811,cl7_c6_after),
 (uint16_t)__builtin_offsetof(struct result811,cl7_c6_restored),
 (uint16_t)__builtin_offsetof(struct result811,cl7_c9_after),
 (uint16_t)__builtin_offsetof(struct result811,cl7_c9_restored),
 (uint16_t)__builtin_offsetof(struct result811,cl7_c10_after),
 (uint16_t)__builtin_offsetof(struct result811,cl7_c10_restored),
 (uint16_t)__builtin_offsetof(struct result811,cl7_c12_after),
 (uint16_t)__builtin_offsetof(struct result811,cl7_c12_restored),
 (uint16_t)__builtin_offsetof(struct result811,cl7_c15_after),
 (uint16_t)__builtin_offsetof(struct result811,cl7_c15_restored),
 (uint16_t)__builtin_offsetof(struct result811,cl7_c16_after),
 (uint16_t)__builtin_offsetof(struct result811,cl7_c16_restored),
 (uint16_t)__builtin_offsetof(struct result811,cl7_c18_after),
 (uint16_t)__builtin_offsetof(struct result811,cl7_c18_restored),
 (uint16_t)__builtin_offsetof(struct result811,cl7_c25_after),
 (uint16_t)__builtin_offsetof(struct result811,cl7_c25_restored),
 (uint16_t)__builtin_offsetof(struct result811,cl9_after),
 (uint16_t)__builtin_offsetof(struct result811,cl9_restored),
 (uint16_t)__builtin_offsetof(struct result811,cl9_c6_after),
 (uint16_t)__builtin_offsetof(struct result811,cl9_c6_restored),
 (uint16_t)__builtin_offsetof(struct result811,cl9_c7_after),
 (uint16_t)__builtin_offsetof(struct result811,cl9_c7_restored),
 (uint16_t)__builtin_offsetof(struct result811,cl9_c10_after),
 (uint16_t)__builtin_offsetof(struct result811,cl9_c10_restored),
 (uint16_t)__builtin_offsetof(struct result811,cl9_c12_after),
 (uint16_t)__builtin_offsetof(struct result811,cl9_c12_restored),
 (uint16_t)__builtin_offsetof(struct result811,cl9_c15_after),
 (uint16_t)__builtin_offsetof(struct result811,cl9_c15_restored),
 (uint16_t)__builtin_offsetof(struct result811,cl9_c16_after),
 (uint16_t)__builtin_offsetof(struct result811,cl9_c16_restored),
 (uint16_t)__builtin_offsetof(struct result811,cl9_c18_after),
 (uint16_t)__builtin_offsetof(struct result811,cl9_c18_restored),
 (uint16_t)__builtin_offsetof(struct result811,cl9_c25_after),
 (uint16_t)__builtin_offsetof(struct result811,cl9_c25_restored),
};
void probe811(struct result811 *o)
{
 uint32_t flags,restored;*o=(struct result811){0};
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 for(unsigned i=0;i<sizeof(sentinel_offsets)/sizeof(sentinel_offsets[0]);++i)
  *(uint32_t *)((uint8_t *)o+sentinel_offsets[i])=0xffffffff;
 for(unsigned i=0;i<7;++i)o->h_checked[i]=o->h_restored[i]=0xffffffff;
 for(unsigned i=0;i<11;++i)o->mmio_checked[i]=o->mmio_restored[i]=0xffffffff;
 for(unsigned i=0;i<4;++i)o->crtc_checked[i]=o->crtc_restored[i]=0xffffffff;
 __asm__ volatile("pushfl;popl %0;cli":"=r"(flags)::"memory");o->flags_entry=flags;
 __asm__ volatile("pushfl;popl %0":"=r"(o->flags_critical)::"memory");
 __asm__ volatile("mov %%cr0,%0":"=r"(o->cr0));
 __asm__ volatile("mov %%cr3,%0":"=r"(o->cr3));
 __asm__ volatile("mov %%cr4,%0":"=r"(o->cr4));
 o->forward_status=0x8111;
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
 for(unsigned i=0;i<7;++i){o->h_before[i]=R32(horizontal[i][0]);if(o->h_before[i]!=horizontal[i][2])admitted=0;}
 o->c4_before=cr(4);o->c5_before=cr(5);o->c0_before=cr(0);o->c2_before=cr(2);o->c3_before=cr(3);
 if(o->c4_before!=0xa7 || o->c5_before!=0x31 || o->c0_before!=0xc8 || o->c2_before!=0x9f || o->c3_before!=0x8c)admitted=0;
 o->forward_status=0x8112;if(!admitted)goto selectors;
 sw(0x21);gate(5);o->forward_status=0x8113;if(sr()!=0x21)goto restore;
 cw(0x1f,0x57);o->unlock_read=cr(0x1f);
 o->forward_status=0x8114;
 if(cr(0x11)!=o->cr11_before || cr(0x22)!=o->cr22_before)goto restore;
 for(unsigned i=0;i<11;++i){o->attempted_mmio=i+1;R32(setup[i][0])=setup[i][1];}
 for(unsigned i=0;i<3;++i){o->attempted_crtc=i+1;cw(cs[i][0],cs[i][1]);}
 o->forward_status=0x8118;
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
 o->forward_status=0x8119;
 for(unsigned i=0;i<7;++i){
  uint32_t value=R32(horizontal[i][0]);o->h_checked[i]=value;o->h_count=i+1;
  if(value!=horizontal[i][1]){o->h_first=i;o->h_expected=horizontal[i][1];o->h_observed=value;goto restore;}
 }
 /* Next original SetGPURegister access only: (779-32)/8 == 93. */
 o->c4_attempted=1;cw(4,93);o->forward_status=0x811b;
 o->c4_checked=cr(4);o->c5_checked=cr(5);
 if(o->c4_checked!=93 || o->c5_checked!=o->c5_before)goto restore;
 /* Original next read/modify/write: preserve CR05 upper three bits. */
 o->c5_target=(o->c5_checked&0xe0)|((((779u-32u+16u)/8u)-1u)&0x1f);
 o->c5_attempted=1;cw(5,(uint8_t)o->c5_target);o->forward_status=0x811d;
 o->c5_after=cr(5);o->c4_after=cr(4);
 if(o->c5_after!=o->c5_target || o->c4_after!=93)goto restore;
 /* Next original CRTC total byte: (779/8)-5 == 92. */
 o->c0_target=(779u/8u)-5u;o->c0_attempted=1;cw(0,(uint8_t)o->c0_target);o->forward_status=0x811e;
 o->c0_after=cr(0);o->c4_after_c0=cr(4);o->c5_after_c0=cr(5);
 if(o->c0_after!=o->c0_target || o->c4_after_c0!=93 || o->c5_after_c0!=o->c5_target)goto restore;
 /* Next original horizontal blank-start byte: (720/8)-1 == 89. */
 o->c2_target=(720u/8u)-1u;o->c2_attempted=1;cw(2,(uint8_t)o->c2_target);o->forward_status=0x81110;
 o->c2_after=cr(2);o->c0_after_c2=cr(0);o->c4_after_c2=cr(4);o->c5_after_c2=cr(5);
 if(o->c2_after!=o->c2_target || o->c0_after_c2!=o->c0_target || o->c4_after_c2!=93 || o->c5_after_c2!=o->c5_target)goto restore;
 /* Next original horizontal blank-end byte; preserve own upper three bits. */
 o->c3_target=(o->c3_before&0xe0)|(((779u/8u)-1u)&0x1f);
 o->c3_attempted=1;cw(3,(uint8_t)o->c3_target);o->forward_status=0x81112;
 o->c3_after=cr(3);o->c0_after_c3=cr(0);o->c2_after_c3=cr(2);o->c4_after_c3=cr(4);o->c5_after_c3=cr(5);
 if(o->c3_after!=o->c3_target || o->c0_after_c3!=o->c0_target || o->c2_after_c3!=o->c2_target || o->c4_after_c3!=93 || o->c5_after_c3!=o->c5_target)goto restore;
 /* Original second CR05 write: replace only horizontal blank-end bit7. */
 o->c5b_before=o->c5_after_c3;
 o->c5b_target=(o->c5b_before&0x7f)|((((779u/8u)-1u)&0x20)<<2);
 o->c5b_attempted=1;cw(5,(uint8_t)o->c5b_target);o->forward_status=0x81114;
 o->c5b_after=cr(5);o->c0_after_c5b=cr(0);o->c2_after_c5b=cr(2);o->c3_after_c5b=cr(3);o->c4_after_c5b=cr(4);
 if(o->c5b_after!=o->c5b_target || o->c0_after_c5b!=o->c0_target || o->c2_after_c5b!=o->c2_target || o->c3_after_c5b!=o->c3_target || o->c4_after_c5b!=93)goto restore;
 /* Next original CR17 RMW: clear bit7 only, with fresh own-byte capture. */
 o->forward_status=0x81116;o->c17_before=cr(0x17);
 if(o->c17_before!=o->crtc_checked[1])goto restore;
 o->c17_target=o->c17_before&0x7f;o->c17_attempted=1;cw(0x17,(uint8_t)o->c17_target);
 o->c17_after=cr(0x17);o->c0_after_c17=cr(0);o->c2_after_c17=cr(2);o->c3_after_c17=cr(3);o->c4_after_c17=cr(4);o->c5_after_c17=cr(5);
 if(o->c17_after!=o->c17_target || o->c0_after_c17!=o->c0_target || o->c2_after_c17!=o->c2_target || o->c3_after_c17!=o->c3_target || o->c4_after_c17!=93 || o->c5_after_c17!=o->c5b_target)goto restore;
 /* Original next CR01 display-end byte, fresh own value for recovery. */
 o->forward_status=0x81118;o->c1_before=cr(1);o->c1_target=(720u/8u)-1u;
 o->c1_attempted=1;cw(1,(uint8_t)o->c1_target);
 o->c1_after=cr(1);o->c0_after_c1=cr(0);o->c2_after_c1=cr(2);o->c3_after_c1=cr(3);o->c4_after_c1=cr(4);o->c5_after_c1=cr(5);o->c17_after_c1=cr(0x17);
 if(o->c1_after!=o->c1_target || o->c0_after_c1!=o->c0_target || o->c2_after_c1!=o->c2_target || o->c3_after_c1!=o->c3_target || o->c4_after_c1!=93 || o->c5_after_c1!=o->c5b_target || o->c17_after_c1!=o->c17_target)goto restore;
 /* Original later CR02 write: same target, distinct source-ordered access. */
 o->forward_status=0x8111a;o->c2b_before=cr(2);
 if(o->c2b_before!=o->c2_after_c1)goto restore;
 o->c2b_target=(720u/8u)-1u;o->c2b_attempted=1;cw(2,(uint8_t)o->c2b_target);
 o->c2b_after=cr(2);o->c0_after_c2b=cr(0);o->c1_after_c2b=cr(1);o->c3_after_c2b=cr(3);o->c4_after_c2b=cr(4);o->c5_after_c2b=cr(5);o->c17_after_c2b=cr(0x17);
 if(o->c2b_after!=o->c2b_target || o->c0_after_c2b!=o->c0_target || o->c1_after_c2b!=o->c1_target || o->c3_after_c2b!=o->c3_target || o->c4_after_c2b!=93 || o->c5_after_c2b!=o->c5b_target || o->c17_after_c2b!=o->c17_target)goto restore;
 /* Original next CR17 RMW: set bit7, fresh own value under outer blank. */
 o->forward_status=0x8111c;o->c17b_before=cr(0x17);
 if(o->c17b_before!=o->c17_after_c2b)goto restore;
 o->c17b_target=(o->c17b_before&0x7f)|0x80;o->c17b_attempted=1;cw(0x17,(uint8_t)o->c17b_target);
 o->c17b_after=cr(0x17);o->c0_after_c17b=cr(0);o->c1_after_c17b=cr(1);o->c2_after_c17b=cr(2);o->c3_after_c17b=cr(3);o->c4_after_c17b=cr(4);o->c5_after_c17b=cr(5);
 if(o->c17b_after!=o->c17b_target || o->c0_after_c17b!=o->c0_target || o->c1_after_c17b!=o->c1_target || o->c2_after_c17b!=o->c2b_target || o->c3_after_c17b!=o->c3_target || o->c4_after_c17b!=93 || o->c5_after_c17b!=o->c5b_target)goto restore;
 /* Next original stride high bits: pixelDepth is four bytes, m=360. */
 o->forward_status=0x8111e;o->c19b_before=cr(0x19);o->c13_before_c19b=cr(0x13);
 if(o->c19b_before!=o->crtc_checked[2] || o->c13_before_c19b!=0x80)goto restore;
 o->c19b_target=(o->c19b_before&0x1f)|((((720u/8u)*4u)>>3)&0xe0);
 o->c19b_attempted=1;cw(0x19,(uint8_t)o->c19b_target);
 o->c19b_after=cr(0x19);o->c13_after_c19b=cr(0x13);o->c17_after_c19b=cr(0x17);
 o->c0_after_c19b=cr(0);o->c1_after_c19b=cr(1);o->c2_after_c19b=cr(2);o->c3_after_c19b=cr(3);o->c4_after_c19b=cr(4);o->c5_after_c19b=cr(5);
 if(o->c19b_after!=o->c19b_target || o->c13_after_c19b!=o->c13_before_c19b || o->c17_after_c19b!=o->c17b_target || o->c0_after_c19b!=o->c0_target || o->c1_after_c19b!=o->c1_target || o->c2_after_c19b!=o->c2b_target || o->c3_after_c19b!=o->c3_target || o->c4_after_c19b!=93 || o->c5_after_c19b!=o->c5b_target)goto restore;
 /* Next original stride low byte: pixelDepth is four bytes, m=360. */
 o->forward_status=0x81120;o->c13_before=cr(0x13);o->c19_before_c13=cr(0x19);
 if(o->c13_before!=o->c13_after_c19b || o->c19_before_c13!=o->c19b_after)goto restore;
 o->c13_target=((720u/8u)*4u)&0xff;
 o->c13_attempted=1;cw(0x13,(uint8_t)o->c13_target);
 o->c13_after=cr(0x13);o->c19_after_c13=cr(0x19);o->c17_after_c13=cr(0x17);
 o->c0_after_c13=cr(0);o->c1_after_c13=cr(1);o->c2_after_c13=cr(2);o->c3_after_c13=cr(3);o->c4_after_c13=cr(4);o->c5_after_c13=cr(5);
 if(o->c13_after!=o->c13_target || o->c19_after_c13!=o->c19_before_c13 || o->c17_after_c13!=o->c17b_target || o->c0_after_c13!=o->c0_target || o->c1_after_c13!=o->c1_target || o->c2_after_c13!=o->c2b_target || o->c3_after_c13!=o->c3_target || o->c4_after_c13!=93 || o->c5_after_c13!=o->c5b_target)goto restore;
 /* Next pinned source-order word: vertical display end only. */
 o->forward_status=0x81122;o->v_before=R32(0x680800);
 o->vtotal_before=R32(0x680804);o->vsyncstart_before=R32(0x68080c);o->vsyncend_before=R32(0x680810);o->vvalidend_before=R32(0x680818);o->c13_v_before=cr(0x13);o->c19_v_before=cr(0x19);
 if(o->v_before!=719 || o->vtotal_before!=749 || o->vsyncstart_before!=724 || o->vsyncend_before!=729 || o->vvalidend_before!=719 || o->c13_v_before!=104 || o->c19_v_before!=48)goto restore;
 o->v_target=480u-1u;o->v_attempted=1;R32(0x680800)=o->v_target;
 o->v_after=R32(0x680800);o->vtotal_after=R32(0x680804);o->vsyncstart_after=R32(0x68080c);o->vsyncend_after=R32(0x680810);o->vvalidend_after=R32(0x680818);o->c13_v_after=cr(0x13);o->c19_v_after=cr(0x19);
 if(o->v_after!=o->v_target || o->vtotal_after!=o->vtotal_before || o->vsyncstart_after!=o->vsyncstart_before || o->vsyncend_after!=o->vsyncend_before || o->vvalidend_after!=o->vvalidend_before || o->c13_v_after!=o->c13_v_before || o->c19_v_after!=o->c19_v_before)goto restore;
 /* Next pinned source-order word: vertical total only. */
 o->forward_status=0x81124;o->vt_before=R32(0x680804);
 o->vt_disp_before=R32(0x680800);o->vt_syncstart_before=R32(0x68080c);o->vt_syncend_before=R32(0x680810);o->vt_validend_before=R32(0x680818);o->vt_c13_before=cr(0x13);o->vt_c19_before=cr(0x19);
 if(o->vt_before!=749 || o->vt_disp_before!=479 || o->vt_syncstart_before!=724 || o->vt_syncend_before!=729 || o->vt_validend_before!=719 || o->vt_c13_before!=104 || o->vt_c19_before!=48)goto restore;
 o->vt_target=524u;o->vt_attempted=1;R32(0x680804)=o->vt_target;
 o->vt_after=R32(0x680804);o->vt_disp_after=R32(0x680800);o->vt_syncstart_after=R32(0x68080c);o->vt_syncend_after=R32(0x680810);o->vt_validend_after=R32(0x680818);o->vt_c13_after=cr(0x13);o->vt_c19_after=cr(0x19);
 if(o->vt_after!=o->vt_target || o->vt_disp_after!=o->vt_disp_before || o->vt_syncstart_after!=o->vt_syncstart_before || o->vt_syncend_after!=o->vt_syncend_before || o->vt_validend_after!=o->vt_validend_before || o->vt_c13_after!=o->vt_c13_before || o->vt_c19_after!=o->vt_c19_before)goto restore;
 /* Next pinned source-order word: NVVCRTC only; readonly775 baseline. */
 o->forward_status=0x81126;o->vc_before=R32(0x680808);
 o->vc_disp_before=R32(0x680800);o->vc_total_before=R32(0x680804);o->vc_syncstart_before=R32(0x68080c);o->vc_syncend_before=R32(0x680810);o->vc_validstart_before=R32(0x680814);o->vc_validend_before=R32(0x680818);o->vc_c13_before=cr(0x13);o->vc_c19_before=cr(0x19);
 if(o->vc_before!=719 || o->vc_disp_before!=479 || o->vc_total_before!=524 || o->vc_syncstart_before!=724 || o->vc_syncend_before!=729 || o->vc_validstart_before!=0 || o->vc_validend_before!=719 || o->vc_c13_before!=104 || o->vc_c19_before!=48)goto restore;
 o->vc_target=479u;o->vc_attempted=1;R32(0x680808)=o->vc_target;
 o->vc_after=R32(0x680808);o->vc_disp_after=R32(0x680800);o->vc_total_after=R32(0x680804);o->vc_syncstart_after=R32(0x68080c);o->vc_syncend_after=R32(0x680810);o->vc_validstart_after=R32(0x680814);o->vc_validend_after=R32(0x680818);o->vc_c13_after=cr(0x13);o->vc_c19_after=cr(0x19);
 if(o->vc_after!=o->vc_target || o->vc_disp_after!=o->vc_disp_before || o->vc_total_after!=o->vc_total_before || o->vc_syncstart_after!=o->vc_syncstart_before || o->vc_syncend_after!=o->vc_syncend_before || o->vc_validstart_after!=o->vc_validstart_before || o->vc_validend_after!=o->vc_validend_before || o->vc_c13_after!=o->vc_c13_before || o->vc_c19_after!=o->vc_c19_before)goto restore;
 /* Next pinned source-order word: NVVVALIDSTART same-value zero write. */
 o->forward_status=0x81128;o->vs_before=R32(0x680814);
 o->vs_disp_before=R32(0x680800);o->vs_total_before=R32(0x680804);o->vs_crtc_before=R32(0x680808);o->vs_syncstart_before=R32(0x68080c);o->vs_syncend_before=R32(0x680810);o->vs_validend_before=R32(0x680818);o->vs_c13_before=cr(0x13);o->vs_c19_before=cr(0x19);
 if(o->vs_before!=0 || o->vs_disp_before!=479 || o->vs_total_before!=524 || o->vs_crtc_before!=479 || o->vs_syncstart_before!=724 || o->vs_syncend_before!=729 || o->vs_validend_before!=719 || o->vs_c13_before!=104 || o->vs_c19_before!=48)goto restore;
 o->vs_target=0u;o->vs_attempted=1;R32(0x680814)=o->vs_target;
 o->vs_after=R32(0x680814);o->vs_disp_after=R32(0x680800);o->vs_total_after=R32(0x680804);o->vs_crtc_after=R32(0x680808);o->vs_syncstart_after=R32(0x68080c);o->vs_syncend_after=R32(0x680810);o->vs_validend_after=R32(0x680818);o->vs_c13_after=cr(0x13);o->vs_c19_after=cr(0x19);
 if(o->vs_after!=o->vs_target || o->vs_disp_after!=o->vs_disp_before || o->vs_total_after!=o->vs_total_before || o->vs_crtc_after!=o->vs_crtc_before || o->vs_syncstart_after!=o->vs_syncstart_before || o->vs_syncend_after!=o->vs_syncend_before || o->vs_validend_after!=o->vs_validend_before || o->vs_c13_after!=o->vs_c13_before || o->vs_c19_after!=o->vs_c19_before)goto restore;
 /* Next pinned source-order word: NVVSYNCSTART, target489 from GPU_PARAMETER. */
 o->forward_status=0x8112a;o->sy_before=R32(0x68080c);
 o->sy_disp_before=R32(0x680800);o->sy_total_before=R32(0x680804);o->sy_crtc_before=R32(0x680808);o->sy_validstart_before=R32(0x680814);o->sy_syncend_before=R32(0x680810);o->sy_validend_before=R32(0x680818);o->sy_c13_before=cr(0x13);o->sy_c19_before=cr(0x19);
 if(o->sy_before!=724 || o->sy_disp_before!=479 || o->sy_total_before!=524 || o->sy_crtc_before!=479 || o->sy_validstart_before!=0 || o->sy_syncend_before!=729 || o->sy_validend_before!=719 || o->sy_c13_before!=104 || o->sy_c19_before!=48)goto restore;
 o->sy_target=489u;o->sy_attempted=1;R32(0x68080c)=o->sy_target;
 o->sy_after=R32(0x68080c);o->sy_disp_after=R32(0x680800);o->sy_total_after=R32(0x680804);o->sy_crtc_after=R32(0x680808);o->sy_validstart_after=R32(0x680814);o->sy_syncend_after=R32(0x680810);o->sy_validend_after=R32(0x680818);o->sy_c13_after=cr(0x13);o->sy_c19_after=cr(0x19);
 if(o->sy_after!=o->sy_target || o->sy_disp_after!=o->sy_disp_before || o->sy_total_after!=o->sy_total_before || o->sy_crtc_after!=o->sy_crtc_before || o->sy_validstart_after!=o->sy_validstart_before || o->sy_syncend_after!=o->sy_syncend_before || o->sy_validend_after!=o->sy_validend_before || o->sy_c13_after!=o->sy_c13_before || o->sy_c19_after!=o->sy_c19_before)goto restore;
 /* Next pinned source-order word: NVVSYNCEND, nvvstart489+3=492. */
 o->forward_status=0x8112c;o->se_before=R32(0x680810);
 o->se_disp_before=R32(0x680800);o->se_total_before=R32(0x680804);o->se_crtc_before=R32(0x680808);o->se_validstart_before=R32(0x680814);o->se_syncstart_before=R32(0x68080c);o->se_validend_before=R32(0x680818);o->se_c13_before=cr(0x13);o->se_c19_before=cr(0x19);
 if(o->se_before!=729 || o->se_disp_before!=479 || o->se_total_before!=524 || o->se_crtc_before!=479 || o->se_validstart_before!=0 || o->se_syncstart_before!=489 || o->se_validend_before!=719 || o->se_c13_before!=104 || o->se_c19_before!=48)goto restore;
 o->se_target=492u;o->se_attempted=1;R32(0x680810)=o->se_target;
 o->se_after=R32(0x680810);o->se_disp_after=R32(0x680800);o->se_total_after=R32(0x680804);o->se_crtc_after=R32(0x680808);o->se_validstart_after=R32(0x680814);o->se_syncstart_after=R32(0x68080c);o->se_validend_after=R32(0x680818);o->se_c13_after=cr(0x13);o->se_c19_after=cr(0x19);
 if(o->se_after!=o->se_target || o->se_disp_after!=o->se_disp_before || o->se_total_after!=o->se_total_before || o->se_crtc_after!=o->se_crtc_before || o->se_validstart_after!=o->se_validstart_before || o->se_syncstart_after!=o->se_syncstart_before || o->se_validend_after!=o->se_validend_before || o->se_c13_after!=o->se_c13_before || o->se_c19_after!=o->se_c19_before)goto restore;
 /* Next pinned source-order word: NVVVALIDEND, yres480-1=479. */
 o->forward_status=0x8112e;o->ve_before=R32(0x680818);
 o->ve_disp_before=R32(0x680800);o->ve_total_before=R32(0x680804);o->ve_crtc_before=R32(0x680808);o->ve_validstart_before=R32(0x680814);o->ve_syncstart_before=R32(0x68080c);o->ve_syncend_before=R32(0x680810);o->ve_c13_before=cr(0x13);o->ve_c19_before=cr(0x19);
 if(o->ve_before!=719 || o->ve_disp_before!=479 || o->ve_total_before!=524 || o->ve_crtc_before!=479 || o->ve_validstart_before!=0 || o->ve_syncstart_before!=489 || o->ve_syncend_before!=492 || o->ve_c13_before!=104 || o->ve_c19_before!=48)goto restore;
 o->ve_target=479u;o->ve_attempted=1;R32(0x680818)=o->ve_target;
 o->ve_after=R32(0x680818);o->ve_disp_after=R32(0x680800);o->ve_total_after=R32(0x680804);o->ve_crtc_after=R32(0x680808);o->ve_validstart_after=R32(0x680814);o->ve_syncstart_after=R32(0x68080c);o->ve_syncend_after=R32(0x680810);o->ve_c13_after=cr(0x13);o->ve_c19_after=cr(0x19);
 if(o->ve_after!=o->ve_target || o->ve_disp_after!=o->ve_disp_before || o->ve_total_after!=o->ve_total_before || o->ve_crtc_after!=o->ve_crtc_before || o->ve_validstart_after!=o->ve_validstart_before || o->ve_syncstart_after!=o->ve_syncstart_before || o->ve_syncend_after!=o->ve_syncend_before || o->ve_c13_after!=o->ve_c13_before || o->ve_c19_after!=o->ve_c19_before)goto restore;
 /* First CRTC_VSYNCSTART operation: change only CR07 bits7/2; CR10 is untouched. */
 o->forward_status=0x81130;o->c7_before=cr(7);
 o->c7_c6_before=cr(0x6);o->c7_c9_before=cr(0x9);o->c7_c10_before=cr(0x10);o->c7_c12_before=cr(0x12);o->c7_c15_before=cr(0x15);o->c7_c16_before=cr(0x16);o->c7_c18_before=cr(0x18);o->c7_c25_before=cr(0x25);
 if(o->c7_before!=0xf0 || o->c7_c6_before!=0xec || o->c7_c9_before!=0x60 || o->c7_c10_before!=0xd4 || o->c7_c12_before!=0xcf || o->c7_c15_before!=0xcf || o->c7_c16_before!=0xed || o->c7_c18_before!=0xff || o->c7_c25_before!=0x10)goto restore;
 o->c7_target=(o->c7_before&0x7bu)|((489u>>2)&0x80u)|((489u>>6)&4u);o->c7_attempted=1;cw(7,o->c7_target);
 o->c7_after=cr(7);o->c7_c6_after=cr(0x6);o->c7_c9_after=cr(0x9);o->c7_c10_after=cr(0x10);o->c7_c12_after=cr(0x12);o->c7_c15_after=cr(0x15);o->c7_c16_after=cr(0x16);o->c7_c18_after=cr(0x18);o->c7_c25_after=cr(0x25);
 if(o->c7_after!=o->c7_target || o->c7_c6_after!=o->c7_c6_before || o->c7_c9_after!=o->c7_c9_before || o->c7_c10_after!=o->c7_c10_before || o->c7_c12_after!=o->c7_c12_before || o->c7_c15_after!=o->c7_c15_before || o->c7_c16_after!=o->c7_c16_before || o->c7_c18_after!=o->c7_c18_before || o->c7_c25_after!=o->c7_c25_before)goto restore;
 /* Second CRTC_VSYNCSTART operation: CR10 low byte, after qualified CR07 bits. */
 o->forward_status=0x81132;o->c10_before=cr(0x10);
 o->c10_c6_before=cr(0x6);o->c10_c7_before=cr(0x7);o->c10_c9_before=cr(0x9);o->c10_c12_before=cr(0x12);o->c10_c15_before=cr(0x15);o->c10_c16_before=cr(0x16);o->c10_c18_before=cr(0x18);o->c10_c25_before=cr(0x25);
 if(o->c10_before!=0xd4 || o->c10_c6_before!=0xec || o->c10_c7_before!=0x74 || o->c10_c9_before!=0x60 || o->c10_c12_before!=0xcf || o->c10_c15_before!=0xcf || o->c10_c16_before!=0xed || o->c10_c18_before!=0xff || o->c10_c25_before!=0x10)goto restore;
 o->c10_target=489u&0xffu;o->c10_attempted=1;cw(0x10,o->c10_target);
 o->c10_after=cr(0x10);o->c10_c6_after=cr(0x6);o->c10_c7_after=cr(0x7);o->c10_c9_after=cr(0x9);o->c10_c12_after=cr(0x12);o->c10_c15_after=cr(0x15);o->c10_c16_after=cr(0x16);o->c10_c18_after=cr(0x18);o->c10_c25_after=cr(0x25);
 if(o->c10_after!=o->c10_target || o->c10_c6_after!=o->c10_c6_before || o->c10_c7_after!=o->c10_c7_before || o->c10_c9_after!=o->c10_c9_before || o->c10_c12_after!=o->c10_c12_before || o->c10_c15_after!=o->c10_c15_before || o->c10_c16_after!=o->c10_c16_before || o->c10_c18_after!=o->c10_c18_before || o->c10_c25_after!=o->c10_c25_before)goto restore;
 /* CRTC_VTOTAL overflow: second CR07 operation, after CR10. Same-value 74. */
 o->forward_status=0x81134;o->ct7_before=cr(7);
 o->ct7_c6_before=cr(0x6);o->ct7_c9_before=cr(0x9);o->ct7_c10_before=cr(0x10);o->ct7_c12_before=cr(0x12);o->ct7_c15_before=cr(0x15);o->ct7_c16_before=cr(0x16);o->ct7_c18_before=cr(0x18);o->ct7_c25_before=cr(0x25);
 if(o->ct7_before!=0x74 || o->ct7_c6_before!=0xec || o->ct7_c9_before!=0x60 || o->ct7_c10_before!=0xe9 || o->ct7_c12_before!=0xcf || o->ct7_c15_before!=0xcf || o->ct7_c16_before!=0xed || o->ct7_c18_before!=0xff || o->ct7_c25_before!=0x10)goto restore;
 o->ct7_target=(o->ct7_before&0xdeu)|((524u>>4)&0x20u)|((524u>>8)&1u);o->ct7_attempted=1;cw(7,o->ct7_target);
 o->ct7_after=cr(7);o->ct7_c6_after=cr(0x6);o->ct7_c9_after=cr(0x9);o->ct7_c10_after=cr(0x10);o->ct7_c12_after=cr(0x12);o->ct7_c15_after=cr(0x15);o->ct7_c16_after=cr(0x16);o->ct7_c18_after=cr(0x18);o->ct7_c25_after=cr(0x25);
 if(o->ct7_after!=o->ct7_target || o->ct7_c6_after!=o->ct7_c6_before || o->ct7_c9_after!=o->ct7_c9_before || o->ct7_c10_after!=o->ct7_c10_before || o->ct7_c12_after!=o->ct7_c12_before || o->ct7_c15_after!=o->ct7_c15_before || o->ct7_c16_after!=o->ct7_c16_before || o->ct7_c18_after!=o->ct7_c18_before || o->ct7_c25_after!=o->ct7_c25_before)goto restore;
 /* CRTC_VTOTAL low byte after the second CR07 operation. */
 o->forward_status=0x81136;o->ct6_before=cr(6);
 o->ct6_c7_before=cr(0x7);o->ct6_c9_before=cr(0x9);o->ct6_c10_before=cr(0x10);o->ct6_c12_before=cr(0x12);o->ct6_c15_before=cr(0x15);o->ct6_c16_before=cr(0x16);o->ct6_c18_before=cr(0x18);o->ct6_c25_before=cr(0x25);
 if(o->ct6_before!=0xec || o->ct6_c7_before!=0x74 || o->ct6_c9_before!=0x60 || o->ct6_c10_before!=0xe9 || o->ct6_c12_before!=0xcf || o->ct6_c15_before!=0xcf || o->ct6_c16_before!=0xed || o->ct6_c18_before!=0xff || o->ct6_c25_before!=0x10)goto restore;
 o->ct6_target=(524u&0xffu);o->ct6_attempted=1;cw(6,o->ct6_target);
 o->ct6_after=cr(6);o->ct6_c7_after=cr(0x7);o->ct6_c9_after=cr(0x9);o->ct6_c10_after=cr(0x10);o->ct6_c12_after=cr(0x12);o->ct6_c15_after=cr(0x15);o->ct6_c16_after=cr(0x16);o->ct6_c18_after=cr(0x18);o->ct6_c25_after=cr(0x25);
 if(o->ct6_after!=o->ct6_target || o->ct6_c7_after!=o->ct6_c7_before || o->ct6_c9_after!=o->ct6_c9_before || o->ct6_c10_after!=o->ct6_c10_before || o->ct6_c12_after!=o->ct6_c12_before || o->ct6_c15_after!=o->ct6_c15_before || o->ct6_c16_after!=o->ct6_c16_before || o->ct6_c18_after!=o->ct6_c18_before || o->ct6_c25_after!=o->ct6_c25_before)goto restore;
 /* CRTC_VBLANKEND: preserve bit7 and replace low seven bits from total524. */
 o->forward_status=0x81138;o->ct16_before=cr(0x16);
 o->ct16_c6_before=cr(0x6);o->ct16_c7_before=cr(0x7);o->ct16_c9_before=cr(0x9);o->ct16_c10_before=cr(0x10);o->ct16_c12_before=cr(0x12);o->ct16_c15_before=cr(0x15);o->ct16_c18_before=cr(0x18);o->ct16_c25_before=cr(0x25);
 if(o->ct16_before!=0xed || o->ct16_c6_before!=0xc || o->ct16_c7_before!=0x74 || o->ct16_c9_before!=0x60 || o->ct16_c10_before!=0xe9 || o->ct16_c12_before!=0xcf || o->ct16_c15_before!=0xcf || o->ct16_c18_before!=0xff || o->ct16_c25_before!=0x10)goto restore;
 o->ct16_target=(o->ct16_before&0x80u)|(524u&0x7fu);o->ct16_attempted=1;cw(0x16,o->ct16_target);
 o->ct16_after=cr(0x16);o->ct16_c6_after=cr(0x6);o->ct16_c7_after=cr(0x7);o->ct16_c9_after=cr(0x9);o->ct16_c10_after=cr(0x10);o->ct16_c12_after=cr(0x12);o->ct16_c15_after=cr(0x15);o->ct16_c18_after=cr(0x18);o->ct16_c25_after=cr(0x25);
 if(o->ct16_after!=o->ct16_target || o->ct16_c6_after!=o->ct16_c6_before || o->ct16_c7_after!=o->ct16_c7_before || o->ct16_c9_after!=o->ct16_c9_before || o->ct16_c10_after!=o->ct16_c10_before || o->ct16_c12_after!=o->ct16_c12_before || o->ct16_c15_after!=o->ct16_c15_before || o->ct16_c18_after!=o->ct16_c18_before || o->ct16_c25_after!=o->ct16_c25_before)goto restore;
 /* CRTC_VDISPEND overflow bits: yres480 minus1, preserve unrelated CR07 bits. */
 o->forward_status=0x8113a;o->cd7_before=cr(7);
 o->cd7_c6_before=cr(0x6);o->cd7_c9_before=cr(0x9);o->cd7_c10_before=cr(0x10);o->cd7_c12_before=cr(0x12);o->cd7_c15_before=cr(0x15);o->cd7_c16_before=cr(0x16);o->cd7_c18_before=cr(0x18);o->cd7_c25_before=cr(0x25);
 if(o->cd7_before!=0x74 || o->cd7_c6_before!=0xc || o->cd7_c9_before!=0x60 || o->cd7_c10_before!=0xe9 || o->cd7_c12_before!=0xcf || o->cd7_c15_before!=0xcf || o->cd7_c16_before!=0x8c || o->cd7_c18_before!=0xff || o->cd7_c25_before!=0x10)goto restore;
 o->cd7_target=(o->cd7_before&0xbdu)|(((480u-1u)>>3)&0x40u)|(((480u-1u)>>7)&0x02u);o->cd7_attempted=1;cw(7,o->cd7_target);
 o->cd7_after=cr(7);o->cd7_c6_after=cr(0x6);o->cd7_c9_after=cr(0x9);o->cd7_c10_after=cr(0x10);o->cd7_c12_after=cr(0x12);o->cd7_c15_after=cr(0x15);o->cd7_c16_after=cr(0x16);o->cd7_c18_after=cr(0x18);o->cd7_c25_after=cr(0x25);
 if(o->cd7_after!=o->cd7_target || o->cd7_c6_after!=o->cd7_c6_before || o->cd7_c9_after!=o->cd7_c9_before || o->cd7_c10_after!=o->cd7_c10_before || o->cd7_c12_after!=o->cd7_c12_before || o->cd7_c15_after!=o->cd7_c15_before || o->cd7_c16_after!=o->cd7_c16_before || o->cd7_c18_after!=o->cd7_c18_before || o->cd7_c25_after!=o->cd7_c25_before)goto restore;
 /* CRTC_VDISPEND low byte, pinned704 yres480 minus1. */
 o->forward_status=0x8113c;o->cd12_before=cr(0x12);
 o->cd12_c6_before=cr(0x6);o->cd12_c7_before=cr(0x7);o->cd12_c9_before=cr(0x9);o->cd12_c10_before=cr(0x10);o->cd12_c15_before=cr(0x15);o->cd12_c16_before=cr(0x16);o->cd12_c18_before=cr(0x18);o->cd12_c25_before=cr(0x25);
 if(o->cd12_before!=0xcf || o->cd12_c6_before!=0xc || o->cd12_c7_before!=0x36 || o->cd12_c9_before!=0x60 || o->cd12_c10_before!=0xe9 || o->cd12_c15_before!=0xcf || o->cd12_c16_before!=0x8c || o->cd12_c18_before!=0xff || o->cd12_c25_before!=0x10)goto restore;
 o->cd12_target=(480u-1u)&0xffu;o->cd12_attempted=1;cw(0x12,o->cd12_target);
 o->cd12_after=cr(0x12);o->cd12_c6_after=cr(0x6);o->cd12_c7_after=cr(0x7);o->cd12_c9_after=cr(0x9);o->cd12_c10_after=cr(0x10);o->cd12_c15_after=cr(0x15);o->cd12_c16_after=cr(0x16);o->cd12_c18_after=cr(0x18);o->cd12_c25_after=cr(0x25);
 if(o->cd12_after!=o->cd12_target || o->cd12_c6_after!=o->cd12_c6_before || o->cd12_c7_after!=o->cd12_c7_before || o->cd12_c9_after!=o->cd12_c9_before || o->cd12_c10_after!=o->cd12_c10_before || o->cd12_c15_after!=o->cd12_c15_before || o->cd12_c16_after!=o->cd12_c16_before || o->cd12_c18_after!=o->cd12_c18_before || o->cd12_c25_after!=o->cd12_c25_before)goto restore;
 /* CRTC_VBLANKSTART bit5, pinned704 yres480 minus1. */
 o->forward_status=0x8113e;o->cb9_before=cr(9);
 o->cb9_c6_before=cr(0x6);o->cb9_c7_before=cr(0x7);o->cb9_c10_before=cr(0x10);o->cb9_c12_before=cr(0x12);o->cb9_c15_before=cr(0x15);o->cb9_c16_before=cr(0x16);o->cb9_c18_before=cr(0x18);o->cb9_c25_before=cr(0x25);
 if(o->cb9_before!=0x60 || o->cb9_c6_before!=0xc || o->cb9_c7_before!=0x36 || o->cb9_c10_before!=0xe9 || o->cb9_c12_before!=0xdf || o->cb9_c15_before!=0xcf || o->cb9_c16_before!=0x8c || o->cb9_c18_before!=0xff || o->cb9_c25_before!=0x10)goto restore;
 o->cb9_target=(o->cb9_before&0xdfu)|(((480u-1u)>>4)&0x20u);o->cb9_attempted=1;cw(9,o->cb9_target);
 o->cb9_after=cr(9);o->cb9_c6_after=cr(0x6);o->cb9_c7_after=cr(0x7);o->cb9_c10_after=cr(0x10);o->cb9_c12_after=cr(0x12);o->cb9_c15_after=cr(0x15);o->cb9_c16_after=cr(0x16);o->cb9_c18_after=cr(0x18);o->cb9_c25_after=cr(0x25);
 if(o->cb9_after!=o->cb9_target || o->cb9_c6_after!=o->cb9_c6_before || o->cb9_c7_after!=o->cb9_c7_before || o->cb9_c10_after!=o->cb9_c10_before || o->cb9_c12_after!=o->cb9_c12_before || o->cb9_c15_after!=o->cb9_c15_before || o->cb9_c16_after!=o->cb9_c16_before || o->cb9_c18_after!=o->cb9_c18_before || o->cb9_c25_after!=o->cb9_c25_before)goto restore;
 /* CRTC_VBLANKSTART bit3, pinned704 yres480 minus1. */
 o->forward_status=0x81140;o->cb7_before=cr(7);
 o->cb7_c6_before=cr(0x6);o->cb7_c9_before=cr(0x9);o->cb7_c10_before=cr(0x10);o->cb7_c12_before=cr(0x12);o->cb7_c15_before=cr(0x15);o->cb7_c16_before=cr(0x16);o->cb7_c18_before=cr(0x18);o->cb7_c25_before=cr(0x25);
 if(o->cb7_before!=0x36 || o->cb7_c6_before!=0xc || o->cb7_c9_before!=0x40 || o->cb7_c10_before!=0xe9 || o->cb7_c12_before!=0xdf || o->cb7_c15_before!=0xcf || o->cb7_c16_before!=0x8c || o->cb7_c18_before!=0xff || o->cb7_c25_before!=0x10)goto restore;
 o->cb7_target=(o->cb7_before&0xf7u)|(((480u-1u)>>5)&0x08u);o->cb7_attempted=1;cw(7,o->cb7_target);
 o->cb7_after=cr(7);o->cb7_c6_after=cr(0x6);o->cb7_c9_after=cr(0x9);o->cb7_c10_after=cr(0x10);o->cb7_c12_after=cr(0x12);o->cb7_c15_after=cr(0x15);o->cb7_c16_after=cr(0x16);o->cb7_c18_after=cr(0x18);o->cb7_c25_after=cr(0x25);
 if(o->cb7_after!=o->cb7_target || o->cb7_c6_after!=o->cb7_c6_before || o->cb7_c9_after!=o->cb7_c9_before || o->cb7_c10_after!=o->cb7_c10_before || o->cb7_c12_after!=o->cb7_c12_before || o->cb7_c15_after!=o->cb7_c15_before || o->cb7_c16_after!=o->cb7_c16_before || o->cb7_c18_after!=o->cb7_c18_before || o->cb7_c25_after!=o->cb7_c25_before)goto restore;
 /* CRTC_VBLANKSTART low byte, pinned704 yres480 minus1. */
 o->forward_status=0x81142;o->cb15_before=cr(0x15);
 o->cb15_c6_before=cr(0x6);o->cb15_c7_before=cr(0x7);o->cb15_c9_before=cr(0x9);o->cb15_c10_before=cr(0x10);o->cb15_c12_before=cr(0x12);o->cb15_c16_before=cr(0x16);o->cb15_c18_before=cr(0x18);o->cb15_c25_before=cr(0x25);
 if(o->cb15_before!=0xcf || o->cb15_c6_before!=0xc || o->cb15_c7_before!=0x3e || o->cb15_c9_before!=0x40 || o->cb15_c10_before!=0xe9 || o->cb15_c12_before!=0xdf || o->cb15_c16_before!=0x8c || o->cb15_c18_before!=0xff || o->cb15_c25_before!=0x10)goto restore;
 o->cb15_target=(480u-1u)&0xffu;o->cb15_attempted=1;cw(0x15,o->cb15_target);
 o->cb15_after=cr(0x15);o->cb15_c6_after=cr(0x6);o->cb15_c7_after=cr(0x7);o->cb15_c9_after=cr(0x9);o->cb15_c10_after=cr(0x10);o->cb15_c12_after=cr(0x12);o->cb15_c16_after=cr(0x16);o->cb15_c18_after=cr(0x18);o->cb15_c25_after=cr(0x25);
 if(o->cb15_after!=o->cb15_target || o->cb15_c6_after!=o->cb15_c6_before || o->cb15_c7_after!=o->cb15_c7_before || o->cb15_c9_after!=o->cb15_c9_before || o->cb15_c10_after!=o->cb15_c10_before || o->cb15_c12_after!=o->cb15_c12_before || o->cb15_c16_after!=o->cb15_c16_before || o->cb15_c18_after!=o->cb15_c18_before || o->cb15_c25_after!=o->cb15_c25_before)goto restore;
 /* CRTC_LINECOMP high bit, pinned704 m=0x3ff; same-value at this baseline. */
 o->forward_status=0x81144;o->cl7_before=cr(7);
 o->cl7_c6_before=cr(0x6);o->cl7_c9_before=cr(0x9);o->cl7_c10_before=cr(0x10);o->cl7_c12_before=cr(0x12);o->cl7_c15_before=cr(0x15);o->cl7_c16_before=cr(0x16);o->cl7_c18_before=cr(0x18);o->cl7_c25_before=cr(0x25);
 if(o->cl7_before!=0x3e || o->cl7_c6_before!=0xc || o->cl7_c9_before!=0x40 || o->cl7_c10_before!=0xe9 || o->cl7_c12_before!=0xdf || o->cl7_c15_before!=0xdf || o->cl7_c16_before!=0x8c || o->cl7_c18_before!=0xff || o->cl7_c25_before!=0x10)goto restore;
 o->cl7_target=(o->cl7_before&0xefu)|((0x3ffu>>4)&0x10u);o->cl7_attempted=1;cw(7,o->cl7_target);
 o->cl7_after=cr(7);o->cl7_c6_after=cr(0x6);o->cl7_c9_after=cr(0x9);o->cl7_c10_after=cr(0x10);o->cl7_c12_after=cr(0x12);o->cl7_c15_after=cr(0x15);o->cl7_c16_after=cr(0x16);o->cl7_c18_after=cr(0x18);o->cl7_c25_after=cr(0x25);
 if(o->cl7_after!=o->cl7_target || o->cl7_c6_after!=o->cl7_c6_before || o->cl7_c9_after!=o->cl7_c9_before || o->cl7_c10_after!=o->cl7_c10_before || o->cl7_c12_after!=o->cl7_c12_before || o->cl7_c15_after!=o->cl7_c15_before || o->cl7_c16_after!=o->cl7_c16_before || o->cl7_c18_after!=o->cl7_c18_before || o->cl7_c25_after!=o->cl7_c25_before)goto restore;
 /* CRTC_LINECOMP bit6, pinned704 m=0x3ff; same-value at this baseline. */
 o->forward_status=0x81146;o->cl9_before=cr(9);
 o->cl9_c6_before=cr(0x6);o->cl9_c7_before=cr(0x7);o->cl9_c10_before=cr(0x10);o->cl9_c12_before=cr(0x12);o->cl9_c15_before=cr(0x15);o->cl9_c16_before=cr(0x16);o->cl9_c18_before=cr(0x18);o->cl9_c25_before=cr(0x25);
 if(o->cl9_before!=0x40 || o->cl9_c6_before!=0xc || o->cl9_c7_before!=0x3e || o->cl9_c10_before!=0xe9 || o->cl9_c12_before!=0xdf || o->cl9_c15_before!=0xdf || o->cl9_c16_before!=0x8c || o->cl9_c18_before!=0xff || o->cl9_c25_before!=0x10)goto restore;
 o->cl9_target=(o->cl9_before&0xbfu)|((0x3ffu>>3)&0x40u);o->cl9_attempted=1;cw(9,o->cl9_target);
 o->cl9_after=cr(9);o->cl9_c6_after=cr(0x6);o->cl9_c7_after=cr(0x7);o->cl9_c10_after=cr(0x10);o->cl9_c12_after=cr(0x12);o->cl9_c15_after=cr(0x15);o->cl9_c16_after=cr(0x16);o->cl9_c18_after=cr(0x18);o->cl9_c25_after=cr(0x25);
 if(o->cl9_after!=o->cl9_target || o->cl9_c6_after!=o->cl9_c6_before || o->cl9_c7_after!=o->cl9_c7_before || o->cl9_c10_after!=o->cl9_c10_before || o->cl9_c12_after!=o->cl9_c12_before || o->cl9_c15_after!=o->cl9_c15_before || o->cl9_c16_after!=o->cl9_c16_before || o->cl9_c18_after!=o->cl9_c18_before || o->cl9_c25_after!=o->cl9_c25_before)goto restore;
 o->forward_status=0x811;
restore:
 /* Undo only attempted writes, newest first, using own saved full bytes. */
 if(o->cl9_attempted){cw(9,o->cl9_before);o->cl9_restored=cr(9);o->cl9_c6_restored=cr(0x6);o->cl9_c7_restored=cr(0x7);o->cl9_c10_restored=cr(0x10);o->cl9_c12_restored=cr(0x12);o->cl9_c15_restored=cr(0x15);o->cl9_c16_restored=cr(0x16);o->cl9_c18_restored=cr(0x18);o->cl9_c25_restored=cr(0x25);if(o->cl9_restored!=o->cl9_before)o->cl9_cleanup_mask|=1;if(o->cl9_c6_restored!=o->cl9_c6_before)o->cl9_cleanup_mask|=2;if(o->cl9_c7_restored!=o->cl9_c7_before)o->cl9_cleanup_mask|=4;if(o->cl9_c10_restored!=o->cl9_c10_before)o->cl9_cleanup_mask|=8;if(o->cl9_c12_restored!=o->cl9_c12_before)o->cl9_cleanup_mask|=16;if(o->cl9_c15_restored!=o->cl9_c15_before)o->cl9_cleanup_mask|=32;if(o->cl9_c16_restored!=o->cl9_c16_before)o->cl9_cleanup_mask|=64;if(o->cl9_c18_restored!=o->cl9_c18_before)o->cl9_cleanup_mask|=128;if(o->cl9_c25_restored!=o->cl9_c25_before)o->cl9_cleanup_mask|=256;}
 if(o->cl7_attempted){cw(7,o->cl7_before);o->cl7_restored=cr(7);o->cl7_c6_restored=cr(0x6);o->cl7_c9_restored=cr(0x9);o->cl7_c10_restored=cr(0x10);o->cl7_c12_restored=cr(0x12);o->cl7_c15_restored=cr(0x15);o->cl7_c16_restored=cr(0x16);o->cl7_c18_restored=cr(0x18);o->cl7_c25_restored=cr(0x25);if(o->cl7_restored!=o->cl7_before)o->cl7_cleanup_mask|=1;if(o->cl7_c6_restored!=o->cl7_c6_before)o->cl7_cleanup_mask|=2;if(o->cl7_c9_restored!=o->cl7_c9_before)o->cl7_cleanup_mask|=4;if(o->cl7_c10_restored!=o->cl7_c10_before)o->cl7_cleanup_mask|=8;if(o->cl7_c12_restored!=o->cl7_c12_before)o->cl7_cleanup_mask|=16;if(o->cl7_c15_restored!=o->cl7_c15_before)o->cl7_cleanup_mask|=32;if(o->cl7_c16_restored!=o->cl7_c16_before)o->cl7_cleanup_mask|=64;if(o->cl7_c18_restored!=o->cl7_c18_before)o->cl7_cleanup_mask|=128;if(o->cl7_c25_restored!=o->cl7_c25_before)o->cl7_cleanup_mask|=256;}
 if(o->cb15_attempted){cw(0x15,o->cb15_before);o->cb15_restored=cr(0x15);o->cb15_c6_restored=cr(0x6);o->cb15_c7_restored=cr(0x7);o->cb15_c9_restored=cr(0x9);o->cb15_c10_restored=cr(0x10);o->cb15_c12_restored=cr(0x12);o->cb15_c16_restored=cr(0x16);o->cb15_c18_restored=cr(0x18);o->cb15_c25_restored=cr(0x25);if(o->cb15_restored!=o->cb15_before)o->cb15_cleanup_mask|=1;if(o->cb15_c6_restored!=o->cb15_c6_before)o->cb15_cleanup_mask|=2;if(o->cb15_c7_restored!=o->cb15_c7_before)o->cb15_cleanup_mask|=4;if(o->cb15_c9_restored!=o->cb15_c9_before)o->cb15_cleanup_mask|=8;if(o->cb15_c10_restored!=o->cb15_c10_before)o->cb15_cleanup_mask|=16;if(o->cb15_c12_restored!=o->cb15_c12_before)o->cb15_cleanup_mask|=32;if(o->cb15_c16_restored!=o->cb15_c16_before)o->cb15_cleanup_mask|=64;if(o->cb15_c18_restored!=o->cb15_c18_before)o->cb15_cleanup_mask|=128;if(o->cb15_c25_restored!=o->cb15_c25_before)o->cb15_cleanup_mask|=256;}
 if(o->cb7_attempted){cw(7,o->cb7_before);o->cb7_restored=cr(7);o->cb7_c6_restored=cr(0x6);o->cb7_c9_restored=cr(0x9);o->cb7_c10_restored=cr(0x10);o->cb7_c12_restored=cr(0x12);o->cb7_c15_restored=cr(0x15);o->cb7_c16_restored=cr(0x16);o->cb7_c18_restored=cr(0x18);o->cb7_c25_restored=cr(0x25);if(o->cb7_restored!=o->cb7_before)o->cb7_cleanup_mask|=1;if(o->cb7_c6_restored!=o->cb7_c6_before)o->cb7_cleanup_mask|=2;if(o->cb7_c9_restored!=o->cb7_c9_before)o->cb7_cleanup_mask|=4;if(o->cb7_c10_restored!=o->cb7_c10_before)o->cb7_cleanup_mask|=8;if(o->cb7_c12_restored!=o->cb7_c12_before)o->cb7_cleanup_mask|=16;if(o->cb7_c15_restored!=o->cb7_c15_before)o->cb7_cleanup_mask|=32;if(o->cb7_c16_restored!=o->cb7_c16_before)o->cb7_cleanup_mask|=64;if(o->cb7_c18_restored!=o->cb7_c18_before)o->cb7_cleanup_mask|=128;if(o->cb7_c25_restored!=o->cb7_c25_before)o->cb7_cleanup_mask|=256;}
 if(o->cb9_attempted){cw(9,o->cb9_before);o->cb9_restored=cr(9);o->cb9_c6_restored=cr(0x6);o->cb9_c7_restored=cr(0x7);o->cb9_c10_restored=cr(0x10);o->cb9_c12_restored=cr(0x12);o->cb9_c15_restored=cr(0x15);o->cb9_c16_restored=cr(0x16);o->cb9_c18_restored=cr(0x18);o->cb9_c25_restored=cr(0x25);if(o->cb9_restored!=o->cb9_before)o->cb9_cleanup_mask|=1;if(o->cb9_c6_restored!=o->cb9_c6_before)o->cb9_cleanup_mask|=2;if(o->cb9_c7_restored!=o->cb9_c7_before)o->cb9_cleanup_mask|=4;if(o->cb9_c10_restored!=o->cb9_c10_before)o->cb9_cleanup_mask|=8;if(o->cb9_c12_restored!=o->cb9_c12_before)o->cb9_cleanup_mask|=16;if(o->cb9_c15_restored!=o->cb9_c15_before)o->cb9_cleanup_mask|=32;if(o->cb9_c16_restored!=o->cb9_c16_before)o->cb9_cleanup_mask|=64;if(o->cb9_c18_restored!=o->cb9_c18_before)o->cb9_cleanup_mask|=128;if(o->cb9_c25_restored!=o->cb9_c25_before)o->cb9_cleanup_mask|=256;}
 if(o->cd12_attempted){cw(0x12,o->cd12_before);o->cd12_restored=cr(0x12);o->cd12_c6_restored=cr(0x6);o->cd12_c7_restored=cr(0x7);o->cd12_c9_restored=cr(0x9);o->cd12_c10_restored=cr(0x10);o->cd12_c15_restored=cr(0x15);o->cd12_c16_restored=cr(0x16);o->cd12_c18_restored=cr(0x18);o->cd12_c25_restored=cr(0x25);if(o->cd12_restored!=o->cd12_before)o->cd12_cleanup_mask|=1;if(o->cd12_c6_restored!=o->cd12_c6_before)o->cd12_cleanup_mask|=2;if(o->cd12_c7_restored!=o->cd12_c7_before)o->cd12_cleanup_mask|=4;if(o->cd12_c9_restored!=o->cd12_c9_before)o->cd12_cleanup_mask|=8;if(o->cd12_c10_restored!=o->cd12_c10_before)o->cd12_cleanup_mask|=16;if(o->cd12_c15_restored!=o->cd12_c15_before)o->cd12_cleanup_mask|=32;if(o->cd12_c16_restored!=o->cd12_c16_before)o->cd12_cleanup_mask|=64;if(o->cd12_c18_restored!=o->cd12_c18_before)o->cd12_cleanup_mask|=128;if(o->cd12_c25_restored!=o->cd12_c25_before)o->cd12_cleanup_mask|=256;}
 if(o->cd7_attempted){cw(7,o->cd7_before);o->cd7_restored=cr(7);o->cd7_c6_restored=cr(0x6);o->cd7_c9_restored=cr(0x9);o->cd7_c10_restored=cr(0x10);o->cd7_c12_restored=cr(0x12);o->cd7_c15_restored=cr(0x15);o->cd7_c16_restored=cr(0x16);o->cd7_c18_restored=cr(0x18);o->cd7_c25_restored=cr(0x25);if(o->cd7_restored!=o->cd7_before)o->cd7_cleanup_mask|=1;if(o->cd7_c6_restored!=o->cd7_c6_before)o->cd7_cleanup_mask|=2;if(o->cd7_c9_restored!=o->cd7_c9_before)o->cd7_cleanup_mask|=4;if(o->cd7_c10_restored!=o->cd7_c10_before)o->cd7_cleanup_mask|=8;if(o->cd7_c12_restored!=o->cd7_c12_before)o->cd7_cleanup_mask|=16;if(o->cd7_c15_restored!=o->cd7_c15_before)o->cd7_cleanup_mask|=32;if(o->cd7_c16_restored!=o->cd7_c16_before)o->cd7_cleanup_mask|=64;if(o->cd7_c18_restored!=o->cd7_c18_before)o->cd7_cleanup_mask|=128;if(o->cd7_c25_restored!=o->cd7_c25_before)o->cd7_cleanup_mask|=256;}
 if(o->ct16_attempted){cw(0x16,o->ct16_before);o->ct16_restored=cr(0x16);o->ct16_c6_restored=cr(0x6);o->ct16_c7_restored=cr(0x7);o->ct16_c9_restored=cr(0x9);o->ct16_c10_restored=cr(0x10);o->ct16_c12_restored=cr(0x12);o->ct16_c15_restored=cr(0x15);o->ct16_c18_restored=cr(0x18);o->ct16_c25_restored=cr(0x25);if(o->ct16_restored!=o->ct16_before)o->ct16_cleanup_mask|=1;if(o->ct16_c6_restored!=o->ct16_c6_before)o->ct16_cleanup_mask|=2;if(o->ct16_c7_restored!=o->ct16_c7_before)o->ct16_cleanup_mask|=4;if(o->ct16_c9_restored!=o->ct16_c9_before)o->ct16_cleanup_mask|=8;if(o->ct16_c10_restored!=o->ct16_c10_before)o->ct16_cleanup_mask|=16;if(o->ct16_c12_restored!=o->ct16_c12_before)o->ct16_cleanup_mask|=32;if(o->ct16_c15_restored!=o->ct16_c15_before)o->ct16_cleanup_mask|=64;if(o->ct16_c18_restored!=o->ct16_c18_before)o->ct16_cleanup_mask|=128;if(o->ct16_c25_restored!=o->ct16_c25_before)o->ct16_cleanup_mask|=256;}
 if(o->ct6_attempted){cw(6,o->ct6_before);o->ct6_restored=cr(6);o->ct6_c7_restored=cr(0x7);o->ct6_c9_restored=cr(0x9);o->ct6_c10_restored=cr(0x10);o->ct6_c12_restored=cr(0x12);o->ct6_c15_restored=cr(0x15);o->ct6_c16_restored=cr(0x16);o->ct6_c18_restored=cr(0x18);o->ct6_c25_restored=cr(0x25);if(o->ct6_restored!=o->ct6_before)o->ct6_cleanup_mask|=1;if(o->ct6_c7_restored!=o->ct6_c7_before)o->ct6_cleanup_mask|=2;if(o->ct6_c9_restored!=o->ct6_c9_before)o->ct6_cleanup_mask|=4;if(o->ct6_c10_restored!=o->ct6_c10_before)o->ct6_cleanup_mask|=8;if(o->ct6_c12_restored!=o->ct6_c12_before)o->ct6_cleanup_mask|=16;if(o->ct6_c15_restored!=o->ct6_c15_before)o->ct6_cleanup_mask|=32;if(o->ct6_c16_restored!=o->ct6_c16_before)o->ct6_cleanup_mask|=64;if(o->ct6_c18_restored!=o->ct6_c18_before)o->ct6_cleanup_mask|=128;if(o->ct6_c25_restored!=o->ct6_c25_before)o->ct6_cleanup_mask|=256;}
 if(o->ct7_attempted){cw(7,o->ct7_before);o->ct7_restored=cr(7);o->ct7_c6_restored=cr(0x6);o->ct7_c9_restored=cr(0x9);o->ct7_c10_restored=cr(0x10);o->ct7_c12_restored=cr(0x12);o->ct7_c15_restored=cr(0x15);o->ct7_c16_restored=cr(0x16);o->ct7_c18_restored=cr(0x18);o->ct7_c25_restored=cr(0x25);if(o->ct7_restored!=o->ct7_before)o->ct7_cleanup_mask|=1;if(o->ct7_c6_restored!=o->ct7_c6_before)o->ct7_cleanup_mask|=2;if(o->ct7_c9_restored!=o->ct7_c9_before)o->ct7_cleanup_mask|=4;if(o->ct7_c10_restored!=o->ct7_c10_before)o->ct7_cleanup_mask|=8;if(o->ct7_c12_restored!=o->ct7_c12_before)o->ct7_cleanup_mask|=16;if(o->ct7_c15_restored!=o->ct7_c15_before)o->ct7_cleanup_mask|=32;if(o->ct7_c16_restored!=o->ct7_c16_before)o->ct7_cleanup_mask|=64;if(o->ct7_c18_restored!=o->ct7_c18_before)o->ct7_cleanup_mask|=128;if(o->ct7_c25_restored!=o->ct7_c25_before)o->ct7_cleanup_mask|=256;}
 if(o->c10_attempted){cw(0x10,o->c10_before);o->c10_restored=cr(0x10);o->c10_c6_restored=cr(0x6);o->c10_c7_restored=cr(0x7);o->c10_c9_restored=cr(0x9);o->c10_c12_restored=cr(0x12);o->c10_c15_restored=cr(0x15);o->c10_c16_restored=cr(0x16);o->c10_c18_restored=cr(0x18);o->c10_c25_restored=cr(0x25);if(o->c10_restored!=o->c10_before)o->c10_cleanup_mask|=1;if(o->c10_c6_restored!=o->c10_c6_before)o->c10_cleanup_mask|=2;if(o->c10_c7_restored!=o->c10_c7_before)o->c10_cleanup_mask|=4;if(o->c10_c9_restored!=o->c10_c9_before)o->c10_cleanup_mask|=8;if(o->c10_c12_restored!=o->c10_c12_before)o->c10_cleanup_mask|=16;if(o->c10_c15_restored!=o->c10_c15_before)o->c10_cleanup_mask|=32;if(o->c10_c16_restored!=o->c10_c16_before)o->c10_cleanup_mask|=64;if(o->c10_c18_restored!=o->c10_c18_before)o->c10_cleanup_mask|=128;if(o->c10_c25_restored!=o->c10_c25_before)o->c10_cleanup_mask|=256;}
 if(o->c7_attempted){cw(7,o->c7_before);o->c7_restored=cr(7);o->c7_c6_restored=cr(0x6);o->c7_c9_restored=cr(0x9);o->c7_c10_restored=cr(0x10);o->c7_c12_restored=cr(0x12);o->c7_c15_restored=cr(0x15);o->c7_c16_restored=cr(0x16);o->c7_c18_restored=cr(0x18);o->c7_c25_restored=cr(0x25);if(o->c7_restored!=o->c7_before)o->c7_cleanup_mask|=1;if(o->c7_c6_restored!=o->c7_c6_before)o->c7_cleanup_mask|=2;if(o->c7_c9_restored!=o->c7_c9_before)o->c7_cleanup_mask|=4;if(o->c7_c10_restored!=o->c7_c10_before)o->c7_cleanup_mask|=8;if(o->c7_c12_restored!=o->c7_c12_before)o->c7_cleanup_mask|=16;if(o->c7_c15_restored!=o->c7_c15_before)o->c7_cleanup_mask|=32;if(o->c7_c16_restored!=o->c7_c16_before)o->c7_cleanup_mask|=64;if(o->c7_c18_restored!=o->c7_c18_before)o->c7_cleanup_mask|=128;if(o->c7_c25_restored!=o->c7_c25_before)o->c7_cleanup_mask|=256;}
 if(o->ve_attempted){R32(0x680818)=o->ve_before;o->ve_restored=R32(0x680818);o->ve_disp_restored=R32(0x680800);o->ve_total_restored=R32(0x680804);o->ve_crtc_restored=R32(0x680808);o->ve_validstart_restored=R32(0x680814);o->ve_syncstart_restored=R32(0x68080c);o->ve_syncend_restored=R32(0x680810);o->ve_c13_restored=cr(0x13);o->ve_c19_restored=cr(0x19);if(o->ve_restored!=o->ve_before)o->ve_cleanup_mask|=1;if(o->ve_disp_restored!=o->ve_disp_before)o->ve_cleanup_mask|=2;if(o->ve_total_restored!=o->ve_total_before)o->ve_cleanup_mask|=4;if(o->ve_crtc_restored!=o->ve_crtc_before)o->ve_cleanup_mask|=8;if(o->ve_validstart_restored!=o->ve_validstart_before)o->ve_cleanup_mask|=16;if(o->ve_syncstart_restored!=o->ve_syncstart_before)o->ve_cleanup_mask|=32;if(o->ve_syncend_restored!=o->ve_syncend_before)o->ve_cleanup_mask|=64;if(o->ve_c13_restored!=o->ve_c13_before)o->ve_cleanup_mask|=128;if(o->ve_c19_restored!=o->ve_c19_before)o->ve_cleanup_mask|=256;}
 if(o->se_attempted){R32(0x680810)=o->se_before;o->se_restored=R32(0x680810);o->se_disp_restored=R32(0x680800);o->se_total_restored=R32(0x680804);o->se_crtc_restored=R32(0x680808);o->se_validstart_restored=R32(0x680814);o->se_syncstart_restored=R32(0x68080c);o->se_validend_restored=R32(0x680818);o->se_c13_restored=cr(0x13);o->se_c19_restored=cr(0x19);if(o->se_restored!=o->se_before)o->se_cleanup_mask|=1;if(o->se_disp_restored!=o->se_disp_before)o->se_cleanup_mask|=2;if(o->se_total_restored!=o->se_total_before)o->se_cleanup_mask|=4;if(o->se_crtc_restored!=o->se_crtc_before)o->se_cleanup_mask|=8;if(o->se_validstart_restored!=o->se_validstart_before)o->se_cleanup_mask|=16;if(o->se_syncstart_restored!=o->se_syncstart_before)o->se_cleanup_mask|=32;if(o->se_validend_restored!=o->se_validend_before)o->se_cleanup_mask|=64;if(o->se_c13_restored!=o->se_c13_before)o->se_cleanup_mask|=128;if(o->se_c19_restored!=o->se_c19_before)o->se_cleanup_mask|=256;}
 if(o->sy_attempted){R32(0x68080c)=o->sy_before;o->sy_restored=R32(0x68080c);o->sy_disp_restored=R32(0x680800);o->sy_total_restored=R32(0x680804);o->sy_crtc_restored=R32(0x680808);o->sy_validstart_restored=R32(0x680814);o->sy_syncend_restored=R32(0x680810);o->sy_validend_restored=R32(0x680818);o->sy_c13_restored=cr(0x13);o->sy_c19_restored=cr(0x19);if(o->sy_restored!=o->sy_before)o->sy_cleanup_mask|=1;if(o->sy_disp_restored!=o->sy_disp_before)o->sy_cleanup_mask|=2;if(o->sy_total_restored!=o->sy_total_before)o->sy_cleanup_mask|=4;if(o->sy_crtc_restored!=o->sy_crtc_before)o->sy_cleanup_mask|=8;if(o->sy_validstart_restored!=o->sy_validstart_before)o->sy_cleanup_mask|=16;if(o->sy_syncend_restored!=o->sy_syncend_before)o->sy_cleanup_mask|=32;if(o->sy_validend_restored!=o->sy_validend_before)o->sy_cleanup_mask|=64;if(o->sy_c13_restored!=o->sy_c13_before)o->sy_cleanup_mask|=128;if(o->sy_c19_restored!=o->sy_c19_before)o->sy_cleanup_mask|=256;}
 if(o->vs_attempted){R32(0x680814)=o->vs_before;o->vs_restored=R32(0x680814);o->vs_disp_restored=R32(0x680800);o->vs_total_restored=R32(0x680804);o->vs_crtc_restored=R32(0x680808);o->vs_syncstart_restored=R32(0x68080c);o->vs_syncend_restored=R32(0x680810);o->vs_validend_restored=R32(0x680818);o->vs_c13_restored=cr(0x13);o->vs_c19_restored=cr(0x19);if(o->vs_restored!=o->vs_before)o->vs_cleanup_mask|=1;if(o->vs_disp_restored!=o->vs_disp_before)o->vs_cleanup_mask|=2;if(o->vs_total_restored!=o->vs_total_before)o->vs_cleanup_mask|=4;if(o->vs_crtc_restored!=o->vs_crtc_before)o->vs_cleanup_mask|=8;if(o->vs_syncstart_restored!=o->vs_syncstart_before)o->vs_cleanup_mask|=16;if(o->vs_syncend_restored!=o->vs_syncend_before)o->vs_cleanup_mask|=32;if(o->vs_validend_restored!=o->vs_validend_before)o->vs_cleanup_mask|=64;if(o->vs_c13_restored!=o->vs_c13_before)o->vs_cleanup_mask|=128;if(o->vs_c19_restored!=o->vs_c19_before)o->vs_cleanup_mask|=256;}
 if(o->vc_attempted){R32(0x680808)=o->vc_before;o->vc_restored=R32(0x680808);o->vc_disp_restored=R32(0x680800);o->vc_total_restored=R32(0x680804);o->vc_syncstart_restored=R32(0x68080c);o->vc_syncend_restored=R32(0x680810);o->vc_validstart_restored=R32(0x680814);o->vc_validend_restored=R32(0x680818);o->vc_c13_restored=cr(0x13);o->vc_c19_restored=cr(0x19);if(o->vc_restored!=o->vc_before)o->vc_cleanup_mask|=1;if(o->vc_disp_restored!=o->vc_disp_before)o->vc_cleanup_mask|=2;if(o->vc_total_restored!=o->vc_total_before)o->vc_cleanup_mask|=4;if(o->vc_syncstart_restored!=o->vc_syncstart_before)o->vc_cleanup_mask|=8;if(o->vc_syncend_restored!=o->vc_syncend_before)o->vc_cleanup_mask|=16;if(o->vc_validstart_restored!=o->vc_validstart_before)o->vc_cleanup_mask|=32;if(o->vc_validend_restored!=o->vc_validend_before)o->vc_cleanup_mask|=64;if(o->vc_c13_restored!=o->vc_c13_before)o->vc_cleanup_mask|=128;if(o->vc_c19_restored!=o->vc_c19_before)o->vc_cleanup_mask|=256;}
 if(o->vt_attempted){R32(0x680804)=o->vt_before;o->vt_restored=R32(0x680804);o->vt_disp_restored=R32(0x680800);o->vt_syncstart_restored=R32(0x68080c);o->vt_syncend_restored=R32(0x680810);o->vt_validend_restored=R32(0x680818);o->vt_c13_restored=cr(0x13);o->vt_c19_restored=cr(0x19);if(o->vt_restored!=o->vt_before)o->vt_cleanup_mask|=1;if(o->vt_disp_restored!=o->vt_disp_before)o->vt_cleanup_mask|=2;if(o->vt_syncstart_restored!=o->vt_syncstart_before)o->vt_cleanup_mask|=4;if(o->vt_syncend_restored!=o->vt_syncend_before)o->vt_cleanup_mask|=8;if(o->vt_validend_restored!=o->vt_validend_before)o->vt_cleanup_mask|=16;if(o->vt_c13_restored!=o->vt_c13_before)o->vt_cleanup_mask|=32;if(o->vt_c19_restored!=o->vt_c19_before)o->vt_cleanup_mask|=64;}
 if(o->v_attempted){R32(0x680800)=o->v_before;o->v_restored=R32(0x680800);o->vtotal_restored=R32(0x680804);o->vsyncstart_restored=R32(0x68080c);o->vsyncend_restored=R32(0x680810);o->vvalidend_restored=R32(0x680818);o->c13_v_restored=cr(0x13);o->c19_v_restored=cr(0x19);if(o->v_restored!=o->v_before)o->v_cleanup_mask|=1;if(o->vtotal_restored!=o->vtotal_before)o->v_cleanup_mask|=2;if(o->vsyncstart_restored!=o->vsyncstart_before)o->v_cleanup_mask|=4;if(o->vsyncend_restored!=o->vsyncend_before)o->v_cleanup_mask|=8;if(o->vvalidend_restored!=o->vvalidend_before)o->v_cleanup_mask|=16;if(o->c13_v_restored!=o->c13_v_before)o->v_cleanup_mask|=32;if(o->c19_v_restored!=o->c19_v_before)o->v_cleanup_mask|=64;}
 if(o->c13_attempted){cw(0x13,(uint8_t)o->c13_before);o->c13_restored=cr(0x13);o->c19_restored_c13=cr(0x19);if(o->c13_restored!=o->c13_before)o->c13_cleanup_mask|=1;if(o->c19_restored_c13!=o->c19_before_c13)o->c13_cleanup_mask|=2;}
 if(o->c19b_attempted){cw(0x19,(uint8_t)o->c19b_before);o->c19b_restored=cr(0x19);o->c13_restored_c19b=cr(0x13);if(o->c19b_restored!=o->c19b_before)o->c19b_cleanup_mask|=1;if(o->c13_restored_c19b!=o->c13_before_c19b)o->c19b_cleanup_mask|=2;}
 if(o->c17b_attempted){cw(0x17,(uint8_t)o->c17b_before);o->c17b_restored=cr(0x17);if(o->c17b_restored!=o->c17b_before)o->c17b_cleanup_mask=1;}
 if(o->c2b_attempted){cw(2,(uint8_t)o->c2b_before);o->c2b_restored=cr(2);if(o->c2b_restored!=o->c2b_before)o->c2b_cleanup_mask=1;}
 if(o->c1_attempted){cw(1,(uint8_t)o->c1_before);o->c1_restored=cr(1);if(o->c1_restored!=o->c1_before)o->c1_cleanup_mask=1;}
 if(o->c17_attempted){cw(0x17,(uint8_t)o->c17_before);o->c17_restored=cr(0x17);if(o->c17_restored!=o->c17_before)o->c17_cleanup_mask=1;}
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
 if(!o->h_cleanup_mask && !o->c4_cleanup_mask && !o->c0_cleanup_mask && !o->c2_cleanup_mask && !o->c3_cleanup_mask && !o->c5b_cleanup_mask && !o->c17_cleanup_mask && !o->c1_cleanup_mask && !o->c2b_cleanup_mask && !o->c17b_cleanup_mask && !o->c19b_cleanup_mask && !o->c13_cleanup_mask && !o->v_cleanup_mask && !o->vt_cleanup_mask && !o->vc_cleanup_mask && !o->vs_cleanup_mask && !o->sy_cleanup_mask && !o->se_cleanup_mask && !o->ve_cleanup_mask && !o->c7_cleanup_mask && !o->c10_cleanup_mask && !o->ct7_cleanup_mask && !o->ct6_cleanup_mask && !o->ct16_cleanup_mask && !o->cd7_cleanup_mask && !o->cd12_cleanup_mask && !o->cb9_cleanup_mask && !o->cb7_cleanup_mask && !o->cb15_cleanup_mask && !o->cl7_cleanup_mask && !o->cl9_cleanup_mask){gate(4);sw((uint8_t)o->seq_before);o->output_restored=1;}
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
 if(o->forward_status!=0x8111 && o->forward_status!=0x8112 && !o->cleanup_ok)o->code=0x8115;
 if(o->h_cleanup_mask)o->code=0x811a;
 if(o->c4_cleanup_mask)o->code=0x811c;
 if(o->c0_cleanup_mask)o->code=0x811f;
 if(o->c2_cleanup_mask)o->code=0x81111;
 if(o->c3_cleanup_mask)o->code=0x81113;
 if(o->c5b_cleanup_mask)o->code=0x81115;
 if(o->c17_cleanup_mask)o->code=0x81117;
 if(o->c1_cleanup_mask)o->code=0x81119;
 if(o->c2b_cleanup_mask)o->code=0x8111b;
 if(o->c17b_cleanup_mask)o->code=0x8111d;
 if(o->c19b_cleanup_mask)o->code=0x8111f;
 if(o->c13_cleanup_mask)o->code=0x81121;
 if(o->v_cleanup_mask)o->code=0x81123;
 if(o->vt_cleanup_mask)o->code=0x81125;
 if(o->vc_cleanup_mask)o->code=0x81127;
 if(o->vs_cleanup_mask)o->code=0x81129;
 if(o->sy_cleanup_mask)o->code=0x8112b;
 if(o->se_cleanup_mask)o->code=0x8112d;
 if(o->ve_cleanup_mask)o->code=0x8112f;
 if(o->c7_cleanup_mask)o->code=0x81131;
 if(o->c10_cleanup_mask)o->code=0x81133;
 if(o->ct7_cleanup_mask)o->code=0x81135;
 if(o->ct6_cleanup_mask)o->code=0x81137;
 if(o->ct16_cleanup_mask)o->code=0x81139;
 if(o->cd7_cleanup_mask)o->code=0x8113b;
 if(o->cd12_cleanup_mask)o->code=0x8113d;
 if(o->cb9_cleanup_mask)o->code=0x8113f;
 if(o->cb7_cleanup_mask)o->code=0x81141;
 if(o->cb15_cleanup_mask)o->code=0x81143;
 if(o->cl7_cleanup_mask)o->code=0x81145;
 if(o->cl9_cleanup_mask)o->code=0x81147;
 if(o->forward_status!=0x8111 && !o->selectors_restored)o->code=0x8116;
 __asm__ volatile("pushl %1;popfl;pushfl;popl %0":"=&r"(restored):"r"(flags):"memory","cc");o->flags_restored=restored;
}
