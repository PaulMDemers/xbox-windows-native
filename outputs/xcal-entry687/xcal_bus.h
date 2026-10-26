/* SPDX-License-Identifier: GPL-2.0-or-later
 * Experimental MCPX SMBus block protocol derived from Cromwell i2cio.c.
 * No native I/O binding is provided: host prototype, not a shipping driver.
 */
#ifndef XWN_XCAL_BUS681_H
#define XWN_XCAL_BUS681_H
#include <stdint.h>
struct xcal_bus {
    void *ctx;
    uint8_t (*r8)(void *, unsigned);
    uint16_t (*r16)(void *, unsigned);
    void (*w8)(void *, unsigned, uint8_t);
    void (*w16)(void *, unsigned, uint16_t);
    unsigned poll_limit;
};
enum xcal_result {
    XCAL_OK=0, XCAL_ARGUMENT, XCAL_BUSY, XCAL_DIRTY_STATUS,
    XCAL_TIMEOUT, XCAL_BUS_ERROR, XCAL_BLOCK_LENGTH
};
/* Reads leave output unchanged on failure. Offsets are relative to SMBus base.
 * Idle entry must have no pending status bits; never clear preexisting status.
 * Acknowledge only observed terminal bits from this transaction. No retry.
 * Poll budget bounds callback calls; it is NOT a calibrated time deadline.
 */
int xcal_read32(const struct xcal_bus *, uint8_t reg, uint32_t *value);
int xcal_write32(const struct xcal_bus *, uint8_t reg, uint32_t value);
#endif
