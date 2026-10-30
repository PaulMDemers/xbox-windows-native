/* SPDX-License-Identifier: GPL-2.0-or-later
 * Experimental host-only successor to681; not installed in a launcher.
 */
#ifndef XWN_XCAL_BUS698_H
#define XWN_XCAL_BUS698_H
#include <stdint.h>
struct xcal_bus {
    void *ctx;
    uint8_t (*r8)(void *, unsigned);
    uint16_t (*r16)(void *, unsigned);
    void (*w8)(void *, unsigned, uint8_t);
    void (*w16)(void *, unsigned, uint16_t);
    unsigned poll_limit;
};
struct xcal_trace { uint16_t entry,last,final,length; unsigned polls,ack; };
enum xcal_result { XCAL_OK, XCAL_ARGUMENT, XCAL_BUSY, XCAL_DIRTY_STATUS,
    XCAL_TIMEOUT, XCAL_BUS_ERROR, XCAL_BLOCK_LENGTH, XCAL_FINAL_STATUS };
/* Caller owns bus exclusively with IF clear; no interrupt-state changes here.
 * A read publishes data only after success and clean final known flags.
 * Poll budget limits calls, not wall time. Unknown status bits are retained.
 */
int xcal_read32(const struct xcal_bus *,uint8_t,uint32_t *,struct xcal_trace *);
int xcal_write32(const struct xcal_bus *,uint8_t,uint32_t,struct xcal_trace *);
#endif
