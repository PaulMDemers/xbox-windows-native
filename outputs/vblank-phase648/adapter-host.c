/* SPDX-License-Identifier: GPL-2.0-or-later */
#include "xwn_hd_adapter.h"
#include "trace648.h"
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
int baseline_apply(const struct xwn_hd_io *,const struct xwn_hd_request *,volatile struct xwn_hd_state *);
struct event {unsigned kind,address,value;};
#define MAX_EVENTS 1300000
struct model {
 struct event *events;unsigned count,used,index,edge_enabled,phase,at;
 unsigned delay_samples[6],noise,fail_sync;
 uint32_t addr[128],value[128];unsigned char crtc[256];
};
static void record(struct model *m,unsigned k,unsigned a,unsigned v) {
 assert(m->count<MAX_EVENTS);m->events[m->count++]=(struct event){k,a,v};
}
static uint32_t r32(void *v,uint32_t a) {
 struct model*m=v;unsigned i;uint32_t x=0;
 if(a==0x6806a0)x=m->fail_sync?1:0;
 else if(a==0x680508)x=0x3c20d;
 else if(a==0x600804)x=3;
 else for(i=0;i<m->used;i++)if(m->addr[i]==a){x=m->value[i];break;}
 record(m,1,a,x);return x;
}
static void w32(void*v,uint32_t a,uint32_t x) {
 struct model*m=v;unsigned i;record(m,2,a,x);
 for(i=0;i<m->used;i++)if(m->addr[i]==a)break;
 assert(i<128);if(i==m->used)m->used++;m->addr[i]=a;m->value[i]=x;
}
static uint8_t r8(void*v,uint32_t a) {
 struct model*m=v;unsigned x=0;
 if(a==0x6013da && m->edge_enabled) {
  unsigned wanted;assert(m->phase<6);wanted=(m->phase%2)*8;
  x=0xa0|(m->at<m->delay_samples[m->phase]?(wanted^8):wanted);
  if(m->noise)x|=m->at&1;
  m->at++;
  if((x&8)==wanted){m->phase++;m->at=0;}
 } else if(a==0x6013d5)x=m->crtc[m->index];
 record(m,3,a,x);return (uint8_t)x;
}
static void w8(void*v,uint32_t a,uint8_t x) {
 struct model*m=v;record(m,4,a,x);
 if(a==0x6013d4)m->index=x;
 if(a==0x6013d5)m->crtc[m->index]=x;
 if(a==0xc03c5 && x==1)m->edge_enabled=1;
}
static uint16_t in16(void*v,uint16_t a){struct model*m=v;record(m,5,a,0);return 0;}
static uint8_t in8(void*v,uint16_t a){struct model*m=v;record(m,6,a,0x10);return 0x10;}
static void out16(void*v,uint16_t a,uint16_t x){record(v,7,a,x);}
static void out8(void*v,uint16_t a,uint8_t x){record(v,8,a,x);}
static void delay(void*v,unsigned us){record(v,9,0,us);}
static struct xwn_hd_io io(struct model*m){struct xwn_hd_io i={m,r32,w32,r8,w8,in16,in8,out16,out8,delay};return i;}
static unsigned cases;
static void run(unsigned mode,int target,unsigned lag,unsigned noise,unsigned gate,unsigned sync) {
 struct model a={0},b={0};struct xwn_hd_state sa,sb;
 struct xwn_hd_request r={mode,67108864,57671680,9437184,316160,0,3,mode==3?8:2};
 struct xwn_hd_io ia,ib;unsigned i,completed=0,failed=0;int ra,rb;
 a.events=calloc(MAX_EVENTS,sizeof(struct event));b.events=calloc(MAX_EVENTS,sizeof(struct event));assert(a.events&&b.events);
 a.noise=b.noise=noise;a.fail_sync=b.fail_sync=sync;
 for(i=0;i<6;i++)a.delay_samples[i]=b.delay_samples[i]=target==-2?i+1:0;
 if(target>=0)a.delay_samples[target]=b.delay_samples[target]=lag;
 if(gate)r.cable=1;
 ia=io(&a);ib=io(&b);ra=baseline_apply(&ia,&r,&sa);rb=xwn_hd_apply(&ib,&r,&sb);
 assert(ra==rb && !memcmp(&sa,&sb,sizeof sa));
 assert(a.count==b.count && !memcmp(a.events,b.events,a.count*sizeof(struct event)));
 if(gate||sync)assert(!XwnTrace648.waits_started && !XwnTrace648.failed_wait);
 else {
  for(i=0;i<6;i++) {
   volatile struct xwn_edge648 *e=&XwnTrace648.edge[i];
   unsigned n=b.delay_samples[i],samples=n>=100000?100000:n+1,wanted=(i%2)*8;
   unsigned first=0xa0|(n?(wanted^8):wanted);
   unsigned last=0xa0|(n>=100000?(wanted^8):wanted)|(noise?((samples-1)&1):0);
   assert(e->wanted==wanted && e->samples==samples && e->first==first && e->last==last);
   assert(e->bit_changes==(n && n<100000?1u:0u));
   assert(e->byte_changes==(noise?samples-1:(n && n<100000?1u:0u)));
   if(n>=100000){failed=i+1;assert(!e->completed);break;}
   assert(e->completed);completed++;
  }
  assert(XwnTrace648.failed_wait==failed && XwnTrace648.waits_completed==completed);
  assert(XwnTrace648.waits_started==completed+(failed?1u:0u));
  for(i=XwnTrace648.waits_started;i<6;i++) {
   const unsigned *words=(const unsigned *)&XwnTrace648.edge[i];unsigned j;
   for(j=0;j<7;j++)assert(!words[j]);
  }
  assert(rb==(failed?-1:1));
 }
 cases++;free(a.events);free(b.events);
}
int main(void) {
 unsigned m,i,n;
 for(m=1;m<=3;m+=2) {
  run(m,-1,0,0,0,0);run(m,-2,0,1,0,0);
  for(i=0;i<6;i++)for(n=99999;n<=100001;n++)run(m,(int)i,n,1,0,0);
  run(m,-1,0,0,1,0);run(m,-1,0,0,0,1);
 }
 printf("PASS %u differential scenarios: exact callback sequence/state, phase and sampled-byte trace\n",cases);
 return 0;
}
