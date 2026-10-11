#include "admission.h"
unsigned x259_admit(const X259Admission *a,const X259Ref *refs,const int64_t *ages,uint32_t age_count)
{
    uint32_t counts[X259_FAMILIES]={0},i;
    if(!a||!a->owner||!a->virtual_base||a->generation!=1||a->closed||a->attempted!=1||
       a->reads>8||a->writes>8||a->physical<0x100000||a->physical>0x03bfc000||
       (a->physical&4095)||a->ram_bytes<16384||a->physical>a->ram_bytes-16384)
        return X259_BAD_ARENA;
    for(i=0;i<4;i++)if(a->pages[i]!=a->physical+4096u*i)return X259_BAD_ARENA;
    if(!a->producer_halted||!a->cpu_stopped||!a->frontend_closed||!a->worker_joined||
       !a->render_fenced||!a->display_fenced||a->pending_reports||a->pending_cpu_jobs||a->active_primitives)
        return X259_BUSY;
    if(a->complete_families!=((1u<<X259_FAMILIES)-1)||a->unclassified||
       a->count>X259_MAX_REFS||(a->count&&!refs))return X259_UNKNOWN;
    if(a->frame_time<5||a->frame_time>INT32_MAX||age_count!=a->expected[X259_SURFACE]||
       (age_count&&!ages))return X259_BAD_AGE;
    for(i=0;i<age_count;i++)
        if(ages[i]<0||ages[i]>a->frame_time||a->frame_time-ages[i]>=5)return X259_BAD_AGE;
    for(i=0;i<a->count;i++){
        const X259Ref *r=&refs[i];
        if(r->family>=X259_FAMILIES||!r->identity)return X259_UNKNOWN;
        counts[r->family]++;
        /* Subtraction makes UINT64 wrap impossible. Zero-length entries must
         * be excluded explicitly by the collector, never interpreted here. */
        if(!r->length||r->begin>=a->ram_bytes||r->length>a->ram_bytes-r->begin)return X259_BAD_RANGE;
        if(r->begin<a->physical+16384&&a->physical<r->begin+r->length)return X259_OVERLAP;
        for(uint32_t j=0;j<i;j++)
            if(refs[j].family==r->family&&refs[j].identity==r->identity)return X259_UNKNOWN;
    }
    for(i=0;i<X259_FAMILIES;i++)if(counts[i]!=a->expected[i])return X259_UNKNOWN;
    return X259_ACCEPT;
}
