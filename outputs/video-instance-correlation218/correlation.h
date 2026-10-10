/* SPDX-License-Identifier: MIT */
#ifndef XWN_INST_CORRELATION_H
#define XWN_INST_CORRELATION_H
#include <stdint.h>
#define INST_BYTES 0x5000u
#define INST_WORDS (INST_BYTES/4u)
#define INST_BLOCKS (INST_BYTES/16u)
typedef struct INST_RESULT {
    unsigned cpu_stable,gpu_stable,nonzero_words,distinct_blocks;
    unsigned forward_mismatches,reverse16_mismatches,correlation;
} INST_RESULT;
/* Hypothesis only: reverse the order of16-byte blocks, retaining intra-block
   order. No address is used or written by this pure comparison routine. */
static INST_RESULT inst_compare(const uint32_t *c0,const uint32_t *c1,
                               const uint32_t *g0,const uint32_t *g1)
{
    INST_RESULT r={1,1,0,0,0,0,0};
    for(unsigned i=0;i<INST_WORDS;i++){
        if(c0[i]!=c1[i])r.cpu_stable=0;
        if(g0[i]!=g1[i])r.gpu_stable=0;
        if(c0[i])r.nonzero_words++;
        if(c0[i]!=g0[i])r.forward_mismatches++;
        unsigned inverse=(INST_BLOCKS-1u-i/4u)*4u+i%4u;
        if(c0[inverse]!=g0[i])r.reverse16_mismatches++;
    }
    /* Exact unique block count is bounded1280^2 comparisons. Distinct content
       rejects equal-zero/repeated-pattern windows as an informative result. */
    for(unsigned i=0;i<INST_BLOCKS;i++){
        unsigned unique=1;
        for(unsigned j=0;j<i;j++){
            unsigned equal=1;
            for(unsigned x=0;x<4;x++)if(c0[i*4+x]!=c0[j*4+x])equal=0;
            if(equal){unique=0;break;}
        }
        r.distinct_blocks+=unique;
    }
    r.correlation=r.cpu_stable && r.gpu_stable && r.nonzero_words>=256 &&
      r.distinct_blocks>=64 && r.reverse16_mismatches==0;
    return r;
}
#endif
