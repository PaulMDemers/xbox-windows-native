/* SPDX-License-Identifier: MIT */
#ifndef XWN686_PROBE_H
#define XWN686_PROBE_H
#include <stdint.h>
static const uint8_t encoder_addresses[3]={0xe0,0x8a,0xd4};
struct encoder_response { int32_t status; uint32_t value; };
/* Names express address responses, not a unique vendor/chip ID. */
static const char *response_label(const struct encoder_response r[3])
{
    unsigned mask=0;
    for(unsigned i=0;i<3;++i) if(r[i].status==0) mask|=1u<<i;
    switch(mask) {
        case 0:return "unidentified";
        case 1:return "xcalibur-address-response";
        case 2:return "conexant-address-response";
        case 4:return "focus-address-response";
        default:return "multiple-address-responses";
    }
}
#endif
