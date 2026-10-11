/* Exercise the exact waveform generator, emitting the expected scheduled PCM. */
#include <assert.h>
#include <stdio.h>
#include "waveform.h"
int main(void)
{
    unsigned cycle, frame, channel;
    for(cycle=0;cycle<6;cycle++) for(frame=0;frame<CHANNEL001_FRAMES;frame++) for(channel=0;channel<2;channel++) {
        unsigned mask=cycle%3+1;
        int wide=channel001_sample(frame,channel,mask)*(cycle<3?1:4);
        assert(wide>=-32768 && wide<=32767);
        short v=(short)wide;
        unsigned short u=(unsigned short)v;
        assert(v>=-7552 && v<=7552);
        if(frame>=96000 || !(mask&(1U<<channel))) assert(v==0);
        if(frame==0 || frame==95999) assert(v==0);
        assert(putchar(u&255)!=EOF);assert(putchar(u>>8)!=EOF);
    }
    assert(channel001_sample(0,2,3)==0);
    assert(channel001_sample(100,0,0)==0);
    assert(channel001_sample(100,0,4)==0);
    return fflush(stdout)==0?0:1;
}
