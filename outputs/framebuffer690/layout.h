/* SPDX-License-Identifier: MIT */
#ifndef XWN_LAYOUT690_H
#define XWN_LAYOUT690_H
#include <stdint.h>
struct fb690 {uint32_t address,bytes,allocation,pitch,width,height,depth,scanout;};
int framebuffer_admit690(const struct fb690 *);
int handoff_overlap690(uint32_t address,uint32_t bytes);
uint32_t checkpoint_pixel690(unsigned x,unsigned y);
#endif
