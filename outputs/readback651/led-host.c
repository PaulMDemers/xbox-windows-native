/* SPDX-License-Identifier: GPL-2.0-or-later */
#include "led651.h"
#include <assert.h>
#include <stdio.h>
struct model {unsigned fail,calls,delays,reg[10],value[10];};
static int send(void*v,unsigned char a,unsigned char r,unsigned char x) {
 struct model*m=v;assert(a==0x10 && m->calls<9);
 m->reg[m->calls]=r;m->value[m->calls++]=x;return m->calls==m->fail;
}
static void delay(void*v,unsigned us){struct model*m=v;assert(us==1000000 && m->delays<38);m->delays++;}
static struct xwn_trace649 trace(unsigned phase,unsigned byte,unsigned varied) {
 struct xwn_trace649 t={0};struct xwn_edge649*e=&t.edge[phase-1];
 t.waits_started=t.failed_wait=phase;t.waits_completed=phase-1;
 e->wanted=((phase-1)%2)*8;e->first=e->last=byte;e->samples=100000;e->byte_changes=varied;
 return t;
}
int main(void) {
 unsigned p,byte,variation,match,h,fail,i,cases=0;
 const unsigned phases[6]={80,5,85,165,245,95},matches[5]={5,80,85,245,165};
 const unsigned hs[3]={0,1,0xffffffffu},hm[3]={5,80,165};
 const unsigned ds[10]={38,0,0,8,10,18,20,28,30,38};
 for(p=1;p<=6;p++)for(byte=0;byte<256;byte++) {
  struct xwn_trace649 t=trace(p,byte,0);
  assert(status651(&t)==(((byte&8)==t.edge[p-1].wanted)?165:byte==255?80:5));cases++;
 }
 for(p=1;p<=6;p++)for(variation=0;variation<4;variation++)for(match=0;match<5;match++)for(h=0;h<3;h++)for(fail=0;fail<=9;fail++) {
  unsigned wanted=((p-1)%2)*8,byte=(wanted^8)|0xa0,status,ret;
  struct xwn_trace649 t=trace(p,byte,0);struct model m={0};
  const unsigned regs[9]={8,7,8,8,8,8,8,8,7};unsigned vals[9];
  if(variation==1)t.edge[p-1].byte_changes=99;
  if(variation==2)t.edge[p-1].samples=0;
  if(variation==3)t.edge[p-1].first=t.edge[p-1].last=255;
  status=variation==0?5:variation==1?85:variation==2?165:wanted==0?80:165;
  vals[0]=phases[p-1];vals[1]=1;vals[2]=0;vals[3]=matches[match];vals[4]=0;vals[5]=status;vals[6]=0;vals[7]=hm[h];vals[8]=0;
  m.fail=fail;ret=led651_show(&m,send,delay,-1,255,22,&t,match,1,hs[h]);
  assert(ret==fail && m.calls==(fail?fail:9) && m.delays==ds[fail]);
  for(i=0;i<m.calls;i++){assert(m.reg[i]==regs[i] && m.value[i]==vals[i]);}cases++;
 }
 for(fail=0;fail<=3;fail++) {
  struct model m={0};struct xwn_trace649 t={0};m.fail=fail;
  assert(led651_show(&m,send,delay,1,5,0,&t,4,0,0)==fail);
  assert(m.calls==(fail?fail:3) && m.value[0]==5 && m.delays==(fail==1||fail==2?0:8));cases++;
 }
 assert(handshake651(0,0)==165 && handshake651(1,0x10)==80 && handshake651(1,0x11)==5);cases+=3;
 printf("PASS %u LED/classification cases; all bytes, four slots and every failed write\n",cases);return 0;
}
