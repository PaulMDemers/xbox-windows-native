/* SPDX-License-Identifier: MIT */
#ifndef XWN_LAYOUT695_H
#define XWN_LAYOUT695_H
#include <stdint.h>
struct fb695 {uint32_t address,bytes,allocation,pitch,width,height,depth,scanout;};
int framebuffer_admit695(const struct fb695 *);
int handoff_overlap695(uint32_t address,uint32_t bytes);
uint32_t checkpoint_pixel695(unsigned x,unsigned y);
#endif
