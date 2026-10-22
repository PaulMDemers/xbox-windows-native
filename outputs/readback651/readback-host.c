/* SPDX-License-Identifier: GPL-2.0-or-later */
#include "readback651.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static struct xwn_hd_profile profile;
static unsigned flags_value,flags_calls,flip_flags;
static unsigned flags(void){return flags_value^((flags_calls++ && flip_flags)?0x200:0);}
struct model {unsigned index,r32,r8,w8,bad_restore;};
static uint32_t r32(void *v,uint32_t a) {
 struct model*m=v;unsigned i;assert(m->r32<18 && a==mm651_offsets[m->r32]);m->r32++;
 for(i=0;i<28;i++)if(xwn_hd_mmio_offsets[i]==a)return profile.mmio[i];
 assert(a==0x680508 || a==0x600804 || a==0x6806a0);return 0x12345678;
}
static uint8_t r8(void *v,uint32_t a) {
 struct model*m=v;unsigned i;m->r8++;
 if(a==0x6013d4)return (uint8_t)(m->index^((m->r8==25 && m->bad_restore)?1:0));
 assert(a==0x6013d5);
 for(i=0;i<35;i++)if(xwn_hd_crtc_indices[i]==m->index)return profile.crtc[i];
 assert(0);return 0;
}
static void w8(void *v,uint32_t a,uint8_t x){struct model*m=v;assert(a==0x6013d4);m->index=x;m->w8++;}
int main(void) {
 unsigned mode,index,i,b,checks=0;
 for(mode=1;mode<=3;mode+=2) {
  assert(xwn_hd_get_profile(mode,&profile));
  for(index=0;index<256;index++) {
   struct model m={0};struct xwn_hd_io io={0};struct readback651 s;
   io.opaque=&m;io.r32=r32;io.r8=r8;io.w8=w8;m.index=index;
   flags_value=0x46;flags_calls=flip_flags=0;capture651(&io,&s,flags);
   assert(s.captured && s.cr_captured && m.index==index && s.index_before==index && s.index_after==index);
   assert(m.r32==18 && m.r8==25 && m.w8==24 && flags_calls==2);
   assert(s.flags_before==0x46 && s.flags_after==0x46 && match651(&s,&profile)==0);checks++;
  }
  {
   struct model m={0};struct xwn_hd_io io={0};struct readback651 s,changed;
   io.opaque=&m;io.r32=r32;io.r8=r8;io.w8=w8;
   flags_value=0x246;flags_calls=flip_flags=0;capture651(&io,&s,flags);
   assert(s.captured && !s.cr_captured && !m.r8 && !m.w8 && flags_calls==1 && match651(&s,&profile)==4);checks++;
   memset(&m,0,sizeof m);flags_value=0x46;flags_calls=0;flip_flags=1;capture651(&io,&s,flags);
   assert(s.captured && !s.cr_captured && match651(&s,&profile)==4);checks++;
   memset(&m,0,sizeof m);flags_calls=flip_flags=0;m.bad_restore=1;capture651(&io,&s,flags);
   assert(s.captured && !s.cr_captured && match651(&s,&profile)==4);checks++;
   memset(&m,0,sizeof m);flags_calls=flip_flags=0;capture651(&io,&s,flags);
   for(i=0;i<23;i++)for(b=0;b<8;b++) {
    unsigned mask=cr651_indices[i]==0x19?0xe0:cr651_indices[i]==0x2d?1:255;
    changed=s;changed.cr[i]^=1u<<b;
    assert(match651(&changed,&profile)==((mask&(1u<<b))?1u:0u));checks++;
   }
   for(i=0;i<18;i++)for(b=0;b<32;b++) {
    changed=s;changed.mm[i]^=1u<<b;
    assert(match651(&changed,&profile)==(i<15?2u:0u));checks++;
   }
   changed=s;changed.cr[0]^=1;changed.mm[0]^=1;assert(match651(&changed,&profile)==3);checks++;
   changed=s;changed.captured=0;assert(match651(&changed,&profile)==4);checks++;
  }
 }
 printf("PASS %u capture/mask cases; all selector bytes, IF skip, restoration failures and every stored bit\n",checks);return 0;
}
