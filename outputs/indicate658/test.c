/* SPDX-License-Identifier: GPL-2.0-or-later */
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "indication.h"
static unsigned checks;
#define CHECK(x) do{assert(x);checks++;}while(0)
struct fixture {unsigned mode,fail_delay,delays,in16,in8,nout,reg,transactions,fail_transaction,values[32][3];};
static unsigned in(void *p,unsigned port,unsigned size){
 struct fixture *f=p;CHECK(port==0xc000);
 if(size==2){f->in16++;return f->mode==1?0x800:0;}
 CHECK(size==1);f->in8++;
 if(f->mode==2)return 0;
 return f->mode==3 || f->fail_transaction==f->transactions?0x26:0x10;
}
static void out(void *p,unsigned port,unsigned size,unsigned value){
 struct fixture *f=p;CHECK(f->nout<32);f->values[f->nout][0]=port;f->values[f->nout][1]=size;f->values[f->nout++][2]=value;
 if(port==0xc008)f->reg=value;
 if(port==0xc002)f->transactions++;
}
static int delay(void *p,unsigned us){struct fixture *f=p;CHECK(us==10 || us==1000);f->delays++;return f->fail_delay==f->delays;}
int main(void){
 static const unsigned masks[8]={15,5,80,85,165,245,95,255};
 unsigned code,i,slots[4];
 for(code=0;code<8;code++){
  struct fixture f={0};struct signal658 r={0};const struct smc658 io={&f,in,out,delay};
  CHECK(show658(&io,code,10000,&r)==0);CHECK(f.nout==15 && f.delays==12000 && r.transactions==3);
  for(i=0;i<3;i++){
   unsigned n=5*i;CHECK(f.values[n][0]==0xc004 && f.values[n][1]==1 && f.values[n][2]==32);
   CHECK(f.values[n+1][0]==0xc008 && f.values[n+1][2]==(i==1?7:8));
   CHECK(f.values[n+2][0]==0xc006 && f.values[n+2][1]==2 && f.values[n+2][2]==(i==0?0:i==1?1:masks[code]));
   CHECK(f.values[n+3][0]==0xc000 && f.values[n+3][1]==2);
   CHECK(f.values[n+4][0]==0xc002 && f.values[n+4][2]==26);
  }
 }
 for(code=1;code<=3;code++){
  struct fixture f={0};struct signal658 r={0};const struct smc658 io={&f,in,out,delay};f.mode=code;
  CHECK(write658(&io,2,1,&r)==(code==1?2:code==2?4:3));
  CHECK(f.in16<=1002 && f.in8<=1000 && f.delays<=1000);CHECK(f.nout==(code==1?0:5));
 }
 for(code=1;code<=3;code++){
  struct fixture f={0};struct signal658 r={0};const struct smc658 io={&f,in,out,delay};f.fail_transaction=code;
  CHECK(show658(&io,0,10000,&r)==3);CHECK(f.nout==code*5);
 }
 {unsigned failures[]={1,2000,2001,12000};for(i=0;i<4;i++){
  struct fixture f={0};struct signal658 r={0};const struct smc658 io={&f,in,out,delay};f.fail_delay=failures[i];
  CHECK(show658(&io,4,10000,&r)==1);CHECK(f.delays==failures[i]);CHECK(f.nout==(i<2?10:15));
 }}
 for(code=1;code<=5;code++){
  struct result656 r={0};classify658(0,code,2,&r,slots);CHECK(slots[0]==2 && slots[1]*8+slots[2]==code && slots[3]==0);
 }
 for(code=1;code<=11;code++)for(i=1;i<=6;i++){
  struct result656 r={0};r.used=1;r.safe_to_continue=1;r.failed_phase=i;
  classify658(0,0,code,&r,slots);CHECK(slots[0]==3 && slots[1]*8+slots[2]==code && slots[3]==i);
  r.safe_to_continue=0;r.cleanup_error=code;classify658(0,0,0,&r,slots);CHECK(slots[0]==5 && slots[1]*8+slots[2]==code);
 }
 {struct result656 r={0};r.used=1;r.safe_to_continue=1;r.completed=3;
  classify658(0,0,0,&r,slots);CHECK(slots[0]==0 && slots[1]==0 && slots[2]==0 && slots[3]==0);
  classify658(1,0,0,&r,slots);CHECK(slots[0]==7 && slots[1]*8+slots[2]==15);
  r.used=0;classify658(0,0,0,&r,slots);CHECK(slots[0]==4 && slots[1]*8+slots[2]==15);
  classify658(0,0,100,&r,slots);CHECK(slots[0]==3 && slots[1]==7 && slots[2]==7);
 }
 {struct fixture f={0};struct signal658 r={0};const struct smc658 io={&f,in,out,delay};
  CHECK(show658(&io,8,1000,&r)==5);CHECK(show658(&io,0,10001,&r)==5);CHECK(show658(&io,0,0,&r)==5);CHECK(f.nout==0 && f.delays==0);
  f.mode=1;f.fail_delay=1;CHECK(write658(&io,2,1,&r)==1);CHECK(f.nout==0 && f.delays==1);
 }
 printf("{\"checks\":%u,\"status\":\"pass\"}\n",checks);return 0;
}
