/* SPDX-License-Identifier: GPL-2.0-or-later */
#ifndef XWN_GEOMETRY702_H
#define XWN_GEOMETRY702_H
#include <stdint.h>
/* This descriptor must be produced by the checked kernel allocator/page walk.
 * Booleans are caller obligations, not independent ownership verification.
 * This host-only component has NO output blank/enable or encoder binding. */
struct request702 {
 uint32_t ram,base,allocation,checked_bytes,contiguous,alias_checked;
 uint32_t width,height,pitch,depth,blank_confirmed;
};
struct result702 {uint32_t phase,error,width,height,pitch,format,start,interlace;};
enum {G702_OK=1,G702_ARGUMENT=2,G702_LAYOUT=3,G702_IF=4,
      G702_BASELINE=5,G702_READBACK=6};
int bounds702(const struct request702 *);
int geometry702(const struct request702 *,volatile uint8_t *,struct result702 *);
#endif
