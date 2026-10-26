/* SPDX-License-Identifier: MIT */
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "sample.h"
struct fake { uint32_t value; unsigned calls, sleeps, milliseconds; };
static uint32_t pm(void *p) { struct fake *f=p; ++f->calls; return f->value++; }
static uint64_t q(void *p) { (void)p; return UINT64_C(0xfedcba9876543210); }
static void nap(void *p, unsigned n) { struct fake *f=p; ++f->sleeps; f->milliseconds+=n; }
int main(void)
{
    struct sample s[SAMPLE_COUNT];
    struct fake f={UINT32_MAX-10,0,0,0};
    struct reader r={&f,pm,q,q,q,nap};
    assert(acquire(&r,s,100));
    assert(f.calls==130 && f.sleeps==64 && f.milliseconds==6400);
    for(unsigned i=0;i<SAMPLE_COUNT;++i) {
        assert(s[i].pm_before==(uint32_t)(UINT32_MAX-10+2*i));
        assert(s[i].pm_after==s[i].pm_before+1);
        assert(s[i].qpc==q(0) && s[i].irq==q(0) && s[i].tsc==q(0));
    }
    /* Preserve, rather than mask away, every high timer bit. */
    f=(struct fake){0xab000000,0,0,0};
    assert(acquire(&r,s,0));
    assert(f.calls==130 && f.sleeps==0 && s[0].pm_before==0xab000000);
    assert(!acquire(NULL,s,0) && !acquire(&r,NULL,0) && !acquire(&r,s,1));
    struct reader bad=r; bad.pm=NULL; assert(!acquire(&bad,s,0));
    bad=r; bad.qpc=NULL; assert(!acquire(&bad,s,0));
    bad=r; bad.irq=NULL; assert(!acquire(&bad,s,0));
    bad=r; bad.tsc=NULL; assert(!acquire(&bad,s,0));
    bad=r; bad.sleep_ms=NULL; assert(!acquire(&bad,s,0));
    puts("PASS: 130 samples, full-width wrap/high bits, finite sleep count, invalid callbacks");
}
