/* SPDX-License-Identifier: MIT */
#ifndef XWN684_SAMPLE_H
#define XWN684_SAMPLE_H
#include <stdint.h>
#define SAMPLE_COUNT 65
struct sample { uint32_t pm_before, pm_after; uint64_t qpc, irq, tsc; };
struct reader {
    void *ctx;
    uint32_t (*pm)(void *);
    uint64_t (*qpc)(void *), (*irq)(void *), (*tsc)(void *);
    void (*sleep_ms)(void *, unsigned);
};
/* Finite acquisition only: no timer-based wait, masking or state writes.
 * Kernel sleep and read callbacks are not independently time-bounded here. */
static int acquire(struct reader *r, struct sample *s, unsigned interval_ms)
{
    if (!r || !s || !r->pm || !r->qpc || !r->irq || !r->tsc ||
        !r->sleep_ms || (interval_ms != 0 && interval_ms != 100)) return 0;
    for (unsigned i = 0; i < SAMPLE_COUNT; ++i) {
        if (i && interval_ms) r->sleep_ms(r->ctx, interval_ms);
        s[i].pm_before = r->pm(r->ctx);
        s[i].qpc = r->qpc(r->ctx);
        s[i].irq = r->irq(r->ctx);
        s[i].tsc = r->tsc(r->ctx);
        s[i].pm_after = r->pm(r->ctx);
    }
    return 1;
}
#endif
