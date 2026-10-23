/* SPDX-License-Identifier: GPL-2.0-or-later */
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "signal672.h"
struct event { unsigned ms,reg,value; };
struct model {
 unsigned reg,value,tx,failtx,mode,calls,faildelay,ms,n,reenter;
 struct event ev[128];
 struct emission672 *owner;
 const struct smc658 *io;
};
static unsigned tests;
static unsigned in(void *p,unsigned port,unsigned width){
 struct model *m=p;assert(port==0xc000 && (width==1 || width==2));
 if(m->mode==1)return 0x800;
 if(width==1 && (m->mode==2 || m->tx==m->failtx))return 0x26;
 if(m->mode==3)return 0;
 return 0x10;
}
static void out(void *p,unsigned port,unsigned width,unsigned value){
 struct model *m=p;
 if(port==0xc008){assert(width==1);m->reg=value;}
 else if(port==0xc006){assert(width==2);m->value=value;}
 else if(port==0xc002){
  assert(width==1 && value==0x1a && m->n<128);m->tx++;
  m->ev[m->n++]=(struct event){m->ms,m->reg,m->value};
 }else assert((port==0xc004 && width==1 && value==0x20) || (port==0xc000 && width==2));
}
static int delay(void *p,unsigned us){
 struct model *m=p;assert(us==10 || us==1000);m->calls++;
 if(m->reenter){
  struct emission672 before=*m->owner;m->reenter=0;
  assert(marker672(m->io,m->owner)==6);
  assert(!memcmp(&before,m->owner,sizeof(before)));
 }
 if(us==1000)m->ms++;
 return m->calls==m->faildelay;
}
static void check(const struct record669 *r,unsigned kind,unsigned value){
 struct record669 before=*r;struct code672 c=classify672(r);
 assert(c.kind==kind && c.value==value);
 assert(!memcmp(&before,r,sizeof(before)));tests++;
}
static void event(struct model *m,unsigned *at,unsigned ms,unsigned reg,unsigned value){
 assert(*at<m->n);assert(m->ev[*at].ms==ms && m->ev[*at].reg==reg && m->ev[*at].value==value);(*at)++;
}
static struct smc658 io_for(struct model *m){struct smc658 io={m,in,out,delay};return io;}
static void waveform(unsigned kind,unsigned value){
 static const unsigned masks[]={0x50,0xa5,0x55,0x5f,0xf5,0x0f,0xf0};
 struct model m={0};struct emission672 r={0};struct smc658 io=io_for(&m);
 struct code672 c={kind,value};unsigned at=0,t=0,j,k,total;
 m.owner=&r;m.io=&io;m.reenter=1;
 assert(report672(&io,&r,c)==0 && r.complete && r.used==1);
 event(&m,&at,0,8,0);event(&m,&at,0,7,1);
 for(j=0;j<2;j++){
  t+=2000;event(&m,&at,t,8,masks[kind]);
  t+=6000;event(&m,&at,t,8,0);t+=2000;
  for(k=0;k<value+1;k++){
   event(&m,&at,t,8,0xf0);t+=500;event(&m,&at,t,8,0);t+=500;
  }
 }
 event(&m,&at,t,8,masks[kind]);assert(at==m.n && m.ms==t && t<=44000);
 assert(r.steps==m.tx && r.milliseconds==t && r.pauses==6+4*(value+1));
 total=m.tx;
 {struct emission672 before=r;unsigned calls=m.calls;
  assert(report672(&io,&r,c)==6 && !memcmp(&before,&r,sizeof(r)) && m.calls==calls && m.tx==total);}
 tests++;
 /* Every SMC transaction can fail; no later transaction or continuation. */
 for(j=1;j<=total;j++){
  memset(&m,0,sizeof(m));memset(&r,0,sizeof(r));m.failtx=j;
  assert(report672(&io,&r,c)==3 && r.error==3 && !r.complete && m.tx==j);
  assert(report672(&io,&r,c)==6 && m.tx==j);tests++;
 }
 /* First, middle and last timer sample failures retain the exact stop. */
 for(j=0;j<3;j++){
  unsigned sample=j==0?1:j==1?t/2:t;
  memset(&m,0,sizeof(m));memset(&r,0,sizeof(r));m.faildelay=sample;
  assert(report672(&io,&r,c)==1 && r.error==1 && !r.complete && m.calls==sample);
  tests++;
 }
}
int main(void){
 struct record669 r={0};struct model m={0};struct emission672 e={0};struct smc658 io=io_for(&m);
 struct code672 c={0,0};unsigned i,j,at=0;
 assert(classify672(0).kind==INVALID672);tests++;
 check(&r,INVALID672,1);r.phase=HELD669;
 for(i=0;i<SENT669;i++){r.status=i;check(&r,WRAPPER672,i);}
 r.status=ADMISSION669;
 for(i=1;i<=5;i++){r.result.admission=i;check(&r,ADMISSION672,i);}
 r.result.admission=0;r.status=SEND_FAILED669;
 for(i=1;i<=11;i++){
  r.send_error=i;check(&r,SEND672,i);r.send_error=0;
  r.result.error=i;check(&r,NATIVE672,i);r.result.error=0;
 }
 r.status=UNSAFE669;r.result.used=1;
 for(i=1;i<=11;i++){r.result.cleanup_error=i;check(&r,CLEANUP672,i);}
 r.result.cleanup_error=0;r.status=SENT669;check(&r,INVALID672,2);
 r.enter_called=r.send_called=r.flags_valid=1;r.result.safe=1;r.result.completed=3;
 check(&r,SUCCESS672,0);
 for(i=0;i<13;i++){
  struct record669 bad=r;
  switch(i){
  case 0:bad.faults=1;break;case 1:bad.enter_called=0;break;case 2:bad.send_called=0;break;
  case 3:bad.flags_valid=0;break;case 4:bad.enter_error=1;break;case 5:bad.send_error=1;break;
  case 6:bad.result.admission=1;break;case 7:bad.result.used=0;break;case 8:bad.result.safe=0;break;
  case 9:bad.result.completed=2;break;case 10:bad.result.error=1;break;
  case 11:bad.result.cleanup_error=1;break;default:bad.final_flags=512;break;
  }
  check(&bad,INVALID672,2);
 }
 r.result.error=12;check(&r,INVALID672,1);r.result.error=0;
 r.result.admission=6;check(&r,INVALID672,1);
 for(i=0;i<=INVALID672;i++)for(j=0;j<=11;j++)if(i!=SUCCESS672 || j==0)waveform(i,j);
 m.owner=&e;m.io=&io;m.reenter=1;assert(marker672(&io,&e)==0 && e.complete && m.ms==10000);
 event(&m,&at,0,8,0);event(&m,&at,0,7,1);event(&m,&at,2000,8,5);event(&m,&at,10000,8,0);
 assert(at==m.n && marker672(&io,&e)==6);tests++;
 for(i=1;i<=4;i++){
  memset(&m,0,sizeof(m));memset(&e,0,sizeof(e));m.failtx=i;
  assert(marker672(&io,&e)==3 && !e.complete && m.tx==i);tests++;
 }
 for(i=1;i<=3;i++){
  memset(&m,0,sizeof(m));memset(&e,0,sizeof(e));m.mode=i;
  assert(marker672(&io,&e)==(i==1?2:i==2?3:4) && !e.complete);
  assert(m.calls==(i==2?0:1000));tests++;
 }
 for(i=0;i<3;i++){
  memset(&m,0,sizeof(m));memset(&e,0,sizeof(e));m.faildelay=i==0?1:i==1?5000:10000;
  assert(marker672(&io,&e)==1 && !e.complete && m.calls==m.faildelay);tests++;
 }
 memset(&m,0,sizeof(m));memset(&e,0,sizeof(e));
 assert(marker672(0,&e)==5 && !e.used);assert(marker672(&io,0)==5);
 c.kind=7;assert(report672(&io,&e,c)==5);c.kind=0;c.value=12;assert(report672(&io,&e,c)==5);
 c.kind=SUCCESS672;c.value=1;assert(report672(&io,&e,c)==5 && !e.used && !m.n && !m.calls);tests+=5;
 printf("{\"passed\":true,\"assertion_groups\":%u,\"waveform_codes\":73,\"max_report_ms\":44000,\"marker_ms\":10000}\n",tests);
 return 0;
}
