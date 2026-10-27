/* SPDX-License-Identifier: MIT */
#ifndef XWN_LAYOUT693_H
#define XWN_LAYOUT693_H
#include <stdint.h>
struct fb693 {uint32_t address,bytes,allocation,pitch,width,height,depth,scanout;};
int framebuffer_admit693(const struct fb693 *);
int handoff_overlap693(uint32_t address,uint32_t bytes);
uint32_t checkpoint_pixel693(unsigned x,unsigned y);
#endif
