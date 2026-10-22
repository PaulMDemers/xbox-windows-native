/* SPDX-License-Identifier: GPL-2.0-or-later */
#include "led648.h"
#include <assert.h>
#include <stdio.h>
struct model {unsigned fail,calls,delays,reg[6],value[6];};
static int send(void*v,unsigned char a,unsigned char r,unsigned char x) {
 struct model*m=v;assert(a==0x10 && m->calls<5);
 m->reg[m->calls]=r;m->value[m->calls++]=x;return m->calls==m->fail;
}
static void delay(void*v,unsigned us){struct model*m=v;assert(us==1000000 && m->delays<18);m->delays++;}
int main(void) {
 unsigned phase,fail,cases=0;const unsigned masks[8]={0,80,5,85,165,245,95,0};
 for(phase=0;phase<=7;phase++)for(fail=0;fail<=5;fail++) {
  struct model m={0};unsigned ret,i;const unsigned regs[5]={8,7,8,8,7};
  const unsigned vals[5]={165,1,0,masks[phase],0};m.fail=fail;
  ret=led648_show(&m,send,delay,-1,255,22,phase);
  assert(ret==fail && m.calls==(fail?fail:5));
  for(i=0;i<m.calls;i++)assert(m.reg[i]==regs[i] && m.value[i]==vals[i]);
  assert(m.delays==(fail==1||fail==2?0:fail==3?8:fail==4?10:18));cases++;
 }
 for(fail=0;fail<=3;fail++) {
  struct model m={0};unsigned ret;m.fail=fail;
  ret=led648_show(&m,send,delay,1,5,0,0);
  assert(ret==(fail==3?5:fail) && m.calls==(fail?fail:3));
  assert(m.value[0]==5 && m.delays==(fail==1||fail==2?0:8));cases++;
 }
 printf("PASS %u LED cases, all phase codes and diagnostic-write failures\n",cases);return 0;
}
