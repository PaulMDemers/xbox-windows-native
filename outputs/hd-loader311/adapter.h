/* SPDX-License-Identifier: GPL-2.0-or-later */
#ifndef XWN_HD_ADAPTER311_H
#define XWN_HD_ADAPTER311_H
#include "profile.h"
struct xwn_hd_io {
 void *opaque;
 uint32_t (*r32)(void *,uint32_t);
 void (*w32)(void *,uint32_t,uint32_t);
 uint8_t (*r8)(void *,uint32_t);
 void (*w8)(void *,uint32_t,uint8_t);
 uint16_t (*in16)(void *,uint16_t);
 uint8_t (*in8)(void *,uint16_t);
 void (*out16)(void *,uint16_t,uint16_t);
 void (*out8)(void *,uint16_t,uint8_t);
 void (*delay)(void *,unsigned);
};
struct xwn_hd_request {uint32_t mode,ram,fb,reserved,hidden,encoder,cable,video_flags;};
struct xwn_hd_state {uint32_t stage,error,mutated,smb_attempts,smb_completed,sync_polls,vblank_polls,vpll,pcrtc;};
/* 1 success; 0 unsupported BEFORE adapter writes; -1 partial failure, no resume. */
int xwn_hd_apply(const struct xwn_hd_io *,const struct xwn_hd_request *,volatile struct xwn_hd_state *);
/* One bounded write, no retry after a potentially accepted transaction. */
int xwn_hd_smb_write(const struct xwn_hd_io *,uint8_t,uint8_t,uint8_t);
#endif
