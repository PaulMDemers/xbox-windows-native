/* Byte oracle/redzones for both compiled row-copy modes and alias fallback.
 * SPDX-License-Identifier: GPL-2.0-or-later */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "row_store.h"
static unsigned checks,seed=0x1840115;
#define CHECK(x) do {++checks;if(!(x)){fprintf(stderr,"failure line%d seed%x\n",__LINE__,seed);exit(1);}}while(0)
static unsigned next(void){seed=seed*1664525U+1013904223U;return seed;}
int main(void)
{
    unsigned i,j,n,so,to,enabled,result;unsigned char *s,*d,*expected,*saved;
    s=malloc(16448);d=malloc(16448);expected=malloc(16448);saved=malloc(16448);
    CHECK(s&&d&&expected&&saved);
    CHECK(!XwEligible((XW_PTR)-8,0x10000,16));
    CHECK(!XwEligible(0x10000,(XW_PTR)-8,16));
    CHECK(!XwEligible(0x10000,0x10010,32));
    CHECK(XwEligible(0x10000,0x10020,32));
    for(i=0;i<12000;i++) {
        n=i<8200?i:next()%8193;so=64+next()%8;to=64+next()%8;enabled=i&1;
        for(j=0;j<16448;j++)s[j]=(unsigned char)(j*37+i);
        memset(d,0x5a,16448);memcpy(expected,d,16448);memcpy(saved,s,16448);
        memmove(expected+to,s+so,n);
        result=XwCopyRow(d+to,s+so,n,enabled);
        CHECK(result==(unsigned)(enabled&&n&&!(n&3)&&!(((XW_PTR)(d+to)|(XW_PTR)(s+so))&3)));
        CHECK(memcmp(expected,d,16448)==0);CHECK(memcmp(saved,s,16448)==0);
    }
    for(i=0;i<4000;i++) {
        n=next()%4097;so=64+next()%4097;to=64+next()%4097;
        for(j=0;j<16448;j++)d[j]=(unsigned char)(j*29+i);
        memcpy(expected,d,16448);memmove(expected+to,expected+so,n);
        result=XwCopyRow(d+to,d+so,n,1);
        CHECK(result==(unsigned)XwEligible((XW_PTR)(d+to),(XW_PTR)(d+so),n));
        CHECK(memcmp(expected,d,16448)==0);
    }
    free(s);free(d);free(expected);free(saved);
    printf("PASS %u checks;16000 byte-oracle cases;both modes,unaligned/tails,alias,wrap,redzones\n",checks);
    return 0;
}
