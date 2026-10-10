/* SPDX-License-Identifier: GPL-2.0-or-later
 * Resident CPU ownership prefix only. No GPU mapping, command or grant API.
 * Release is safe because this implementation cannot expose any GPU reference.
 */
#include "context.h"
static unsigned char expected(uint32_t i,uint32_t generation)
{
    if(i>=8208 && i<8212)return 0; /* Cleared future completion word, not a GPU witness. */
    return (unsigned char)((i*29u+(i>>8)*7u+generation*11u)^0xa5u);
}
static int verify(X222Manager *m)
{
    uint32_t i;
    for(i=0;i<X222_BYTES;i++)if(m->memory[i]!=expected(i,m->generation))return 0;
    /* Diagnostic totals saturate; they cannot wrap into a misleading small count. */
    if(m->verified_bytes<=UINT32_MAX-X222_BYTES)m->verified_bytes+=X222_BYTES;
    else m->verified_bytes=UINT32_MAX;
    return 1;
}
static void increment(uint32_t *v) { if(*v!=UINT32_MAX)++*v; }
void x222_initialize(X222Manager *m)
{
    uint32_t i; unsigned char *p=(unsigned char *)m;
    for(i=0;i<sizeof(*m);i++)p[i]=0;
    m->next_generation=1;
}
void x222_action(X222Manager *m,const X222Ops *ops,void *owner,const X222Request *in,X222Reply *out)
{
    uint32_t i,status=X222_BAD; uint64_t physical;
    unsigned char *p=(unsigned char *)out;
    if(!out)return;
    for(i=0;i<sizeof(*out);i++)p[i]=0;
    if(!m || !ops || !owner || !in || !ops->passive || !ops->enter || !ops->leave ||
       !ops->allocate || !ops->translate || !ops->free) {out->status=X222_BAD;return;}
    if(!ops->passive(ops->opaque)) {out->status=X222_IRQL;return;}
    if(!ops->enter(ops->opaque)) {out->status=X222_WAIT;return;}
    if(in->op==X222_INFO && !in->generation)status=X222_OK;
    else if(in->op==X222_ALLOCATE && !in->generation) {
        if(m->memory)status=X222_BUSY;
        else if(!m->next_generation)status=X222_EXHAUSTED;
        else {
            uint32_t generation=m->next_generation++;
            unsigned char *memory=ops->allocate(ops->opaque);
            status=X222_OOM;
            if(memory) {
                physical=ops->translate(ops->opaque,memory);
                status=X222_TRANSLATION;
                if(!(physical&4095) && physical>=0x100000 && physical<=0x03c00000-X222_BYTES) {
                    for(i=0;i<4;i++) {
                        if(ops->translate(ops->opaque,memory+i*4096)!=physical+i*4096 ||
                           ops->translate(ops->opaque,memory+i*4096+4095)!=physical+i*4096+4095)break;
                    }
                    if(i==4) {
                        for(i=0;i<X222_BYTES;i++)memory[i]=expected(i,generation);
                        m->memory=memory;m->owner=owner;m->generation=generation;
                        for(i=0;i<4;i++)m->pages[i]=(uint32_t)physical+i*4096;
                        increment(&m->allocations);status=X222_OK;
                    }
                }
                if(status!=X222_OK)ops->free(ops->opaque,memory);
            }
        }
    } else if(in->op>=X222_QUERY && in->op<=X222_CLEANUP && in->op!=X222_INFO) {
        if(!m->memory)status=(in->op==X222_CLEANUP && !in->generation)?X222_OK:X222_EMPTY;
        else if(m->owner!=owner)status=X222_OWNER;
        else if(in->op==X222_CLEANUP && !in->generation)status=X222_OK;
        else if(!in->generation || in->generation!=m->generation)status=X222_STALE;
        else status=X222_OK;
        if(status==X222_OK && m->memory) {
            if(!verify(m))status=X222_CORRUPT;
            if(in->op==X222_RELEASE || in->op==X222_CLEANUP) {
                /* CPU-only, pre-exposure cleanup. This is NOT a GPU drain. */
                ops->free(ops->opaque,m->memory);m->memory=0;m->owner=0;m->generation=0;
                for(i=0;i<4;i++)m->pages[i]=0;
                increment(&m->releases);
                if(in->op==X222_CLEANUP)increment(&m->cleanup_releases);
            } else if(status==X222_OK && in->op==X222_EXPOSE) {
                /* No actual resident instance/channel handoff exists yet. Never
                 * call the mock215 expose operation or manufacture proof bits. */
                increment(&m->exposure_refusals);status=X222_HOLD;
            }
        }
    }
    out->status=status;out->owned=m->memory!=0;
    out->allocations=m->allocations;out->releases=m->releases;
    out->verified_bytes=m->verified_bytes;out->exposure_refusals=m->exposure_refusals;
    out->cleanup_releases=m->cleanup_releases;
    if(m->memory && m->owner==owner) {
        out->generation=m->generation;
        for(i=0;i<4;i++)out->pages[i]=m->pages[i];
    }
    ops->leave(ops->opaque);
}
