/* SPDX-License-Identifier: GPL-2.0-or-later */
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "retirement.h"
typedef struct { uint32_t words[X224_WORDS],calls,fail_at,change_at; } Mock;
static int reader(void *opaque,uint32_t index,uint32_t *value)
{
    Mock *m=opaque;assert(index<X224_WORDS);
    if(m->calls++==m->fail_at)return 0;
    *value=m->words[index];if(m->calls>m->change_at)*value^=0x1000;
    return 1;
}
static void reset(Mock *m)
{ memset(m,0,sizeof(*m));m->words[3]=m->words[11]=16;m->fail_at=m->change_at=~0u; }
int main(void)
{
    Mock m;X224Reply r;uint32_t i;
    reset(&m);x224_sample(reader,&m,&r);
    assert(r.status==X224_OBSERVED && r.reads==128 && r.rounds==8);
    assert(r.reasons==(X224_NO_OWNERSHIP|X224_UNMODELED_BUSY));
    /* Disabled push/pull and equal cached pointers do not hide pending DMA. */
    reset(&m);m.words[7]=4;x224_sample(reader,&m,&r);assert(r.reasons&X224_DMA_DATA);
    /* Even equal DMA GET/PUT cannot discard a residual method header. */
    reset(&m);m.words[5]=1u<<18;x224_sample(reader,&m,&r);assert(r.reasons&X224_METHOD);
    for(i=0;i<128;i++) {
        reset(&m);m.fail_at=i;x224_sample(reader,&m,&r);
        assert(r.status==X224_READ_FAILED && r.reads==i && r.rounds==i/16 && m.calls==i+1);
        assert(r.reasons&X224_NO_OWNERSHIP);
    }
    reset(&m);m.change_at=16;x224_sample(reader,&m,&r);assert(r.reasons&X224_CHANGED);
    for(i=0;i<65536;i++) {
        reset(&m);m.words[5]=i<<16;x224_sample(reader,&m,&r);
        assert(!!(r.reasons&X224_METHOD)==!!(m.words[5]&0x1ffc0000));
        assert(!!(r.reasons&X224_DMA_ERROR)==!!(m.words[5]&0xe0000000));
        assert(r.reasons&X224_NO_OWNERSHIP);
    }
    x224_sample(NULL,NULL,&r);assert(r.status==X224_READ_FAILED && !r.reads);
    puts("PASS DMA_state_cases=65536 read_failure_positions=128 no_ownership_grant=1");return 0;
}
