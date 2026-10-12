/* SPDX-License-Identifier: GPL-2.0-or-later */
#include "adapter.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static unsigned checks;
#define CHECK(v) do{checks++;assert(v);}while(0)
struct model {
 uint32_t addr[128],value[128];unsigned used,reads,writes,delay,starts,unblank,blank;
 unsigned fail_at,busy,timeout,combined,sync_stuck,edge_stuck,bad_geometry,bad_pitch;
 uint8_t index,crt[256],reg,data,enc_reg[32],enc_value[32],vblank;
};
static uint32_t r32(void *v,uint32_t a){
 struct model*m=v;unsigned i;m->reads++;
 if(a==0x6806a0)return m->sync_stuck?1:0;
 if(a==0x680508)return 0x0003c20d;
 if(a==0x600804)return 3;
 for(i=0;i<m->used;i++)if(m->addr[i]==a)return m->value[i]^((m->bad_geometry&&a==0x680838)?1:0);
 return 0;
}
static void w32(void*v,uint32_t a,uint32_t x){
 struct model*m=v;unsigned i;m->writes++;
 CHECK(a!=0x680508&&a!=0x600804);
 for(i=0;i<m->used;i++)if(m->addr[i]==a)break;
 CHECK(i<128);if(i==m->used){m->used++;m->addr[i]=a;}m->value[i]=x;
}
static uint8_t r8(void*v,uint32_t a){
 struct model*m=v;m->reads++;
 if(a==0x6013da){if(!m->edge_stuck)m->vblank^=8;return m->vblank;}
 if(a==0x6013d5)return m->crt[m->index]^((m->bad_pitch==m->index)?(m->index==0x19?0x20:1):0);
 return 0;
}
static void w8(void*v,uint32_t a,uint8_t x){struct model*m=v;m->writes++;if(a==0x6013d4)m->index=x;if(a==0x6013d5)m->crt[m->index]=x;}
static uint16_t in16(void*v,uint16_t a){struct model*m=v;CHECK(a==0xc000);m->reads++;return m->busy?0x800:0;}
static uint8_t in8(void*v,uint16_t a){
 struct model*m=v;CHECK(a==0xc000);m->reads++;
 if(m->timeout)return 0;
 if(m->starts==m->fail_at)return m->combined?0x12:2;
 return 0x10;
}
static void out16(void*v,uint16_t a,uint16_t x){struct model*m=v;m->writes++;if(a==0xc006)m->data=(uint8_t)x;}
static void out8(void*v,uint16_t a,uint8_t x){
 struct model*m=v;m->writes++;
 if(a==0x80d3){if(x==4){m->unblank++;CHECK(m->starts==19);}else{CHECK(x==5);m->blank++;}}
 if(a==0xc008)m->reg=x;
 if(a==0xc002){CHECK(x==0x1a&&m->blank&&!m->unblank);CHECK(m->starts<32);m->enc_reg[m->starts]=m->reg;m->enc_value[m->starts]=m->data;m->starts++;}
}
static void delay(void*v,unsigned us){struct model*m=v;m->delay+=us;CHECK(m->delay<7000000);}
static struct xwn_hd_io io(struct model*m){struct xwn_hd_io a={m,r32,w32,r8,w8,in16,in8,out16,out8,delay};return a;}
static const struct xwn_hd_request valid={1,67108864,57671680,9437184,316160,0,3,2};
static int apply(struct model*m,struct xwn_hd_state*s){struct xwn_hd_io a=io(m);return xwn_hd_apply(&a,&valid,s);}
int main(void){
 struct model m={0};struct xwn_hd_state s;struct xwn_hd_profile p;unsigned i,j;
 CHECK(apply(&m,&s)==1&&s.stage==5&&!s.error&&m.unblank==1&&m.blank==1);
 CHECK(s.smb_completed==19&&s.smb_attempts==19&&s.vblank_polls>=6&&s.vpll==0x3c20d&&s.pcrtc==3);
 CHECK(xwn_hd_get_profile(1,&p));
 for(i=0;i<28;i++)CHECK(r32(&m,xwn_hd_mmio_offsets[i])==p.mmio[i]);
 for(i=0;i<35;i++)CHECK(m.crt[xwn_hd_crtc_indices[i]]==p.crtc[i]);
 CHECK(r32(&m,0x600800)==valid.fb);
 CHECK(m.enc_reg[0]==0xba&&m.enc_value[0]==0x80&&m.enc_reg[1]==0xba&&m.enc_value[1]==0x3f);
 CHECK(m.enc_reg[2]==0x6c&&m.enc_value[2]==0x46&&m.enc_reg[3]==0x6c&&m.enc_value[3]==0xc6);
 for(i=0;i<13;i++)CHECK(m.enc_reg[i+4]==xwn_hd_encoder_indices[i]&&m.enc_value[i+4]==p.encoder[i]);
 CHECK(m.enc_reg[17]==0x6c&&m.enc_value[17]==0xc6&&m.enc_reg[18]==0xba&&m.enc_value[18]==0x28);
 for(j=0;j<2;j++)for(i=1;i<=19;i++){
  memset(&m,0,sizeof m);m.fail_at=i;m.combined=j;
  CHECK(apply(&m,&s)==-1&&s.error==13&&s.stage==255&&s.mutated);
  CHECK(m.starts==i&&s.smb_completed==i-1&&!m.unblank&&m.blank==2);
 }
 for(i=0;i<8;i++){
  memset(&m,0,sizeof m);
  if(i==0)m.busy=1;
  if(i==1)m.timeout=1;
  if(i==2)m.sync_stuck=1;
  if(i==3)m.edge_stuck=1;
  if(i==4)m.bad_geometry=1;
  if(i==5)m.bad_pitch=0x13;
  if(i==6)m.bad_pitch=0x28;
  if(i==7)m.bad_pitch=0x19;
  CHECK(apply(&m,&s)==-1&&s.stage==255&&!m.unblank&&m.blank==2);
  CHECK(s.error==(i==0?11:i==1?12:i==2?21:i==3?22:i==4?23:24));
 }
 for(i=0;i<9;i++){
  struct xwn_hd_request r=valid;struct xwn_hd_io a;
  memset(&m,0,sizeof m);a=io(&m);
  switch(i){case 0:r.mode=2;break;case 1:r.ram++;break;case 2:r.fb++;break;case 3:r.reserved++;break;case 4:r.hidden++;break;case 5:r.encoder=1;break;case 6:r.cable=1;break;case 7:r.video_flags=0;break;case 8:a.delay=0;break;}
  CHECK(xwn_hd_apply(&a,&r,&s)==0&&!s.mutated&&!m.writes&&!m.reads);
 }
 CHECK(xwn_hd_apply(0,&valid,&s)==0);CHECK(xwn_hd_apply(0,&valid,0)==0);
 printf("PASS %u\n",checks);return 0;
}
