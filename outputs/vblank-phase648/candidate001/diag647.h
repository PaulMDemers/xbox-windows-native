/* SPDX-License-Identifier: GPL-2.0-or-later
 * Diagnostic AFTER video setup returns. No video registers or retry policy.
 * LED signaling and eight-second delay perturb timing; not a functional fix.
 */
#ifndef XWN_DIAG647_H
#define XWN_DIAG647_H
static unsigned diag647_mask(int result,unsigned stage,unsigned error) {
 if(result==1 && stage==5 && error==0)return 0x05; /* green/off: setup returned success */
 if(result==0 && stage==0 && error==0)return 0x50; /* red/off: pre-write rejection */
 if(result==-1 && stage==255) {
  if(error>=11 && error<=13)return 0xf5; /* red/amber: SMBus failure */
  if(error==21)return 0xff;             /* amber: synchronization timeout */
  if(error==22)return 0xa5;             /* red/green: vblank timeout */
  if(error==23 || error==24)return 0x5f; /* green/amber: readback mismatch */
 }
 return 0x00; /* off: unexpected state; absence of indication is inconclusive */
}
#endif
