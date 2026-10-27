/* SPDX-License-Identifier: MIT
 * Kernel framebuffer validation only. No mapping/ownership transfer implied.
 */
#include "layout.h"
int framebuffer_admit701(const struct fb701 *f)
{
    if(!f || f->width!=1280 || f->height!=720 || f->depth!=32 ||
       f->pitch!=5120 || f->bytes!=3686400 || f->allocation<f->bytes ||
       f->address%4096 || f->address>=0x04000000 ||
       f->bytes>0x04000000-f->address || f->scanout!=f->address)return 0;
    return 1;
}
int handoff_overlap701(uint32_t a,uint32_t n)
{
    /* Conservative diagnostic reservations: GDT, IDT clear, firmware+BSS+stack.
     * This does not allocate or reserve those regions on the live kernel. */
    if(!n || a>=0x04000000 || n>0x04000000-a)return -1;
    const uint32_t regions[][2]={{0xa0000,0x1000},{0xb0000,0x5000},{0x02600000,0x00200000}};
    for(unsigned i=0;i<3;++i)if(a<regions[i][0]+regions[i][1] && regions[i][0]<a+n)return 1;
    return 0;
}
uint32_t checkpoint_pixel701(unsigned x,unsigned y)
{
    if(x>=1280 || y>=720)return 0;
    if(x<8 || x>=1272 || y<8 || y>=713)return 0xffffff;
    if(y<80)return 0x2080ff;
    /* Four unmistakable reference quadrants, not a native video test. */
    if(x<640)return y<400?0xff0000:0x0000ff;
    return y<400?0x00ff00:0xffffff;
}
