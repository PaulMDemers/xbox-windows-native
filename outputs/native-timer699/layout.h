/* SPDX-License-Identifier: MIT */
#ifndef XWN_LAYOUT699_H
#define XWN_LAYOUT699_H
#include <stdint.h>
struct fb699 {uint32_t address,bytes,allocation,pitch,width,height,depth,scanout;};
int framebuffer_admit699(const struct fb699 *);
int handoff_overlap699(uint32_t address,uint32_t bytes);
uint32_t checkpoint_pixel699(unsigned x,unsigned y);
#endif
