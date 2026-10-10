/* SPDX-License-Identifier: MIT */
#ifndef XWN_XID_HID_H
#define XWN_XID_HID_H
#include "xid_wire.h"
#define XWN_REPORT_SIZE 13
extern const uint8_t xwn_report_descriptor[];
extern const unsigned xwn_report_descriptor_size;
void xwn_xid_to_hid(const xwn_xid_sample *sample, uint8_t report[XWN_REPORT_SIZE]);
/* Only the two observed simple descriptor shapes are supported. */
int xwn_xid_config(const uint8_t *bytes, unsigned length, uint8_t *endpoint);
int xwn_xid_descriptor(const uint8_t *bytes, unsigned length);
#endif
