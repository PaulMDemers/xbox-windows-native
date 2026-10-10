/* SPDX-License-Identifier: MIT */
#include "correlation.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static uint32_t c[2][INST_WORDS],g[2][INST_WORDS];
static unsigned checks;
#define CHECK(x) do{checks++;assert(x);}while(0)
int main(void)
{
    INST_RESULT r=inst_compare(c[0],c[1],g[0],g[1]);
    CHECK(!r.correlation && r.nonzero_words==0 && r.distinct_blocks==1);
    for(unsigned i=0;i<INST_WORDS;i++)c[0][i]=c[1][i]=g[0][i]=g[1][i]=0x12345678u;
    r=inst_compare(c[0],c[1],g[0],g[1]);CHECK(!r.correlation && r.distinct_blocks==1);
    for(unsigned seed=1;seed<=16;seed++){
        for(unsigned b=0;b<INST_BLOCKS;b++)for(unsigned v=0;v<4;v++){
            uint32_t x=seed*0x10000u+b*17u+v+1u;
            c[0][b*4+v]=c[1][b*4+v]=x;
            /* Independent oracle constructs descending source block labels. */
            unsigned destination=INST_BLOCKS-1-b;
            g[0][destination*4+v]=g[1][destination*4+v]=x;
        }
        r=inst_compare(c[0],c[1],g[0],g[1]);
        CHECK(r.correlation && r.distinct_blocks==INST_BLOCKS && r.nonzero_words==INST_WORDS);
        CHECK(r.forward_mismatches==INST_WORDS && r.reverse16_mismatches==0);
        unsigned pos=seed*277u%INST_WORDS;
        g[0][pos]^=1;r=inst_compare(c[0],c[1],g[0],g[1]);
        CHECK(!r.correlation && !r.gpu_stable && r.reverse16_mismatches==1);
        g[1][pos]^=1;r=inst_compare(c[0],c[1],g[0],g[1]);
        CHECK(!r.correlation && r.gpu_stable && r.reverse16_mismatches==1);
        g[0][pos]^=1;g[1][pos]^=1;c[1][pos]^=1;
        r=inst_compare(c[0],c[1],g[0],g[1]);CHECK(!r.correlation && !r.cpu_stable);
        c[1][pos]^=1;memcpy(g[0],c[0],INST_BYTES);memcpy(g[1],c[1],INST_BYTES);
        r=inst_compare(c[0],c[1],g[0],g[1]);
        CHECK(!r.correlation && r.forward_mismatches==0 && r.reverse16_mismatches==INST_WORDS);
    }
    printf("CORRELATION218 checks=%u seeds=16 PASS\n",checks);return 0;
}
