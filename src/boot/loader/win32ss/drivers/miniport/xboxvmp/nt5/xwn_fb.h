/* SPDX-License-Identifier: GPL-2.0-or-later */
#pragma once
#ifdef XBOX_NT5_HD_RESERVATION
#include <drivers/xbox/xwn_hd_layout.h>
#define XWN_FB_VERSION 2
#define XWN_FB_BYTES XWN_HD_FB_BYTES
#else
#define XWN_FB_VERSION 1
#define XWN_FB_BYTES 0x00400000
#endif
#define XWN_FB_MAX_REFS 0x7fffffff
typedef struct _XWN_FB_VIEW {
    ULONG Size, Version, Address, Physical, ReservedBytes, VisibleBytes;
    ULONG Width, Height, Stride, HiddenOffset, CacheType;
} XWN_FB_VIEW, *PXWN_FB_VIEW;
C_ASSERT(sizeof(XWN_FB_VIEW) == 44);
BOOLEAN NTAPI XwnFbPublish(const XWN_FB_VIEW *View);
NTSTATUS NTAPI XwnFbAcquire(PVOID Owner, PXWN_FB_VIEW View);
NTSTATUS NTAPI XwnFbRelease(PVOID Owner, PVOID Address);
NTSTATUS NTAPI XwnFbReleaseOwner(PVOID Owner);
