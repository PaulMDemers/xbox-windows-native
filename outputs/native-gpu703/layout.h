/* SPDX-License-Identifier: MIT */
#ifndef XWN_LAYOUT703_H
#define XWN_LAYOUT703_H
#include <stdint.h>
struct fb703 {uint32_t address,bytes,allocation,pitch,width,height,depth,scanout;};
int framebuffer_admit703(const struct fb703 *);
int handoff_overlap703(uint32_t address,uint32_t bytes);
uint32_t checkpoint_pixel703(unsigned x,unsigned y);
#endif
