/* SPDX-License-Identifier: MIT */
#ifndef XWN_CAPTURE722_H
#define XWN_CAPTURE722_H
#include <stdint.h>
#define MMIO722 30
#define CRTC722 31
extern const uint32_t mmio722[MMIO722];
extern const uint8_t crtc722[CRTC722];
struct capture722 {
 uint32_t flags_entry, flags_critical, flags_restored, cr0, cr3, cr4;
 uint32_t selectors[3], selectors_after[3], selectors_restored;
 uint32_t mmio[MMIO722], crtc[CRTC722], seq[5], graphics[9];
};
void capture722(struct capture722 *);
int layout722(uint32_t address,uint32_t allocation,uint32_t scanout,
              uint32_t width,uint32_t height,uint32_t pitch);
uint32_t pixel722(uint32_t x,uint32_t y,uint32_t w,uint32_t h,uint32_t color);
#endif
