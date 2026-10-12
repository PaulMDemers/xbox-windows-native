/* New narrow cache-owner disposal proposal. No runtime provider yet. */
enum { X283_DISPOSE=283, X283_REFUSED=0, X283_OK=1, X283_QUARANTINE=2 };
typedef struct {
 X277Proof observation;
 unsigned operation,complete_graph,unknown_edges,selected_gl_edges,selected_ui_edges;
 unsigned locks_held,owner_current,contexts_current,observer_armed,post_snapshots;
 unsigned cache_count;
} X283Proof;
typedef struct {unsigned status,evicted_mask,deleted_mask;} X283Result;
static unsigned x283_admit(const X283Proof *p)
{
 if(!p || p->operation!=X283_DISPOSE || p->observation.stage!=2 ||
    p->complete_graph!=1 || p->unknown_edges || p->selected_gl_edges || p->selected_ui_edges ||
    p->locks_held!=1 || p->owner_current!=1 || p->contexts_current!=1 ||
    p->observer_armed!=1 || p->post_snapshots!=1 || p->cache_count<4 || p->cache_count>512)return 1;
 return x280_validate(&p->observation,1);
}
