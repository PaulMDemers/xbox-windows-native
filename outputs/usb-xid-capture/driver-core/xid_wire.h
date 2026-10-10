/* SPDX-License-Identifier: MIT */
#ifndef XWN_XID_WIRE_H
#define XWN_XID_WIRE_H
#include <stdint.h>
typedef struct xwn_xid_sample {
    uint16_t digital;
    uint8_t pressure[8]; /* A B X Y Black White LT RT; interpretation needs device testing. */
    int16_t sticks[4];  /* LX LY RX RY, little-endian signed wire fields. */
} xwn_xid_sample;
enum xwn_xid_decode_result {
    XWN_XID_INVALID = -1,
    XWN_XID_NO_DATA = 0,
    XWN_XID_SAMPLE = 1
};
/* Call only for a successful USB completion, using its actual returned length.
 * Output is untouched on NO_DATA or INVALID. No allocation, I/O or global state.
 */
int xwn_xid_decode(const uint8_t *bytes, uint32_t length, xwn_xid_sample *output);
#endif
