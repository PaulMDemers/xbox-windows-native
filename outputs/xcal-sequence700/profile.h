/* SPDX-License-Identifier: GPL-2.0-or-later
 * Isolated encoder-only successor to681 with698 bus trace and685 bounded delay.
 * No GPU initialization, output enable, Windows admission or physical release.
 */
#ifndef XWN_PROFILE700_H
#define XWN_PROFILE700_H
#include "xcal_bus.h"
#include "delay_candidate.h"
struct xcal_request {
 unsigned mode,confirmed_xcalibur,cable,flags;
 uint32_t ram,fb,reserved,hidden;
 unsigned clock_qualified;
};
struct xcal_progress {
 unsigned attempted,completed,table_completed,delay_completed,phase,error;
 unsigned reg,is_read;
 uint32_t read_value;
 struct xcal_trace bus;
 struct delay_observation delay;
};
int xcal_program700(const struct xcal_bus *,const struct xcal_request *,
 uint32_t (*)(void *),void *,struct xcal_progress *);
#endif
