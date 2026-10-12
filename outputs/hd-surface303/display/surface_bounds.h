/* SPDX-License-Identifier: GPL-2.0-or-later */
#ifndef XWN_SURFACE_BOUNDS_H
#define XWN_SURFACE_BOUNDS_H
/* Returned lengths must cover the image; bounded geometry prevents overflow. */
static inline unsigned int
XwnSurfaceBytes(unsigned int Width, unsigned int Height, unsigned int Stride,
                unsigned int Bits, unsigned int FrameBytes, unsigned int RamBytes)
{
    unsigned int Bytes;
    if (!Width || Width > 1920u || !Height || Height > 1080u || Bits != 32u ||
        Stride != Width * 4u || !RamBytes || RamBytes > 0x00900000u ||
        FrameBytes > RamBytes)
        return 0;
    Bytes = Height * Stride;
    return Bytes <= FrameBytes ? Bytes : 0;
}
#endif
