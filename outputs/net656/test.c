/* SPDX-License-Identifier: GPL-2.0-or-later
 * Independent register/descriptor fault model, not hardware qualification.
 */
#include "nic.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
struct model {
 uint32_t regs[0x270/4],tick,step;unsigned ops,fail_at,commands,kicks,stops;
 unsigned frozen,no_phy,no_link,setup_stuck,mii_stuck,tx_stuck,tx_error,stop_stuck;
 unsigned occupied,command_fail,backwards,irq_error;uint16_t command;
 struct dma656 dma;
};
static unsigned checks;
static int fault(struct model *m){m->ops++;return m->fail_at && m->ops==m->fail_at;}
static int readreg(void *p,unsigned reg,uint32_t *v){
 struct model *m=p;assert(!(reg&3) && reg<0x270);
 if(fault(m))return -1;
 if(reg==0x130){*v=m->setup_stuck?0:0x80000000u;return 0;}
 if(reg==0x190 && m->mii_stuck){*v=0x10000;return 0;}
 if((reg==0x88 || reg==0x98) && m->stop_stuck){*v=1;return 0;}
 *v=m->regs[reg/4];return 0;
}
static int writereg(void *p,unsigned reg,uint32_t v){
 struct model *m=p;unsigned phy,r,index;
 assert(!(reg&3) && reg<0x270);if(fault(m))return -1;
 if(reg==0 || reg==0x180){m->regs[reg/4]&=~v;return 0;}
 m->regs[reg/4]=v;
 if(reg==0x190 && (v&0x10000)){
  phy=(v>>5)&31;r=v&31;
  m->regs[0x190/4]=0;m->regs[0x194/4]=0xffff;
  if(phy==1 && !m->no_phy){
   if(r==2)m->regs[0x194/4]=0x1234;
   if(r==3)m->regs[0x194/4]=0x5678;
   if(r==1)m->regs[0x194/4]=m->no_link?0:0x24;
   if(r==4 || r==5)m->regs[0x194/4]=0x1e0;
  }
 }
 if(reg==0x84 && v==0)m->stops++;
 if(reg==0x84 && v==1 && m->occupied)m->dma.tx[0].flags=0x8000;
 if(reg==0x144 && v==1){
  index=m->kicks%2;
  assert(m->command&4);assert(m->regs[0x84/4]==1);
  assert(m->regs[0x100/4]==0x02680000);
  assert(m->regs[0x104/4]==0x02680020);
  assert(m->dma.tx[index].flags==0x8001);
  assert(m->dma.tx[index].length==813);
  assert(m->dma.tx[index].address==0x02680040u+index*1536);
  /* If a second packet is published early, the previous one is still owned. */
  if(m->kicks)assert(!(m->dma.tx[index^1].flags&0x8000));
  m->kicks++;
  if(m->irq_error)m->regs[0]|=8;
  if(!m->tx_stuck)m->dma.tx[index].flags=m->tx_error?0x4000:1;
 }
 return 0;
}
static int command(void *p,uint16_t v){
 struct model *m=p;m->commands++;
 if(fault(m) || m->command_fail)return -1;
 /* Command access must never contain PCI status bits. */
 assert(v==3 || v==7);m->command=v;return 0;
}
static uint32_t ticks(void *p){struct model *m=p;
 if(m->backwards)m->tick--;else if(!m->frozen)m->tick+=m->step;
 return m->tick;
}
static void syncmem(void *p){(void)p;}
static struct plan656 plan(void){
 struct plan656 p={0};p.dma_bus=0x02680000;p.command=7;
 p.mac[0]=2;p.mac[5]=1;p.source_ip[0]=192;p.source_ip[1]=0;p.source_ip[2]=2;p.source_ip[3]=1;
 p.port=42655;p.post_capture=1;p.admitted=1;return p;
}
static void reset(struct model *m){memset(m,0,sizeof(*m));m->step=100;m->command=7;}
static struct io656 io(struct model *m){struct io656 i={m,readreg,writereg,command,ticks,syncmem};return i;}
static void outcome(struct model *m,unsigned wanted,unsigned safe){
 struct io656 i=io(m);struct plan656 p=plan();struct result656 r={0};uint8_t payload[772]={0};unsigned calls;
 int e=send656(&i,&p,&m->dma,payload,772,&r);
 assert((unsigned)e==wanted);assert(r.safe_to_continue==safe);assert(r.used);
 if(safe)assert(m->command==3 && m->regs[4/4]==0 && m->regs[0x84/4]==0 && m->regs[0x94/4]==0);
 assert(m->kicks<=3 && r.completed<=3 && r.completed<=r.published);
 calls=m->ops;assert(send656(&i,&p,&m->dma,payload,772,&r)==N656_ALREADY);assert(m->ops==calls);checks++;
}
static unsigned checksum(const uint8_t *p,unsigned n,unsigned v){unsigned j;for(j=0;j<n;j+=2)v+=((unsigned)p[j]<<8)|p[j+1];while(v>>16)v=(v&65535)+(v>>16);return v;}
int main(void){
 static struct model m;struct plan656 p=plan();struct io656 i;struct result656 r={0};
 uint8_t payload[772],frame[816],saved[816];unsigned j,n,calls;
 for(j=0;j<772;j++)payload[j]=(uint8_t)j;
 memset(frame,0xa5,sizeof(frame));memcpy(saved,frame,sizeof(frame));
 for(j=0;j<814;j++){assert(frame656(frame+1,j,&p,payload,772)==N656_ARGUMENT);assert(!memcmp(frame,saved,sizeof(frame)));checks++;}
 assert(!frame656(frame+1,814,&p,payload,772));assert(frame[0]==0xa5 && frame[815]==0xa5);
 assert(!memcmp(frame+43,payload,772));assert(checksum(frame+15,20,0)==65535);
 assert(checksum(frame+35,780,checksum(frame+27,8,17+780))==65535);checks++;
 reset(&m);i=io(&m);assert(!send656(&i,&p,&m.dma,payload,772,&r));
 assert(r.completed==3 && r.published==3 && r.safe_to_continue);calls=m.ops;checks++;
 /* Inject a one-shot I/O failure at every operation in the success path.
  * Cleanup may still recover; every call must terminate and report uncertainty. */
 for(j=1;j<=calls;j++){
  reset(&m);m.fail_at=j;i=io(&m);memset(&r,0,sizeof(r));
  assert(send656(&i,&p,&m.dma,payload,772,&r)!=0);
  assert(r.error || r.cleanup_error);assert(r.used && r.phase==7);
  if(r.cleanup_error)assert(!r.safe_to_continue);
  else assert(m.command==3 && m.regs[0x84/4]==0 && m.regs[0x94/4]==0);
  assert(m.kicks<=3);checks++;
 }
 reset(&m);outcome(&m,N656_OK,1);
 reset(&m);m.frozen=1;outcome(&m,N656_TIMER,1);
 reset(&m);m.backwards=1;outcome(&m,N656_TIMER,1);
 reset(&m);m.no_phy=1;outcome(&m,N656_PHY,1);
 reset(&m);m.no_link=1;outcome(&m,N656_LINK,1);
 reset(&m);m.setup_stuck=1;outcome(&m,N656_SETUP,1);
 reset(&m);m.mii_stuck=1;outcome(&m,N656_PHY,1);
 reset(&m);m.tx_stuck=1;outcome(&m,N656_TX_TIMEOUT,1);
 reset(&m);m.tx_error=1;outcome(&m,N656_TX_ERROR,1);
 reset(&m);m.irq_error=1;outcome(&m,N656_TX_ERROR,1);
 reset(&m);m.occupied=1;outcome(&m,N656_DESCRIPTOR,1);
 reset(&m);m.stop_stuck=1;outcome(&m,N656_STOP,0);
 reset(&m);m.command_fail=1;outcome(&m,N656_IO,0);
 for(n=1;n<=1000;n++){
  reset(&m);m.tick=0xfffffffeu;i=io(&m);memset(&r,0,sizeof(r));
  assert(!delay656(&i,&r,n));assert(r.timer_reads<=200001);checks++;
 }
 reset(&m);i=io(&m);memset(&r,0,sizeof(r));p.admitted=0;
 assert(send656(&i,&p,&m.dma,payload,772,&r)==N656_ARGUMENT && !m.ops);checks++;
 p=plan();p.dma_bus=0xffffffe0;
 assert(send656(&i,&p,&m.dma,payload,772,&r)==N656_ARGUMENT && !m.ops);checks++;
 p=plan();assert(send656(&i,&p,&m.dma,payload,773,&r)==N656_ARGUMENT && !m.ops);checks++;
 printf("{\"checks\":%u,\"injected_io_positions\":%u,\"hardware_access\":false}\n",checks,calls);
 return 0;
}
