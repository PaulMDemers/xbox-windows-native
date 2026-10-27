/* SPDX-License-Identifier: GPL-2.0-or-later
 * Protocol reference: XboxDev/cromwell drivers/pci/i2cio.c, pinned in sources.json.
 */
#include "xcal_bus.h"

static int transact(const struct xcal_bus *b, uint8_t reg, uint32_t *value, int read)
{
    if (!b || !value || !b->r8 || !b->r16 || !b->w8 || !b->w16 ||
        !b->poll_limit || b->poll_limit > 1000000) return XCAL_ARGUMENT;
    uint16_t entry = b->r16(b->ctx, 0);
    if (entry & 0x0800) return XCAL_BUSY;
    if (entry & 0x0036) return XCAL_DIRTY_STATUS;
    b->w8(b->ctx, 4, (uint8_t)(0x70 * 2 + read));
    b->w8(b->ctx, 8, reg);
    if (!read) {
        for (unsigned i=0; i<4; ++i) b->w8(b->ctx, 9, (uint8_t)(*value >> (i*8)));
        b->w16(b->ctx, 6, 4);
    }
    b->w8(b->ctx, 2, read ? 0x0d : 0x1d);
    for (unsigned n=0; n<b->poll_limit; ++n) {
        uint8_t status = b->r8(b->ctx, 0) & 0x36;
        if (!status) continue;
        int result = XCAL_OK;
        uint32_t received = 0;
        /* Completion plus an error is failure, unlike the legacy helper. */
        if (status & 0x26) result = XCAL_BUS_ERROR;
        else if (read) {
            if (b->r16(b->ctx, 6) != 4) result = XCAL_BLOCK_LENGTH;
            else for (unsigned i=0; i<4; ++i)
                received |= (uint32_t)b->r8(b->ctx, 9) << (i*8);
        }
        b->w16(b->ctx, 0, status);
        if (result == XCAL_OK && read) *value = received;
        return result;
    }
    /* An incomplete transaction has no acknowledged status; caller must stop.
     * Do not clear pending bits, reset the controller or retry until lucky. */
    return XCAL_TIMEOUT;
}
int xcal_read32(const struct xcal_bus *b, uint8_t r, uint32_t *v)
{ return transact(b,r,v,1); }
int xcal_write32(const struct xcal_bus *b, uint8_t r, uint32_t v)
{ return transact(b,r,&v,0); }
