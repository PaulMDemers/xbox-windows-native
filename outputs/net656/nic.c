/* SPDX-License-Identifier: GPL-2.0-or-later
 * Register sequence derived from retained Cromwell Etherboot forcedeth.c:
 * Timothy Legge 2004; Linux forcedeth (C) 2003 Manfred Spraul.
 * Dedicated post-capture diagnostic. No legacy driver entry is replaced.
 */
#include "nic.h"
enum { IRQ=0,MASK=4,SETUP6=8,POLL=12,MISC=0x80,TX=0x84,TXSTATUS=0x88,
 FILTER=0x8c,OFFLOAD=0x90,RX=0x94,RXSTATUS=0x98,SEED=0x9c,
 SETUP1=0xa0,SETUP2=0xa4,MACA=0xa8,MACB=0xac,MCASTA=0xb0,MCASTB=0xb4,
 MCASTMA=0xb8,MCASTMB=0xbc,TXRING=0x100,RXRING=0x104,RINGS=0x108,
 TXUNKNOWN=0x10c,LINK=0x110,SETUP5=0x130,SETUP3=0x134,CONTROL=0x144,
 MIISTATUS=0x180,SETUP4=0x184,ADAPTER=0x188,MIISPEED=0x18c,
 MIICONTROL=0x190,MIIDATA=0x194,WAKE=0x200,POWER=0x26c };
struct context {const struct io656 *io;const struct plan656 *plan;struct result656 *r;};
static void copy(uint8_t *d,const uint8_t *s,unsigned n){unsigned i;for(i=0;i<n;i++)d[i]=s[i];}
static void zero(void *p,unsigned n){uint8_t *d=p;unsigned i;for(i=0;i<n;i++)d[i]=0;}
static void be16(uint8_t *d,unsigned v){d[0]=(uint8_t)(v>>8);d[1]=(uint8_t)v;}
static unsigned sum(const uint8_t *p,unsigned n,unsigned v){
 unsigned i;for(i=0;i+1<n;i+=2)v+=((unsigned)p[i]<<8)|p[i+1];
 if(n&1)v+=(unsigned)p[n-1]<<8;
 while(v>>16)v=(v&65535)+(v>>16);
 return v;
}
static int valid(const struct plan656 *p){
 unsigned i,v=0;
 if(!p || !p->post_capture || !p->admitted || p->port<1024 ||
    (p->mac[0]&1) || !p->source_ip[0] || p->source_ip[0]>=224 || p->source_ip[0]==127 ||
    !(p->command&2) || p->dma_bus<0x02600000u || (p->dma_bus&31) ||
    p->dma_bus>0x027c0000u-sizeof(struct dma656))return 0;
 for(i=0;i<6;i++)v|=p->mac[i];
 return v!=0;
}
int frame656(uint8_t *out,unsigned capacity,const struct plan656 *p,const uint8_t *payload,unsigned n){
 unsigned i,v;uint8_t *ip,*udp;
 if(!out || !payload || n!=772 || capacity<N656_FRAME || !valid(p))return N656_ARGUMENT;
 zero(out,N656_FRAME);for(i=0;i<6;i++)out[i]=255;copy(out+6,p->mac,6);be16(out+12,0x800);
 ip=out+14;udp=ip+20;ip[0]=0x45;be16(ip+2,800);be16(ip+6,0x4000);ip[8]=1;ip[9]=17;
 copy(ip+12,p->source_ip,4);for(i=16;i<20;i++)ip[i]=255;
 be16(ip+10,(~sum(ip,20,0))&65535);be16(udp,p->port);be16(udp+2,p->port);be16(udp+4,780);
 copy(udp+8,payload,n);v=sum(ip+12,8,17+780);v=(~sum(udp,780,v))&65535;
 be16(udp+6,v?v:65535);return 0;
}
/* 32-bit wrap is supported. A frozen timer exhausts a finite sample budget.
 * A backward jump larger than the requested interval is rejected, not accepted
 * as elapsed time. This is a callback-count bound, not a bus-hang guarantee.
 */
