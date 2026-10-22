/* SPDX-License-Identifier: GPL-2.0-or-later */
#include "led649.h"
#include <assert.h>
#include <stdio.h>
struct model {unsigned fail,calls,delays,reg[8],value[8];};
static int send(void*v,unsigned char a,unsigned char r,unsigned char x) {
 struct model*m=v;assert(a==0x10 && m->calls<7);
 m->reg[m->calls]=r;m->value[m->calls++]=x;return m->calls==m->fail;
}
static void delay(void*v,unsigned us){struct model*m=v;assert(us==1000000 && m->delays<28);m->delays++;}
int main(void) {
 const unsigned phase_masks[8]={0,80,5,85,165,245,95,0};
 const unsigned ticks[8]={0,99999,100000,2999999,3000000,36000000,36000001,0xffffffffu};
 const unsigned duration_masks[8]={80,80,85,85,5,5,165,165};
 const unsigned delays[8]={28,0,0,8,10,18,20,28};
 unsigned phase,j,fail,cases=0;
 for(phase=0;phase<=7;phase++)for(j=0;j<8;j++)for(fail=0;fail<=7;fail++) {
  struct model m={0};unsigned ret,i;const unsigned regs[7]={8,7,8,8,8,8,7};
  const unsigned vals[7]={165,1,0,phase_masks[phase],0,phase>=1 && phase<=6?duration_masks[j]:0,0};m.fail=fail;
  ret=led649_show(&m,send,delay,-1,255,22,phase,ticks[j]);
  assert(ret==fail && m.calls==(fail?fail:7));
  for(i=0;i<m.calls;i++)assert(m.reg[i]==regs[i] && m.value[i]==vals[i]);
  assert(m.delays==delays[fail]);cases++;
 }
 for(fail=0;fail<=3;fail++) {
  struct model m={0};unsigned ret;m.fail=fail;
  ret=led649_show(&m,send,delay,1,5,0,0,0);
  assert(ret==(fail==3?7:fail) && m.calls==(fail?fail:3));
  assert(m.value[0]==5 && m.delays==(fail==1||fail==2?0:8));cases++;
 }
 printf("PASS %u LED cases including duration boundaries and every failed write\n",cases);return 0;
}
