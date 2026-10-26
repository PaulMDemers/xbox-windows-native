/* SPDX-License-Identifier: MIT */
#include <assert.h>
#include <stdio.h>
#include "delay_candidate.h"
struct fake { uint32_t next,step,mask,reads; };
static uint32_t rd(void *p) { struct fake *f=p; uint32_t v=f->next&f->mask;f->next+=f->step;++f->reads;return v; }
int main(void)
{
    struct delay_observation o;
    for(uint32_t step=1;step<=1689;++step) {
        struct fake f={0,step,UINT32_MAX,0};
        assert(delay500_candidate(rd,&f,1,&o)==DELAY_OK);
        assert(o.elapsed>=1688 && o.elapsed<1688+step && o.reads==f.reads);
        f=(struct fake){UINT32_MAX-50,step,UINT32_MAX,0};
        assert(delay500_candidate(rd,&f,1,&o)==DELAY_OK && o.elapsed>=1688);
    }
    struct fake f={10,0,UINT32_MAX,0};
    assert(delay500_candidate(rd,&f,1,&o)==DELAY_LIMIT && f.reads==100001);
    f=(struct fake){100,UINT32_MAX,UINT32_MAX,0};
    assert(delay500_candidate(rd,&f,1,&o)==DELAY_DISCONTINUITY && f.reads==2);
    f=(struct fake){0xfffff0,16,0xffffff,0};
    assert(delay500_candidate(rd,&f,1,&o)==DELAY_DISCONTINUITY && f.reads==2);
    f=(struct fake){0,33751,UINT32_MAX,0};
    assert(delay500_candidate(rd,&f,1,&o)==DELAY_DISCONTINUITY && f.reads==2);
    f=(struct fake){0,1,UINT32_MAX,0};
    assert(delay500_candidate(rd,&f,0,&o)==DELAY_ARGUMENT && f.reads==0);
    assert(delay500_candidate(rd,&f,2,&o)==DELAY_ARGUMENT && f.reads==0);
    assert(delay500_candidate(NULL,&f,1,&o)==DELAY_ARGUMENT);
    assert(delay500_candidate(rd,&f,1,NULL)==DELAY_ARGUMENT);
    puts("PASS: 3378 successful step/wrap models, frozen/backwards/24-bit/gap/argument rejection; no physical qualification");
}