int delay656(const struct io656 *io,struct result656 *r,unsigned us){
 uint32_t begin,now,elapsed,need;unsigned i;
 if(!io || !io->ticks || !r || !us || us>1000)return N656_ARGUMENT;
 need=(us*3580u+999u)/1000u;begin=io->ticks(io->p);r->timer_reads++;
 for(i=0;i<200000;i++){
  now=io->ticks(io->p);r->timer_reads++;elapsed=now-begin;
  if(elapsed>3579545u)return N656_TIMER;
  if(elapsed>=need)return 0;
 }
 return N656_TIMER;
}
static int rd(struct context *c,unsigned a,uint32_t *v){
 c->r->reads++;c->r->last_reg=a;
 if(c->io->read(c->io->p,a,v))return N656_IO;
 c->r->last_value=*v;return 0;
}
static int wr(struct context *c,unsigned a,uint32_t v){
 uint32_t posted;c->r->writes++;c->r->mutated=1;
 if(c->io->write(c->io->p,a,v))return N656_IO;
 return rd(c,IRQ,&posted); /* flush posted write; read does not acknowledge */
}
static int delay(struct context *c,unsigned us){return delay656(c->io,c->r,us);}
static void syncmem(struct context *c){c->r->cache_syncs++;c->io->sync(c->io->p);}
#define TRY(x) do{int e=(x);if(e)return e;}while(0)
static int waitreg(struct context *c,unsigned reg,uint32_t mask,uint32_t value,unsigned count,unsigned us,int timeout){
 unsigned i;uint32_t v;
 for(i=0;i<count;i++){TRY(rd(c,reg,&v));if((v&mask)==value)return 0;TRY(delay(c,us));}
 return timeout;
}
static int quiet(struct context *c){
 int first=0,e;uint32_t v;
 /* Best-effort all stops even after one fault. Bus mastering is disabled last,
  * also on timeout. Caller still must quarantine on ANY failed cleanup check. */
#define CLEAN(x) do{e=(x);if(e && !first)first=e;}while(0)
 CLEAN(wr(c,MASK,0));CLEAN(wr(c,RX,0));CLEAN(wr(c,TX,0));
 CLEAN(waitreg(c,RXSTATUS,1,0,50000,10,N656_STOP));
 CLEAN(waitreg(c,TXSTATUS,1,0,50000,10,N656_STOP));
 CLEAN(wr(c,LINK,0));CLEAN(wr(c,TXUNKNOWN,0));
 c->r->mutated=1;CLEAN(c->io->command(c->io->p,(uint16_t)(c->plan->command&~4u))?N656_IO:0);
 CLEAN(rd(c,MASK,&v));if(!e && v) {if(!first)first=N656_STOP;}
 return first;
#undef CLEAN
}
static int mii(struct context *c,unsigned phy,unsigned reg,uint32_t *value){
 uint32_t v;
 TRY(wr(c,MIISTATUS,15));
 TRY(rd(c,MIICONTROL,&v));
 if(v&0x10000u){TRY(wr(c,MIICONTROL,0x10000));TRY(delay(c,50));}
 TRY(wr(c,MIICONTROL,0x10000|(phy<<5)|reg));
 TRY(waitreg(c,MIICONTROL,0x10000,0,1000,10,N656_PHY));
 TRY(rd(c,MIISTATUS,&v));if(v&1)return N656_PHY;
 TRY(delay(c,50));TRY(rd(c,MIIDATA,value));return 0;
}
static int init(struct context *c,struct dma656 *d){
 unsigned i,phy,full=0;uint32_t a,b,link=0,v;int e;
 TRY(quiet(c)); /* Do not publish any owned ring until old engines stop. */
 c->r->phase=2;
 TRY(wr(c,FILTER,0));TRY(wr(c,ADAPTER,0));TRY(wr(c,CONTROL,0x14));TRY(delay(c,4));TRY(wr(c,CONTROL,4));
 TRY(wr(c,SETUP6,0));
 zero(d,sizeof(*d));
 for(i=0;i<4;i++){
  d->rx[i].address=c->plan->dma_bus+(uint32_t)OFF656(struct dma656,rxbuf)+i*N656_BUFFER;
  d->rx[i].length=N656_BUFFER;d->rx[i].flags=0x8000;
 }
 a=(uint32_t)c->plan->mac[0]|((uint32_t)c->plan->mac[1]<<8)|((uint32_t)c->plan->mac[2]<<16)|((uint32_t)c->plan->mac[3]<<24);
 b=(uint32_t)c->plan->mac[4]|((uint32_t)c->plan->mac[5]<<8);
 TRY(wr(c,MACA,a));TRY(wr(c,MACB,b));
 TRY(wr(c,SETUP3,0x200010));TRY(wr(c,CONTROL,0));TRY(wr(c,CONTROL,2));
 TRY(waitreg(c,SETUP5,0x80000000u,0x80000000u,10000,5,N656_SETUP));TRY(wr(c,SETUP4,0));
 TRY(wr(c,MIISPEED,0x105));c->r->phase=3;
 for(phy=1;phy<32;phy++){
  e=mii(c,phy,2,&a);if(e==N656_IO || e==N656_TIMER)return e;if(e)continue;
  e=mii(c,phy,3,&b);if(e==N656_IO || e==N656_TIMER)return e;if(e)continue;
  if((a&65535) && (a&65535)!=65535 && (b&65535) && (b&65535)!=65535)break;
 }
 if(phy==32)return N656_PHY;
 c->r->phy=phy;
 /* Read twice: standard BMSR link indication can latch low. */
 for(i=0;i<2000;i++){
  TRY(mii(c,phy,1,&a));TRY(mii(c,phy,1,&b));
  if((b&0x24)==0x24)break;
  TRY(delay(c,1000));
 }
 if(i==2000)return N656_LINK;
 TRY(mii(c,phy,4,&a));TRY(mii(c,phy,5,&b));v=a&b;
 if(v&0x100){link=100;full=1;}else if(v&0x80)link=100;
 else if(v&0x40){link=10;full=1;}else if(v&0x20)link=10;else return N656_LINK;
 c->r->phase=4;
 TRY(wr(c,MISC,0x3b0f3c|(full?0:2)));
 TRY(rd(c,TXSTATUS,&v));TRY(wr(c,TXSTATUS,v));
 TRY(wr(c,FILTER,0x7f0008));TRY(wr(c,OFFLOAD,0x5ee));
 TRY(rd(c,RXSTATUS,&v));TRY(wr(c,RXSTATUS,v));
 TRY(wr(c,SEED,0x7f00|(75963081&255)));TRY(wr(c,SETUP1,0x16070f));TRY(wr(c,SETUP2,0x16));
 TRY(wr(c,POLL,970));TRY(wr(c,SETUP6,3));TRY(wr(c,ADAPTER,(phy<<24)|0x4000));
 TRY(wr(c,SETUP4,8));TRY(wr(c,WAKE,0x7770));
 syncmem(c);
 TRY(wr(c,RXRING,c->plan->dma_bus+(uint32_t)OFF656(struct dma656,rx)));
 TRY(wr(c,TXRING,c->plan->dma_bus));TRY(wr(c,RINGS,(3u<<16)|1));
 TRY(rd(c,POWER,&v));TRY(wr(c,POWER,v|0x8000));TRY(delay(c,10));
 TRY(rd(c,POWER,&v));TRY(wr(c,POWER,v|0x100));TRY(wr(c,ADAPTER,0x100000));
 TRY(wr(c,MASK,0));TRY(wr(c,IRQ,0x1ff));TRY(wr(c,MIISTATUS,15));
 TRY(wr(c,MCASTA,1));TRY(wr(c,MCASTB,0));TRY(wr(c,MCASTMA,0));TRY(wr(c,MCASTMB,0));
 TRY(wr(c,FILTER,0x7f0028));TRY(wr(c,LINK,0x10000|link));
 /* All DMA buffers are ours before bus mastering and engine start. */
 if(c->io->command(c->io->p,c->plan->command|4))return N656_IO;
 TRY(wr(c,RX,1));TRY(wr(c,TX,1));return 0;
}
static int burst(struct context *c,struct dma656 *d,const uint8_t *payload){
 unsigned copy_index,i,n;uint16_t flags;uint32_t irq;int e;
 for(copy_index=0;copy_index<3;copy_index++){
  n=copy_index%2;syncmem(c);if(d->tx[n].flags&0x8000)return N656_DESCRIPTOR;
  e=frame656(d->txbuf[n],N656_BUFFER,c->plan,payload,772);if(e)return e;
  d->tx[n].address=c->plan->dma_bus+(uint32_t)OFF656(struct dma656,txbuf)+n*N656_BUFFER;
  d->tx[n].length=N656_FRAME-1;d->tx[n].flags=0;
  syncmem(c);d->tx[n].flags=0x8001;syncmem(c);c->r->published++;
  TRY(wr(c,CONTROL,1));
  for(i=0;i<10000;i++){
   syncmem(c);flags=d->tx[n].flags;
   if(!(flags&0x8000))break;
   TRY(delay(c,50));
  }
  if(i==10000)return N656_TX_TIMEOUT;
  if(flags&0x7808)return N656_TX_ERROR;
  TRY(rd(c,IRQ,&irq));if(irq&8)return N656_TX_ERROR;
  c->r->completed++;
 }
 return 0;
}
int send656(const struct io656 *io,const struct plan656 *plan,struct dma656 *d,
 const uint8_t *payload,unsigned bytes,struct result656 *r){
 struct context c;int e;
 if(!r)return N656_ARGUMENT;
 if(r->used)return N656_ALREADY;
 if(!io || !io->read || !io->write || !io->ticks || !io->command || !io->sync ||
    !valid(plan) || !d || !payload || bytes!=772 || ((__UINTPTR_TYPE__)d&31))return N656_ARGUMENT;
 zero(r,sizeof(*r));r->used=1;r->phase=1;c=(struct context){io,plan,r};
 e=init(&c,d);if(!e){r->phase=5;e=burst(&c,d,payload);}
 r->error=e;r->failed_phase=e?r->phase:0;r->phase=6;r->cleanup_error=quiet(&c);
 r->safe_to_continue=r->cleanup_error==0;r->phase=7;
 return e?e:(int)r->cleanup_error;
}
