/* Fixed immutable records. Getters must acquire transaction state before reading.
 * All fields are scalar copies; no pointer is transported as dereference authority. */
static bool x280_publish(X280Transaction *t,X265State *last,unsigned prior)
{
    if(prior!=1 && prior!=4)return false;
    unsigned index=prior==4;
    if(t->published[index])return false;
    uint64_t row[16]={280,prior,t->candidate,t->reason?6:(prior==1?3:5),
        t->reason,t->armed,t->mutated_mask,t->post_captured,t->sealed,
        last?last->boundary.stage:0,last?last->boundary.worker_thread:0,
        last?last->boundary.cpu[0].epoch:0,last?last->boundary.cpu[1].epoch:0,
        t->finished,last?last->boundary.started:0,last?last->boundary.finished:0};
    memcpy(t->records[index],row,sizeof(row));
    t->published[index]=1;return true;
}
