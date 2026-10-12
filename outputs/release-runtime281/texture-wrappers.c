/* One-shot post-release snapshots. Never fabricate a normal guest bind. */
static unsigned x281_post_attempted;
bool pgraph_gl_reuse280_post(NV2AState *d)
{
    if(qatomic_cmpxchg(&x281_post_attempted,0u,1u)!=0)return false;
    if(!x269_enter())return false;
    bool okay=true;
    for(unsigned i=0;i<4;i++) {
        /* Original snapshot function rechecks live cache owner and restores GL. */
        if(!x269_snapshot(d,i,2)){okay=false;break;}
    }
    if(!okay)qatomic_fetch_or(&x269.transport_error,4u);
    qatomic_fetch_and(&x269.busy,~1u);
    return okay && !pgraph_gl_reuse269_error();
}
X279Result pgraph_gl_release280(NV2AState *d,const X279Proof *proof)
{return x279_release(d,proof);}
