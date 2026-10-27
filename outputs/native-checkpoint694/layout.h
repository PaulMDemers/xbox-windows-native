/* SPDX-License-Identifier: MIT */
#ifndef XWN_LAYOUT694_H
#define XWN_LAYOUT694_H
#include <stdint.h>
struct fb694 {uint32_t address,bytes,allocation,pitch,width,height,depth,scanout;};
int framebuffer_admit694(const struct fb694 *);
int handoff_overlap694(uint32_t address,uint32_t bytes);
uint32_t checkpoint_pixel694(unsigned x,unsigned y);
#endif
