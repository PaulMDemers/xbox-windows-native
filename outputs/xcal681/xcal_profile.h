/* SPDX-License-Identifier: GPL-2.0-or-later */
#ifndef XWN_XCAL_PROFILE681_H
#define XWN_XCAL_PROFILE681_H
#include "xcal_bus.h"
struct xcal_request {
    unsigned mode, confirmed_xcalibur, cable, flags;
    uint32_t ram, fb, reserved, hidden;
};
struct xcal_progress {
    unsigned attempted, completed, table_completed, delay_completed;
    unsigned phase, error;
};
/* Encoder portion ONLY. Does not program NV2A or admit a Windows handoff.
 * Required mode=3 (480p), cable=3 (Cromwell HDTV), flags&8.
 * confirmed_xcalibur must come from separate evidence, never failed other probes.
 * pause500 must be independently bounded by a future native binding.
 */
int xcal_program_table(const struct xcal_bus *, const struct xcal_request *,
                      int (*pause500)(void *), void *, struct xcal_progress *);
#endif
