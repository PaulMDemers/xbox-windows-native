/* Explicit fresh CPU acknowledgment times/identities, including nonzero counts. */
static bool x280_scalar_publish(X265State *s,unsigned reason)
{
    bool ok=x278_publish(s);X277Proof *p=&s->proof278;
    ok &= x265_add(&s->ledger,71,s->boundary.stage,s->boundary.worker_thread,
        s->boundary.started,p->finished,s->boundary.deadline,s->admission278,reason);
    for(unsigned phase=0;phase<2;phase++) {
        X277CPU *c=&p->cpu[phase];
        ok &= x265_add(&s->ledger,72,phase,c->epoch,c->thread,c->when,c->done,c->error,c->clock_error);
    }
    return ok;
}
