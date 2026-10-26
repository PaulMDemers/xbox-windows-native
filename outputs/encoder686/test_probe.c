/* SPDX-License-Identifier: MIT */
#include <assert.h>
#include <string.h>
#include <stdio.h>
#include "probe.h"
int main(void)
{
    const char *want[]={"unidentified","xcalibur-address-response","conexant-address-response",
      "multiple-address-responses","focus-address-response","multiple-address-responses",
      "multiple-address-responses","multiple-address-responses"};
    assert(encoder_addresses[0]==0xe0 && encoder_addresses[1]==0x8a && encoder_addresses[2]==0xd4);
    for(unsigned m=0;m<8;++m) {
        struct encoder_response r[3];
        for(unsigned i=0;i<3;++i) r[i]=(struct encoder_response){m&(1u<<i)?0:(int32_t)0xc0000001,0xdeadbeef};
        assert(!strcmp(response_label(r),want[m]));
    }
    puts("PASS all8 response combinations; no fallback Xcalibur inference");
}
