/*280 Actual worker orchestration. All three state/ledger buffers are allocated
 * before publication. Called by the owned PFIFO worker with its lock held.
 * Capture returns with renderer/PG locks held on success, unlocked on failure.
 * State:1 ready,2 initial running,3 guest may resume,4 end ready,5 complete,6 refusal.
 */
static void x280_unlock(NV2AState *d)
{qemu_mutex_unlock(&d->pgraph.lock);qemu_mutex_unlock(&d->pgraph.renderer_lock);}
static bool x280_worker(NV2AState *d)
{
    X265State *initial=qatomic_load_acquire(&d->ledger265);
    X280Transaction *t=initial?initial->transaction280:NULL;
    if(!t)return false;
    unsigned state=qatomic_load_acquire(&t->state);
    if((state!=1&&state!=4) || qatomic_cmpxchg(&t->state,state,2)!=state)return false;
    unsigned reason=0;X265State *last=t->pre;bool locked=false;
    if(t->candidate>1 || !t->pre || !t->post || !t->end || t->pre==t->post || t->post==t->end || t->pre==t->end){reason=1;goto finish;}
    if(state==1) {
        if(!x280_capture(d,t,t->pre,1)){reason=2;goto finish;}locked=true;
        if(!x280_unbound(d,t->pre,&t->release)){reason=3;goto finish;}
        if(!pgraph_gl_reuse269_arm(d)){reason=4;goto finish;}t->armed=1;t->release.observer_armed=1;
        if(!x260_alive(d,&t->pre->boundary) || !x278_quiescent(d,t->pre,t->pre,false)){reason=15;goto finish;}
        if(t->candidate) {
            X279Result result=pgraph_gl_release280(d,&t->release);
            t->mutated_mask=result.mutated_mask;
            if(result.status!=X279_OK || result.mutated_mask!=15){reason=5;goto finish;}
        }
        x280_unlock(d);locked=false;last=t->post;
        if(!x280_capture(d,t,t->post,2)){reason=6;goto finish;}locked=true;
        if(!x280_link(&t->pre->proof278,&t->post->proof278,t->candidate) ||
           !x280_retained(t->pre,t->post,t->candidate)){reason=7;goto finish;}
        if(!pgraph_gl_reuse280_post(d)){reason=8;goto finish;}t->post_captured=1;
        x280_unlock(d);locked=false;
    } else {
        last=t->end;
        if(!t->armed || !t->post_captured || !pgraph_gl_reuse274_ready(t->pre->boundary.worker_thread)){reason=9;goto finish;}
        if(!x280_capture(d,t,t->end,3)){reason=10;goto finish;}locked=true;
        if(!x274_context_match(t->pre,t->end) || !x280_resume(&t->pre->proof278,&t->end->proof278,t->candidate)){reason=11;goto finish;}
        x280_unlock(d);locked=false;
        qemu_mutex_unlock(&d->pfifo.lock);t->sealed=pgraph_gl_reuse269_seal();qemu_mutex_lock(&d->pfifo.lock);
        if(!t->sealed || pgraph_gl_reuse269_error()){reason=12;goto finish;}
    }
finish:
    if(locked)x280_unlock(d);
    t->reason=reason;t->finished=qemu_clock_get_ns(QEMU_CLOCK_REALTIME);
    if(!t->reason && (!last || !x260_alive(d,&last->boundary)))t->reason=14;
    if(!x280_publish(t,last,state) && !t->reason)t->reason=13;
    if(!t->reason)qatomic_set(&d->pfifo.halt,t->old_halt);
    qatomic_store_release(&t->state,t->reason?6:(state==1?3:5));return true;
}
