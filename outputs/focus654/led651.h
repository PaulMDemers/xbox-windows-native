/* SPDX-License-Identifier: GPL-2.0-or-later
 * 654: one post-result timing-comparison indication; not boot success.
 * Retain the651 ABI so native capture/apply/reset source stays byte-identical.
 * Delay uses the existing timer: a frozen hardware timer can still hang.
 */
#ifndef XWN_LED651_H
#define XWN_LED651_H
#include "trace649.h"
static unsigned focused654(int result,unsigned stage,unsigned error,unsigned match,unsigned captured) {
 static const unsigned masks[5]={5,80,85,245,165};
 if(!captured || match>3 || !((result==1 && stage==5 && error==0) ||
    (result==-1 && stage==255 && error==22)))return masks[4];
 return masks[match];
}
static unsigned led651_show(void *context,
 int (*send)(void *,unsigned char,unsigned char,unsigned char),
 void (*delay)(void *,unsigned),int result,unsigned stage,unsigned error,
 const volatile struct xwn_trace649 *trace,unsigned match,unsigned captured,unsigned handshake) {
 unsigned j,mask=focused654(result,stage,error,match,captured);
 (void)trace;(void)handshake;
 if(send(context,0x10,8,0))return 1;
 if(send(context,0x10,7,1))return 2;
 for(j=0;j<2;j++)delay(context,1000000u);
 if(send(context,0x10,8,(unsigned char)mask))return 3;
 for(j=0;j<20;j++)delay(context,1000000u);
 if(send(context,0x10,7,0))return 4;
 return 0;
}
#endif
