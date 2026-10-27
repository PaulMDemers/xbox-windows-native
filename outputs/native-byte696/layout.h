/* SPDX-License-Identifier: MIT */
#ifndef XWN_LAYOUT696_H
#define XWN_LAYOUT696_H
#include <stdint.h>
struct fb696 {uint32_t address,bytes,allocation,pitch,width,height,depth,scanout;};
int framebuffer_admit696(const struct fb696 *);
int handoff_overlap696(uint32_t address,uint32_t bytes);
uint32_t checkpoint_pixel696(unsigned x,unsigned y);
#endif
