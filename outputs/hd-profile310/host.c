#include "profile.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <limits.h>
int main(void) {
 unsigned checks=0,m,i;struct xwn_hd_profile p,old;
 const uint32_t normal[4]={64u<<20,55u<<20,9u<<20,316160};
 const uint32_t bad[]={0,1,UINT32_MAX,128u<<20,4u<<20,8u<<20,60u<<20,316159,316161};
 for(m=1;m<=2;m++) {
  assert(xwn_hd_get_profile(m,&p));checks++;
  assert(p.stride==p.width*4 && p.visible_bytes==p.stride*p.height);checks++;
  assert(xwn_hd_layout_valid(m,normal[0],normal[1],normal[2],normal[3]));checks++;
  for(i=0;i<4;i++)for(unsigned j=0;j<sizeof(bad)/sizeof(bad[0]);j++) {
   uint32_t v[4];memcpy(v,normal,sizeof(v));v[i]=bad[j];
   if(v[i]==normal[i])continue;
   assert(!xwn_hd_layout_valid(m,v[0],v[1],v[2],v[3]));checks++;
  }
  printf("PROFILE %u %u %u %u %u %u\n",m,p.width,p.height,p.stride,p.visible_bytes,p.interlaced);
  for(i=0;i<35;i++)printf("CR %u %x %x\n",m,xwn_hd_crtc_indices[i],p.crtc[i]);
  for(i=0;i<28;i++)printf("MM %u %x %x\n",m,xwn_hd_mmio_offsets[i],p.mmio[i]);
  for(i=0;i<14;i++)printf("EN %u %x %x\n",m,xwn_hd_encoder_indices[i],p.encoder[i]);
 }
 memset(&p,0xa5,sizeof(p));old=p;
 for(m=0;m<8;m++)if(m!=1 && m!=2) {
  assert(!xwn_hd_get_profile(m,&p) && !memcmp(&p,&old,sizeof(p)));checks++;
  assert(!xwn_hd_layout_valid(m,normal[0],normal[1],normal[2],normal[3]));checks++;
 }
 assert(!xwn_hd_get_profile(UINT_MAX,&p) && !memcmp(&p,&old,sizeof(p)));checks++;
 assert(!xwn_hd_get_profile(1,NULL));checks++;
 printf("CHECKS %u\n",checks);return 0;
}
