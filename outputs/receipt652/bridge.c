/* SPDX-License-Identifier: GPL-2.0-or-later
 * Copy already captured RAM only. These headers come from the pinned651 source.
 * No hook is installed; the caller must quiesce the producer before copying.
 */
#include "receipt.h"
#include "xwn_hd_adapter.h"
#include "trace649.h"
#include "readback651.h"
static void snapshot(uint32_t *d,const volatile struct readback651 *s) {
    unsigned i;
    d[0]=s->captured;d[1]=s->cr_captured;d[2]=s->index_before;
    d[3]=s->index_after;d[4]=s->flags_before;d[5]=s->flags_after;
    for(i=0;i<23;i++)d[6+i]=s->cr[i];
    for(i=0;i<18;i++)d[29+i]=s->mm[i];
}
void xwn652_bridge(struct xwn652_data *d,int result,unsigned post_kind,
                  const struct xwn_hd_request *r,const volatile struct xwn_hd_state *s,
                  const volatile struct xwn_trace649 *t,
                  const volatile struct readback651 *pre,const volatile struct readback651 *post) {
    unsigned i;d->result=result;d->post_kind=post_kind;
    d->request[0]=r->mode;d->request[1]=r->ram;d->request[2]=r->fb;
    d->request[3]=r->reserved;d->request[4]=r->hidden;d->request[5]=r->encoder;
    d->request[6]=r->cable;d->request[7]=r->video_flags;
    d->state[0]=s->stage;d->state[1]=s->error;d->state[2]=s->mutated;
    d->state[3]=s->smb_attempts;d->state[4]=s->smb_completed;
    d->state[5]=s->sync_polls;d->state[6]=s->vblank_polls;
    d->state[7]=s->vpll;d->state[8]=s->pcrtc;
    d->trace[0]=t->waits_started;d->trace[1]=t->waits_completed;d->trace[2]=t->failed_wait;
    for(i=0;i<6;i++) {
        const volatile struct xwn_edge649 *e=&t->edge[i];uint32_t *v=d->trace+3+10*i;
        v[0]=e->wanted;v[1]=e->first;v[2]=e->last;v[3]=e->samples;
        v[4]=e->byte_changes;v[5]=e->bit_changes;v[6]=e->completed;
        v[7]=e->begin;v[8]=e->end;v[9]=e->elapsed;
    }
    snapshot(d->pre,pre);snapshot(d->post,post);
}
