/* SPDX-License-Identifier: MIT */
#ifndef XWN_LAYOUT692_H
#define XWN_LAYOUT692_H
#include <stdint.h>
struct fb692 {uint32_t address,bytes,allocation,pitch,width,height,depth,scanout;};
int framebuffer_admit692(const struct fb692 *);
int handoff_overlap692(uint32_t address,uint32_t bytes);
uint32_t checkpoint_pixel692(unsigned x,unsigned y);
#endif
