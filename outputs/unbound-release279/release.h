/*279 HOST-ONLY proposal. Caller must independently establish a current complete
 * pinned-GL4.0 owner graph under actual locks/CPU/context acknowledgments.
 * Not installed; no native GPU grant. The original277 contract is unchanged. */
#include "admission.h"
typedef struct {
    X277Proof observation;
    unsigned operation,complete_graph,unknown_edges,selected_gl_edges,selected_ui_edges;
    unsigned locks_held,owner_current,contexts_current,observer_armed,cache_count;
    unsigned enabled[4],target[4];
} X279Proof;
enum {X279_RELEASE=279, X279_OK=0, X279_REFUSED=1, X279_QUARANTINE=2};
typedef struct {unsigned status,mutated_mask;} X279Result;
static unsigned x279_admit(const X279Proof *p)
{
    if(!p || p->operation!=X279_RELEASE || x277_validate(&p->observation) ||
       p->observation.stage!=1 || p->complete_graph!=1 || p->unknown_edges ||
       p->selected_gl_edges || p->selected_ui_edges || p->locks_held!=1 ||
       p->owner_current!=1 || p->contexts_current!=1 || p->observer_armed!=1 ||
       p->cache_count<4 || p->cache_count>512) return X279_REFUSED;
    for(unsigned i=0;i<4;i++)
        if(p->enabled[i] || p->target[i]!=0x0de1) return X279_REFUSED;
    return X279_OK;
}
