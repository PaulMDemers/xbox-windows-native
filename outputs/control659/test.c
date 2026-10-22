/* SPDX-License-Identifier: GPL-2.0-or-later */
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "control.h"
struct mock {unsigned mode,transactions,reads,n,fail_transaction,ports[10][3];};
static unsigned input(void *p,unsigned port,unsigned size){
 struct mock *m=p;assert(port==0xc000);m->reads++;
 if(size==2)return m->mode==1?0x800:0;
 assert(size==1);return m->mode==2?0:m->mode==3||m->fail_transaction==m->transactions?0x26:0x10;
}
static void output(void *p,unsigned port,unsigned size,unsigned value){
 struct mock *m=p;assert(m->n<10);m->ports[m->n][0]=port;m->ports[m->n][1]=size;m->ports[m->n++][2]=value;
 if(port==0xc002)m->transactions++;
}
int main(void){
 unsigned mode,mask,cases=0;
 for(mask=0;mask<256;mask++){
  struct mock m={0};struct latch659 r={0};const struct smc658 io={&m,input,output,0};
  assert(latch659(&io,mask,&r)==0);assert(m.n==10&&r.reads==6&&r.writes==10&&r.transactions==2);
  assert(m.ports[1][2]==8&&m.ports[2][2]==mask&&m.ports[6][2]==7&&m.ports[7][2]==1);cases++;
 }
 for(mode=1;mode<=3;mode++){
  struct mock m={0};struct latch659 r={0};const struct smc658 io={&m,input,output,0};m.mode=mode;
  assert(latch659(&io,15,&r)==(mode==1?2:mode==2?4:3));assert(r.reads<=POLLS659+2&&r.transactions==1);cases++;
 }
 for(mode=1;mode<=2;mode++){
  struct mock m={0};struct latch659 r={0};const struct smc658 io={&m,input,output,0};m.fail_transaction=mode;
  assert(latch659(&io,15,&r)==3);assert(r.transactions==mode&&r.writes==mode*5);cases++;
 }
 {unsigned expected[]={15,80,165,245,95,240};for(mode=0;mode<6;mode++){assert(mask659(0,0,mode)==expected[mode]);cases++;}}
 assert(mask659(1,0,0)==240&&mask659(0,2,0)==85&&mask659(0,2,1)==80);cases++;
 {struct mock m={0};struct latch659 r={0};const struct smc658 io={&m,input,output,0};
 assert(latch659(0,0,&r)==1&&latch659(&io,256,&r)==1&&latch659(&io,0,0)==1&&m.n==0);cases++;}
 printf("{\"status\":\"pass\",\"cases\":%u}\n",cases);return 0;
}
