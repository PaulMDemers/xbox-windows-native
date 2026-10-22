/* SPDX-License-Identifier: GPL-2.0-or-later. No physical I/O. */
#include <assert.h>
#include <stdio.h>
#include "led651.h"
struct model {unsigned calls,delays,fail,mask;};
static int send(void *p,unsigned char a,unsigned char reg,unsigned char v) {
 struct model *m=p;unsigned n=++m->calls;
 assert(a==16 && n<=4);
 assert(reg==((n==1 || n==3)?8:7));
 assert(v==(n==1?0:n==2?1:n==3?m->mask:0));
 return n==m->fail;
}
static void delay(void *p,unsigned us) {
 struct model *m=p;assert(us==1000000u);
 assert((m->calls==2 && m->delays<2) || (m->calls==3 && m->delays<22));
 m->delays++;
}
int main(void) {
 static const unsigned stages[]={0,4,5,255},errors[]={0,11,13,21,22,23,24,30};
 static const unsigned masks[]={5,80,85,245};
 unsigned s,e,c,m,f,checks=0;int result;
 for(result=-2;result<=2;result++)for(s=0;s<4;s++)for(e=0;e<8;e++)
 for(c=0;c<2;c++)for(m=0;m<6;m++)for(f=0;f<=4;f++) {
  unsigned wanted=165,valid=c && m<4 &&
   ((result==1 && stages[s]==5 && errors[e]==0) || (result==-1 && stages[s]==255 && errors[e]==22));
  struct model model={0,0,f,0};
  if(valid)wanted=masks[m];
  model.mask=wanted;
  assert(focused654(result,stages[s],errors[e],m,c)==wanted);
  assert(led651_show(&model,send,delay,result,stages[s],errors[e],0,m,c,0xffffffffu)==f);
  assert(model.calls==(f?f:4));
  assert(model.delays==(f==1 || f==2?0:f==3?2:22));checks++;
 }
 printf("{\"passed\":true,\"cases\":%u,\"physical_access\":false}\n",checks);
 return 0;
}
