/* SPDX-License-Identifier: GPL-2.0-or-later */
#ifndef XWN_BOOT_LAYOUT_H
#define XWN_BOOT_LAYOUT_H
/* The mapping remains four MiB. This bound limits CPU boot-video writes;
 * it is not an allocator/GPU capability or firmware-context release. */
#define XWN_BOOT_RESERVED_BYTES 0x00400000u
#define XWN_BOOT_PROTECTED_TAIL 0x00015000u
typedef struct _XWN_BOOT_LAYOUT {
    ULONG WritableBytes, HiddenOffset, VisibleBytes;
} XWN_BOOT_LAYOUT;
static BOOLEAN XwnBootLayout(ULONG Physical, ULONG Width, ULONG Height,
                            ULONG BackBytes, XWN_BOOT_LAYOUT *Out)
{
    XWN_BOOT_LAYOUT Value;
    if (!Out || (Physical != 0x03c00000u && Physical != 0x07c00000u) ||
        Width < 640u || Width > 1920u || Height < 480u || Height > 1080u ||
        !BackBytes || BackBytes >= XWN_BOOT_RESERVED_BYTES-XWN_BOOT_PROTECTED_TAIL)
        return FALSE;
    Value.WritableBytes = XWN_BOOT_RESERVED_BYTES-XWN_BOOT_PROTECTED_TAIL;
    Value.HiddenOffset = Value.WritableBytes-BackBytes;
    /* Width is bounded before multiplying; divide before height multiplication. */
    if (Height > Value.HiddenOffset/(Width*4u)) return FALSE;
    Value.VisibleBytes = Width*4u*Height;
    *Out = Value;
    return TRUE;
}
#endif
