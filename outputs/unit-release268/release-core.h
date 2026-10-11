/* SPDX-License-Identifier: GPL-2.0-or-later
 * Proposed narrow admission only. Caller must supply a coherent actual ledger.
 * No native GPU ownership or thread-completion claim is returned here.
 */
#ifndef X268_RELEASE_CORE_H
#define X268_RELEASE_CORE_H
#include <stdint.h>
#include <stdbool.h>
#define X268_UNITS 4u
typedef struct {
    uintptr_t binding;
    unsigned refs,cache_edges,unit_edges,enabled,target,texture;
} X268Unit;
typedef struct {
    unsigned role,unit,target,texture;
} X268Edge;
typedef struct {
    unsigned overflow,unknown_owners,pending,actor_unknown,callbacks;
    bool cpu_before_ack,worker_owner,render_current,ui_closed,contexts_matched;
    unsigned cache_count,edge_count;
    X268Unit units[X268_UNITS];
    const X268Edge *edges;
} X268Proof;
static inline unsigned x268_admit(const X268Proof *p)
{
    if(!p || p->overflow || p->unknown_owners || p->pending || p->actor_unknown ||
       p->callbacks || !p->cpu_before_ack || !p->worker_owner || !p->render_current ||
       !p->ui_closed || !p->contexts_matched) return 1;
    if(p->cache_count>512 || p->cache_count<4 || p->edge_count>8448 ||
       (p->edge_count && !p->edges)) return 2;
    for(unsigned i=0;i<X268_UNITS;i++) {
        const X268Unit *u=&p->units[i];
        /* Initial transaction deliberately supports only the observed 2D case. */
        if(!u->binding || !u->texture || u->enabled || u->target!=0x0de1 ||
           u->refs!=2 || u->cache_edges!=1 || u->unit_edges!=1) return 3;
        for(unsigned j=0;j<i;j++) if(u->binding==p->units[j].binding ||
                                      u->texture==p->units[j].texture) return 4;
    }
    unsigned seen=0;
    for(unsigned i=0;i<p->edge_count;i++) {
        const X268Edge *e=&p->edges[i];
        for(unsigned j=0;j<X268_UNITS;j++) if(e->texture==p->units[j].texture) {
            /* Only a matching render-context unit/2D binding can be removed.
             * FBOs, another unit/context, images or unknown edges refuse. */
            if(e->role!=1 || e->unit!=j || e->target!=0x0de1 || (seen&(1u<<j))) return 5;
            seen|=1u<<j;
        }
    }
    return 0;
}
#endif
