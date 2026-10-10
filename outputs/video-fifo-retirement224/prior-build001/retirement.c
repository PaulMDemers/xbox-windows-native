/* SPDX-License-Identifier: GPL-2.0-or-later */
#include "retirement.h"
const uint32_t X224Offsets[X224_WORDS]={
    0x3200,0x3204,0x3210,0x3214,0x3220,0x3228,0x324c,0x3240,
    0x3244,0x3250,0x3270,0x2400,0x2100,0x400100,0x400144,0x400148
};
void x224_sample(X224Read read,void *opaque,X224Reply *out)
{
    uint32_t i,j,*p=(uint32_t *)out;
    for(i=0;i<sizeof(*out)/sizeof(*p);i++)p[i]=0;
    out->reasons=X224_NO_OWNERSHIP|X224_UNMODELED_BUSY;
    if(!read){out->status=X224_READ_FAILED;return;}
    for(i=0;i<X224_ROUNDS;i++) {
        uint32_t *v=out->values[i];
        for(j=0;j<X224_WORDS;j++) {
            if(!read(opaque,j,&v[j])){out->status=X224_READ_FAILED;return;}
            out->reads++;
            if(i && v[j]!=out->values[0][j])out->reasons|=X224_CHANGED;
        }
        out->rounds++;
        if(v[7]!=v[8])out->reasons|=X224_DMA_DATA;
        if(v[5]&0x1ffc0000u)out->reasons|=X224_METHOD;
        if(v[6]&1u)out->reasons|=X224_SUBROUTINE;
        if(!(v[3]&16u) || v[2]!=v[10])out->reasons|=X224_CACHE;
        if(!(v[11]&16u))out->reasons|=X224_RUNOUT;
        if(v[13])out->reasons|=X224_GRAPH_IRQ;
        if(v[5]&0xe0000000u)out->reasons|=X224_DMA_ERROR;
        if(v[12])out->reasons|=X224_FIFO_IRQ;
        if(v[4]&0x1000u)out->reasons|=X224_DMA_SUSPENDED;
    }
    out->status=X224_OBSERVED;
}
