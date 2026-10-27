/* SPDX-License-Identifier: MIT */
#ifndef XWN_LAYOUT697_H
#define XWN_LAYOUT697_H
#include <stdint.h>
struct fb697 {uint32_t address,bytes,allocation,pitch,width,height,depth,scanout;};
int framebuffer_admit697(const struct fb697 *);
int handoff_overlap697(uint32_t address,uint32_t bytes);
uint32_t checkpoint_pixel697(unsigned x,unsigned y);
#endif
