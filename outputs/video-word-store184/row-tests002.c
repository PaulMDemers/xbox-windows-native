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
    unsigned i,j,n,so,to,enabled,result,at,fast=0,blocks=0,tails=0,small=0;unsigned char *s,*d,*expected,*saved;
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
    {
        const unsigned lengths[]={0,4,8,12,28,32,36,60,64,68,124,128,256,1024,4096,7680,8192};
        /* LCG low bits correlate adjacent offsets; explicit Cartesian offsets
         * and both modes ensure fast block/tail cases cannot be missed. */
        for(at=0;at<sizeof(lengths)/sizeof(lengths[0]);at++)
        for(enabled=0;enabled<2;enabled++)for(so=64;so<68;so++)for(to=64;to<68;to++) {
            n=lengths[at];
            for(j=0;j<16448;j++)s[j]=(unsigned char)(j*37+at);
            memset(d,0x5a,16448);memcpy(expected,d,16448);memcpy(saved,s,16448);
            memmove(expected+to,s+so,n);result=XwCopyRow(d+to,s+so,n,enabled);
            CHECK(result==(unsigned)(enabled&&n&&so==64&&to==64));
            CHECK(memcmp(expected,d,16448)==0);CHECK(memcmp(saved,s,16448)==0);
            if(result){++fast;if(n>=32)++blocks;else ++small;if(n%32)++tails;}
        }
        CHECK(fast==16);CHECK(blocks==12);CHECK(small==4);CHECK(tails==8);
    }
    free(s);free(d);free(expected);free(saved);
    printf("PASS %u checks;16544 byte-oracle cases;explicit16fast/12block/8tail/4small;both modes,unaligned/tails,alias,wrap,redzones\n",checks);
    return 0;
}
