/* SPDX-License-Identifier: MIT */
#include "probe.h"
struct request704 {
 uint32_t ram,base,allocation,checked_bytes,contiguous,alias_checked;
 uint32_t width,height,pitch,depth,confirmed_xcalibur,cable_byte,flags;
 uint32_t timer_hz,tv_path_confirmed;
};
struct result704 {struct result725 prefix;uint32_t first_actual,first_expected;};
int bounds704(const struct request704 *);
int native_transaction704(const struct request704 *,volatile uint8_t *,volatile uint32_t *,struct result704 *);
