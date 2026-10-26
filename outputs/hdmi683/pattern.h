/* SPDX-License-Identifier: MIT */
#ifndef XWN_VIDEO_BASELINE_PATTERN_H
#define XWN_VIDEO_BASELINE_PATTERN_H
#include <stdint.h>
/* White border; upper RGB/CMY/white/black bars; lower horizontal,
 * vertical and checkerboard 8-pixel cells. No animation or GPU drawing. */
static uint32_t baseline_pixel(unsigned x, unsigned y, unsigned w, unsigned h)
{
    static const uint32_t colors[8] = {
        0xff0000, 0x00ff00, 0x0000ff, 0x00ffff,
        0xff00ff, 0xffff00, 0xffffff, 0
    };
    if (!w || !h || x >= w || y >= h) return 0;
    if (x < 4 || y < 4 || x >= w - 4 || y >= h - 4) return 0xffffff;
    if (y < h / 2) return colors[(x * 8) / w];
    unsigned bit = x < w / 3 ? (y / 8) :
                   x < 2 * w / 3 ? (x / 8) : ((x / 8) ^ (y / 8));
    return (bit & 1) ? 0xffffff : 0;
}
#endif
