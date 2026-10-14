/* SPDX-License-Identifier: GPL-2.0-or-later */
#ifndef XWN_HD_LAYOUT_H
#define XWN_HD_LAYOUT_H

/* Opt-in retail64 reservation. No timing, cache policy or GPU ownership change. */
#define XWN_HD_RAM_BYTES 0x04000000u
#define XWN_HD_FB_BYTES 0x00900000u
#define XWN_HD_FB_PHYSICAL 0x03700000u
#define XWN_HD_BOOT_BACK_BYTES (640u * (480u + 13u + 1u))
#define XWN_HD_HIDDEN_OFFSET (XWN_HD_FB_BYTES - XWN_HD_BOOT_BACK_BYTES)

static inline int
XwnHdLayoutValid(unsigned int Physical, unsigned int Reserved,
                 unsigned int Width, unsigned int Height,
                 unsigned int Stride, unsigned int Hidden)
{
    if (Physical != XWN_HD_FB_PHYSICAL || Reserved != XWN_HD_FB_BYTES ||
        Width < 640u || Width > 1920u || Height < 480u || Height > 1080u ||
        Stride != Width * 4u || Hidden != XWN_HD_HIDDEN_OFFSET)
        return 0;
    /* Bounded dimensions above prevent overflow; division retains the tail. */
    return Height <= Hidden / Stride;
}

static inline int
XwnHdMapEntryValid(unsigned int Slot, unsigned int Base, unsigned int BaseHigh,
                  unsigned int Length, unsigned int LengthHigh, unsigned int Type)
{
    if (BaseHigh || LengthHigh) return 0;
    if (Slot == 0u)
        return Base == 0u && Length == XWN_HD_FB_PHYSICAL && Type == 1u;
    if (Slot == 1u)
        return Base == XWN_HD_FB_PHYSICAL && Length == XWN_HD_FB_BYTES && Type == 0u;
    return 0;
}
#endif
