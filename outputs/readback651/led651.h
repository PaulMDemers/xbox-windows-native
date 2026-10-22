/* SPDX-License-Identifier: GPL-2.0-or-later */
#ifndef XWN_LED651_H
#define XWN_LED651_H
#include "diag647.h"
#include "trace649.h"
static unsigned phase651(unsigned phase){static const unsigned m[6]={80,5,85,165,245,95};return phase>=1&&phase<=6?m[phase-1]:0;}
/* Unknown is red/green, never green. Existing failed-wait samples only. */
static unsigned status651(const volatile struct xwn_trace649 *t) {
 const volatile struct xwn_edge649 *e;unsigned p=t->failed_wait;
 if(p<1 || p>6 || t->waits_started!=p || t->waits_completed!=p-1)return 165;
 e=&t->edge[p-1];
 if(e->completed || e->samples!=100000 || e->wanted!=((p-1)%2)*8 ||
    e->first>255 || e->last>255 || (e->first&8)==e->wanted || (e->last&8)==e->wanted ||
    e->bit_changes || e->byte_changes>=e->samples ||
    (!e->byte_changes && e->first!=e->last))return 165;
 if(e->byte_changes)return 85; /* varied sampled byte; bit3 never matched */
 return e->first==255?80:5; /* constant all-ones vs another constant */
}
static unsigned match651_mask(unsigned v){static const unsigned m[5]={5,80,85,245,165};return v<5?m[v]:165;}
static unsigned handshake651(unsigned captured,unsigned value) {
 if(!captured || value==0xffffffffu)return 165;
 return ((value^(value>>4))&1)?80:5;
}
static unsigned led651_show(void *context,
 int (*send)(void *,unsigned char,unsigned char,unsigned char),
 void (*delay)(void *,unsigned),int result,unsigned stage,unsigned error,
 const volatile struct xwn_trace649 *trace,unsigned match,unsigned captured,unsigned handshake) {
 unsigned i,j,n=1,m[4],call=0;
 m[0]=diag647_mask(result,stage,error);
 if(result==-1 && stage==255 && error==22) {
  n=4;m[0]=phase651(trace->failed_wait);m[1]=match651_mask(match);
  m[2]=status651(trace);m[3]=handshake651(captured,handshake);
 }
 if(send(context,0x10,8,(unsigned char)m[0]))return ++call;
 call++;if(send(context,0x10,7,1))return ++call;call++;
 for(i=0;i<n;i++) {
  if(i) {
   call++;if(send(context,0x10,8,0))return call;
   for(j=0;j<2;j++)delay(context,1000000u);
   call++;if(send(context,0x10,8,(unsigned char)m[i]))return call;
  }
  for(j=0;j<8;j++)delay(context,1000000u);
 }
 call++;if(send(context,0x10,7,0))return call;
 return 0;
}
#endif
