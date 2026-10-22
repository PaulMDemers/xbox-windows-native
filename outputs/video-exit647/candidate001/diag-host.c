/* SPDX-License-Identifier: GPL-2.0-or-later */
#include <assert.h>
#include <stdio.h>
#include "diag647.h"
struct model {unsigned calls,delays,fail,mask;};
static int send(void *p,unsigned char a,unsigned char r,unsigned char v) {
 struct model *m=p; m->calls++;
 assert(a==0x10 && m->calls<=3);
 if(m->calls==1)assert(r==8 && v==m->mask);
 if(m->calls==2)assert(r==7 && v==1);
 if(m->calls==3)assert(r==7 && v==0);
 return m->calls==m->fail;
}
static void delay(void *p,unsigned us) {
 struct model *m=p;assert(m->calls==2 && us==1000000);m->delays++;assert(m->delays<=8);
}
int main(void) {
 const int rows[][4]={{1,5,0,15},{0,0,0,240},{-1,255,11,245},
 {-1,255,12,245},{-1,255,13,245},{-1,255,21,255},{-1,255,22,165},
 {-1,255,23,95},{-1,255,24,95},{1,4,0,170},{0,1,0,170},
 {-1,255,0,170},{-1,4,22,170},{2,5,0,170}};
 unsigned i,f,checks=0;
 for(i=0;i<sizeof(rows)/sizeof(rows[0]);i++) {
  assert(diag647_mask(rows[i][0],rows[i][1],rows[i][2])==(unsigned)rows[i][3]);checks++;
  for(f=0;f<=3;f++) {
   struct model m={0,0,f,(unsigned)rows[i][3]};
   unsigned result=diag647_show(&m,send,delay,rows[i][0],rows[i][1],rows[i][2]);
   assert(result==f);assert(m.calls==(f?f:3));
   assert(m.delays==((f==1 || f==2)?0:8));checks++;
  }
 }
 puts("PASS diagnostic result mapping and bounded LED transactions");
 printf("checks %u\n",checks);return 0;
}
