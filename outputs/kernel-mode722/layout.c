/* SPDX-License-Identifier: MIT */
#include "capture.h"
int layout722(uint32_t a,uint32_t n,uint32_t scan,uint32_t w,uint32_t h,uint32_t pitch)
{
 if(!((w==1280 && h==720)||(w==720 && h==480)))return 0;
 uint32_t bytes=w*h*4;
 return pitch==w*4 && n>=bytes && a<0x4000000 && a%4096==0 &&
        n<=0x4000000-a && scan==a;
}
uint32_t pixel722(uint32_t x,uint32_t y,uint32_t w,uint32_t h,uint32_t color)
{
 if(!((w==1280 && h==720)||(w==720 && h==480)) || x>=w || y>=h)return 0;
 if(x<8 || y<8 || x>=w-8 || y>=h-8)return 0xffffff;
 if(y<64)return color;
 if(y>=h-80 && y<h-16 && x>=w/4 && x<3*w/4)
  return ((x/8+y/8)&1)?0xffffff:0;
 return y<h/2?(x<w/2?0xff0000:0x00ff00):(x<w/2?0x0000ff:0xffffff);
}
