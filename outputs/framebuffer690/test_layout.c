/* SPDX-License-Identifier: MIT */
#include <assert.h>
#include <stdio.h>
#include "layout.h"
int main(void){
 struct fb690 f={0x03000000,3686400,3686400,5120,1280,720,32,0x03000000}, g;
 assert(framebuffer_admit690(&f));assert(!framebuffer_admit690(0));
 for(unsigned i=0;i<8;i++){
  g=f; switch(i){case 0:g.address++;break;case 1:g.bytes--;break;
  case 2:g.allocation--;break;case 3:g.pitch++;break;case 4:g.width++;break;
  case 5:g.height++;break;case 6:g.depth=16;break;case 7:g.scanout++;break;}
  assert(!framebuffer_admit690(&g));
 }
 g=f;g.address=0x04000000-g.bytes;g.scanout=g.address;assert(framebuffer_admit690(&g));
 g.address+=4096;g.scanout=g.address;assert(!framebuffer_admit690(&g));
 g.address=0xfffff000;g.scanout=g.address;assert(!framebuffer_admit690(&g));
 const unsigned r[][2]={{0xa0000,0xa1000},{0xb0000,0xb5000},{0x02600000,0x02800000}};
 for(unsigned i=0;i<3;i++){
  assert(handoff_overlap690(r[i][0]-1,1)==0);
  assert(handoff_overlap690(r[i][0]-1,2)==1);
  assert(handoff_overlap690(r[i][1]-1,1)==1);
  assert(handoff_overlap690(r[i][1],1)==0);
 }
 assert(handoff_overlap690(0,0)==-1);assert(handoff_overlap690(0xffffffff,2)==-1);
 assert(handoff_overlap690(0x03ffffff,2)==-1);
 assert(handoff_overlap690(0x03ffffff,1)==0);
 unsigned counts[5]={0};
 for(unsigned y=0;y<720;y++)for(unsigned x=0;x<1280;x++){
  unsigned c=checkpoint_pixel690(x,y);
  if(x<8 || x>=1272 || y<8 || y>=712){assert(c==0xffffff);counts[0]++;}
  else if(y<80){assert(c==0x2080ff);counts[1]++;}
  else if(y<400){assert(c==(x<640?0xff0000:0x00ff00));counts[2]++;}
  else {assert(c==(x<640?0x0000ff:0xffffff));counts[3]++;}
 }
 assert(checkpoint_pixel690(1280,0)==0 && checkpoint_pixel690(0,720)==0);
 assert(counts[0]+counts[1]+counts[2]+counts[3]==921600);
 puts("PASS allocation bounds, reservation edge intersections, all 921600 pattern pixels");return 0;
}
