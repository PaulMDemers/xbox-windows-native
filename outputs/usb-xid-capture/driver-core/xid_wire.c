/* SPDX-License-Identifier: MIT
 * Original, bounded parser of the observed XID game-controller input format.
 * This module performs no USB transport and is not an installable NT5 driver.
 */
#include "xid_wire.h"
static uint16_t word_le(const uint8_t *p)
{
    return (uint16_t)((uint16_t)p[0] | ((uint16_t)p[1] << 8));
}
int xwn_xid_decode(const uint8_t *bytes, uint32_t length, xwn_xid_sample *output)
{
    xwn_xid_sample sample;
    unsigned i;
    if (length == 0) return XWN_XID_NO_DATA;
    if (length != 20 || !bytes || !output) return XWN_XID_INVALID;
    if (bytes[0] != 0 || bytes[1] != 20) return XWN_XID_INVALID;
    sample.digital = word_le(bytes + 2);
    for (i=0; i<8; i++) sample.pressure[i] = bytes[4+i];
    for (i=0; i<4; i++) {
        uint16_t word = word_le(bytes + 12 + 2*i);
        int32_t signed_word = word >= 0x8000u ? (int32_t)word - 0x10000 : (int32_t)word;
        sample.sticks[i] = (int16_t)signed_word;
    }
    *output = sample;
    return XWN_XID_SAMPLE;
}
