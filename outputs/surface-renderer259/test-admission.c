#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "admission.h"
static X259Admission clean(void)
{
    X259Admission a={0};a.physical=0x1400000;a.owner=0x81234560;a.virtual_base=0x90123000;
    a.generation=a.attempted=1;a.ram_bytes=64u<<20;a.complete_families=127;a.frame_time=40;
    a.producer_halted=a.cpu_stopped=a.frontend_closed=a.worker_joined=a.render_fenced=a.display_fenced=1;
    for(unsigned i=0;i<4;i++)a.pages[i]=a.physical+4096*i;
    return a;
}
int main(void)
{
    unsigned checks=0;X259Admission a=clean();X259Ref refs[X259_MAX_REFS]={0};int64_t ages[2048]={0};
#define CHECK(want) do{assert(x259_admit(&a,refs,ages,a.expected[0])==(want));checks++;}while(0)
    CHECK(X259_ACCEPT);
    /* Half-open boundaries: adjacency allowed, any one-byte overlap rejected. */
    for(unsigned family=0;family<X259_FAMILIES;family++){
        a=clean();a.expected[family]=a.count=1;ages[0]=39;
        refs[0]=(X259Ref){a.physical-4096,4096,1,family};CHECK(X259_ACCEPT);
        refs[0].length++;CHECK(X259_OVERLAP);
        refs[0].begin=a.physical+16384;refs[0].length=1;CHECK(X259_ACCEPT);
        refs[0].begin--;CHECK(X259_OVERLAP);
        refs[0].begin=0;refs[0].length=UINT64_MAX;CHECK(X259_BAD_RANGE);
        refs[0].begin=UINT64_MAX;refs[0].length=2;CHECK(X259_BAD_RANGE);
        refs[0].begin=0;refs[0].length=0;CHECK(X259_BAD_RANGE);
        refs[0]=(X259Ref){0,4096,1,family};a.complete_families&=~(1u<<family);CHECK(X259_UNKNOWN);
    }
    for(unsigned page=0;page<4;page++){a=clean();a.pages[page]+=4096;CHECK(X259_BAD_ARENA);}
    a=clean();a.owner=0;CHECK(X259_BAD_ARENA);
    a=clean();a.owner=UINT64_MAX;CHECK(X259_BAD_ARENA);
    a=clean();a.virtual_base=UINT64_MAX;CHECK(X259_BAD_ARENA);
    a=clean();a.virtual_base++;CHECK(X259_BAD_ARENA);
    a=clean();a.generation=2;CHECK(X259_BAD_ARENA);
    a=clean();a.closed=1;CHECK(X259_BAD_ARENA);
    a=clean();a.attempted=0;CHECK(X259_BAD_ARENA);
    a=clean();a.physical=UINT64_MAX;CHECK(X259_BAD_ARENA);
    a=clean();a.unclassified=1;CHECK(X259_UNKNOWN);
    a=clean();a.pending_reports=1;CHECK(X259_BUSY);
    a=clean();a.pending_cpu_jobs=1;CHECK(X259_BUSY);
    a=clean();a.active_primitives=1;CHECK(X259_BUSY);
    a=clean();a.worker_joined=0;CHECK(X259_BUSY);
    a=clean();a.display_fenced=0;CHECK(X259_BUSY);
    a=clean();a.cpu_stopped=2;CHECK(X259_BUSY);
    a=clean();a.frame_time=INT64_MAX;CHECK(X259_BAD_AGE);
    a=clean();a.frame_time=4;CHECK(X259_BAD_AGE);
    a=clean();a.count=a.expected[0]=1;refs[0]=(X259Ref){0,4096,1,0};
    ages[0]=35;CHECK(X259_BAD_AGE);ages[0]=36;CHECK(X259_ACCEPT);
    ages[0]=41;CHECK(X259_BAD_AGE);ages[0]=-1;CHECK(X259_BAD_AGE);
    a=clean();a.expected[1]=1;CHECK(X259_UNKNOWN);
    a=clean();a.expected[0]=UINT32_MAX;CHECK(X259_UNKNOWN);
    a=clean();a.expected[0]=a.count=2048;a.expected[1]=1;CHECK(X259_UNKNOWN);
    a=clean();a.count=a.expected[1]=2;refs[0]=(X259Ref){0,4096,1,1};refs[1]=refs[0];CHECK(X259_UNKNOWN);
    /* Full bounded collector capacity. Every reference remains independently
     * counted; overflow/unknown family must not be silently truncated. */
    a=clean();a.count=a.expected[1]=X259_MAX_REFS;
    for(unsigned i=0;i<X259_MAX_REFS;i++)refs[i]=(X259Ref){i*4096,4096,i+1,1};
    CHECK(X259_ACCEPT);a.count++;CHECK(X259_UNKNOWN);a.count--;refs[8].family=7;CHECK(X259_UNKNOWN);
    printf("PASS admission_checks=%u full_capacity=%u no_GL_no_guest\n",checks,X259_MAX_REFS);
    return 0;
}
