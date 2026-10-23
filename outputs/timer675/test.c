/* SPDX-License-Identifier: GPL-2.0-or-later */
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "probe.h"
struct model {
 uint32_t tick,step,mask;
 unsigned reads,ports,tx,reg,value,values[6],regs[6],mode,failtx;
 unsigned flags_calls,flags_at,reenter;
 struct record675 *record;struct ops675 *ops;
};
static unsigned cases;
static uint32_t flags(void *p){struct model *m=p;m->flags_calls++;return m->flags_calls==m->flags_at?514:2;}
static uint32_t ticks(void *p){
 struct model *m=p;
 if(m->reenter){struct record675 before=*m->record;m->reenter=0;
  assert(probe675(m->ops,m->record,1000)==BUSY675 && !memcmp(&before,m->record,sizeof(before)));}
 m->reads++;m->tick=(m->tick+m->step)&m->mask;return m->tick;
}
static unsigned input(void *p,unsigned port,unsigned width){
 struct model *m=p;m->ports++;assert(port==0xc000 && (width==1 || width==2));
 if(m->tx+1==m->failtx && width==2 && m->mode==1)return 0x800;
 if(m->tx==m->failtx && width==1)return m->mode==2?0:0x26;
 return 0x10;
}
static void output(void *p,unsigned port,unsigned width,unsigned v){
 struct model *m=p;m->ports++;
 if(port==0xc008){assert(width==1);m->reg=v;}
 else if(port==0xc006){assert(width==2);m->value=v;}
 else if(port==0xc002){assert(width==1 && v==0x1a && m->tx<6);m->regs[m->tx]=m->reg;m->values[m->tx++]=m->value;}
 else assert((port==0xc004 && width==1 && v==0x20)||(port==0xc000 && width==2));
}
static void reset(struct model *m,struct record675 *r){
 memset(m,0,sizeof(*m));memset(r,0,sizeof(*r));m->step=100;m->mask=0xffffffffu;
}
static struct ops675 ops(struct model *m){struct ops675 o={m,flags,ticks,input,output};return o;}
static void check_repeat(struct model *m,struct record675 *r,struct ops675 *o){
 struct record675 before=*r;unsigned ports=m->ports,reads=m->reads;
 assert(probe675(o,r,1000)==BUSY675 && !memcmp(&before,r,sizeof(before)) && m->ports==ports && m->reads==reads);cases++;
}
static void timer_case(uint32_t start,uint32_t step,uint32_t mask,unsigned us,unsigned error,unsigned expected_reads){
 struct model m;struct record675 r;struct ops675 o;unsigned i;
 reset(&m,&r);m.tick=start;m.step=step;m.mask=mask;o=ops(&m);m.record=&r;m.ops=&o;m.reenter=1;
 assert(probe675(&o,&r,us)==OK675 && r.phase==DONE675 && r.final_complete);
 assert(r.timer_error==error && m.reads==expected_reads && r.total_samples==m.reads);
 assert(r.timer_accounting.timer_reads==m.reads && !r.timer_accounting.used && !r.wait_refusals);
 assert(r.stored_samples==(m.reads>64?64:m.reads));
 for(i=0;i<r.stored_samples;i++){start=(start+step)&mask;assert(r.samples[i]==start);}
 assert(r.last_sample==m.tick && r.final_mask==(error?0xa5:0x0f));
 assert(m.tx==3 && m.regs[0]==8 && m.values[0]==0x5f && m.regs[1]==7 && m.values[1]==1 && m.regs[2]==8 && m.values[2]==r.final_mask);
 check_repeat(&m,&r,&o);cases++;
}
int main(void){
 struct model m;struct record675 r;struct ops675 o;unsigned i,j;
 /* Independent arithmetic: one start sample, then ceil(ceil(us*3.58)/100)
  * samples for a monotonically advancing100-tick model. */
 for(i=1;i<=1000;i++)timer_case(0,100,0xffffffffu,i,0,1+(((i*3580+999)/1000)+99)/100);
 timer_case(0,0,0xffffffffu,1000,N656_TIMER,200001);
 timer_case(100000,0xffffffffu,0xffffffffu,1000,N656_TIMER,2);
 timer_case(0,3579546,0xffffffffu,1000,N656_TIMER,2);
 timer_case(0xffffff00u,100,0xffffffffu,1000,0,37);
 /* Hypothetical truncated counter: not a claim about physical Xbox width. */
 timer_case(0x00ffff00u,100,0x00ffffffu,1000,N656_TIMER,3);
 /* Both entry transactions and final transaction can independently fail. */
 for(i=1;i<=3;i++)for(j=1;j<=3;j++){
  reset(&m,&r);o=ops(&m);m.failtx=i;m.mode=j;
  assert(probe675(&o,&r,1000)==(i==3?FINAL_SMC675:ENTRY_SMC675));
  assert(!r.final_complete && m.reads==(i==3?37:0));
  assert(r.wait_refusals==(j==3?0:1) && r.last_wait_us==(j==3?0:10));
  assert(m.tx==(j==1?i-1:i));check_repeat(&m,&r,&o);cases++;
 }
 for(i=1;i<=3;i++){
  reset(&m,&r);o=ops(&m);m.flags_at=i;
  assert(probe675(&o,&r,1000)==IF675 && m.tx==(i==1?0:2));
  assert(m.reads==(i==3?37:0));check_repeat(&m,&r,&o);cases++;
 }
 reset(&m,&r);o=ops(&m);
 assert(probe675(0,&r,1000)==ARG675 && probe675(&o,0,1000)==ARG675);
 assert(probe675(&o,&r,0)==ARG675 && probe675(&o,&r,1001)==ARG675);
 o.ticks=0;assert(probe675(&o,&r,1000)==ARG675 && !r.phase && !m.ports && !m.reads);cases+=5;
 printf("{\"passed\":true,\"assertion_groups\":%u,\"durations\":1000,\"max_timer_samples\":200001,\"timed_indicator_waits\":0}\n",cases);
 return 0;
}
