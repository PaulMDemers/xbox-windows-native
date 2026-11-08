/* SPDX-License-Identifier: MIT */
#ifndef XWN_LAYOUT701_H
#define XWN_LAYOUT701_H
#include <stdint.h>
struct fb701 {uint32_t address,bytes,allocation,pitch,width,height,depth,scanout;};
int framebuffer_admit701(const struct fb701 *);
int handoff_overlap701(uint32_t address,uint32_t bytes);
uint32_t checkpoint_pixel701(unsigned x,unsigned y);
#endif
