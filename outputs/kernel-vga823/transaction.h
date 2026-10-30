/* SPDX-License-Identifier: GPL-2.0-or-later */
#ifndef XWN_TRANSACTION704_H
#define XWN_TRANSACTION704_H
#include "xcal_bus.h"
#include "delay_candidate.h"
/* Caller must independently establish page ownership, aliases, CPU context,
 * PCI mappings and timer rate. These fields enforce a contract, not its proof.
 * Only the retained720p allocation is admitted. Never pass703's smaller buffer.
 */
struct request704 {
 uint32_t ram,base,allocation,checked_bytes,contiguous,alias_checked;
 uint32_t width,height,pitch,depth,confirmed_xcalibur,cable_byte,flags;
 uint32_t timer_hz,tv_path_confirmed;
};
struct encoder704 {
 uint32_t attempted,completed,table_completed,delay_completed,phase,error;
 uint32_t reg,is_read,read_value;
 struct xcal_trace bus;
 struct delay_observation delay;
};
struct result704 {
 uint32_t phase,error,blank_readback,enable_requested,pixels_verified;
 uint32_t width,height,pitch,start,format,interlace;
 uint32_t saved_cr11,saved_cr21,preserved[6];
 struct encoder704 encoder;
 struct delay_observation settle;
 uint32_t diagnostic_crtc[30],diagnostic_mm[30];
 uint32_t address_before,address_after;
 uint32_t vga_bank,vga_index,vga_actual,vga_expected;
};
enum { T704_OK=1,T704_ARGUMENT,T704_LAYOUT,T704_IF,T704_BASELINE,
 T704_BLANK,T704_UNLOCK,T704_SETUP,T704_GEOMETRY,T704_ENCODER,
 T704_READBACK,T704_DRAW,T704_SETTLE,T704_ENABLE };
int bounds704(const struct request704 *);
int encoder704(const struct xcal_bus *,uint32_t (*)(void *),void *,struct encoder704 *);
int native_transaction704(const struct request704 *,volatile uint8_t *,volatile uint32_t *,struct result704 *);
#endif
