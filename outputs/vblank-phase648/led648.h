/* SPDX-License-Identifier: GPL-2.0-or-later
 * Runs only AFTER apply returns. Extra SMC traffic/delay perturb the run.
 */
#ifndef XWN_LED648_H
#define XWN_LED648_H
#include "diag647.h"
static unsigned phase648_mask(unsigned phase) {
 static const unsigned masks[6]={0x50,0x05,0x55,0xa5,0xf5,0x5f};
 return phase>=1 && phase<=6 ? masks[phase-1] : 0;
}
static unsigned led648_show(void *context,
 int (*send)(void *,unsigned char,unsigned char,unsigned char),
 void (*delay)(void *,unsigned),int result,unsigned stage,unsigned error,unsigned phase) {
 unsigned i,mask=diag647_mask(result,stage,error);
 if(send(context,0x10,0x08,(unsigned char)mask))return 1;
 if(send(context,0x10,0x07,1))return 2;
 for(i=0;i<8;i++)delay(context,1000000u);
 if(result==-1 && stage==255 && error==22) {
  if(send(context,0x10,0x08,0))return 3;
  for(i=0;i<2;i++)delay(context,1000000u);
  if(send(context,0x10,0x08,(unsigned char)phase648_mask(phase)))return 4;
  for(i=0;i<8;i++)delay(context,1000000u);
 }
 if(send(context,0x10,0x07,0))return 5;
 return 0;
}
#endif
