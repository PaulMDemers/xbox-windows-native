/* SPDX-License-Identifier: MIT */
#ifndef XWN_LAYOUT691_H
#define XWN_LAYOUT691_H
#include <stdint.h>
struct fb691 {uint32_t address,bytes,allocation,pitch,width,height,depth,scanout;};
int framebuffer_admit691(const struct fb691 *);
int handoff_overlap691(uint32_t address,uint32_t bytes);
uint32_t checkpoint_pixel691(unsigned x,unsigned y);
#endif
