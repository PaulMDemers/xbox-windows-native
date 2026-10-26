/* SPDX-License-Identifier: MIT
 * HOST-ONLY candidate. Not linked into684 or qualified for native startup.
 * Caller must establish a full-width 3,579,545Hz clock and I/O ownership.
 * 500us rounded upward: ceil(3579545 / 2000) =1790 ticks.
 */
#ifndef XWN684_DELAY_CANDIDATE_H
#define XWN684_DELAY_CANDIDATE_H
#include <stdint.h>
enum delay_result { DELAY_OK, DELAY_ARGUMENT, DELAY_LIMIT, DELAY_DISCONTINUITY };
struct delay_observation { uint32_t first,last,elapsed,reads; };
static enum delay_result delay500_candidate(uint32_t (*read_tick)(void *),
    void *ctx, unsigned clock_qualified, struct delay_observation *o)
{
    if(!read_tick || !o || clock_qualified!=1) return DELAY_ARGUMENT;
    o->first=read_tick(ctx);o->last=o->first;o->elapsed=0;o->reads=1;
    for(unsigned i=0;i<100000;++i) {
        uint32_t now=read_tick(ctx), step=now-o->last;
        o->last=now;o->elapsed=now-o->first;++o->reads;
        /* Reject backwards samples/large gaps, including a 24-bit wrap.
         * A true uint32 wrap remains valid through modular subtraction. */
        if(step>35795 || o->elapsed>35795) return DELAY_DISCONTINUITY;
        if(o->elapsed>=1790) return DELAY_OK;
    }
    return DELAY_LIMIT;
}
#endif
