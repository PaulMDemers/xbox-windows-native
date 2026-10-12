/*276 Read-only terminal-refusal view. CPU-owned records are never dereferenced
 * through their saved callback pointers. No job, gate or lifetime mutation. */
static char *x276_unavailable(unsigned state,unsigned done,unsigned error)
{
    return g_strdup_printf("version=276 available=0 state=%u done=%u error=%u",state,done,error);
}
static bool x276_append(char *buffer,size_t *used,const char *format,...)
{
    va_list args;va_start(args,format);
    int n=vsnprintf(buffer+*used,65536-*used,format,args);va_end(args);
    if(n<0 || (size_t)n>=65536-*used)return false;
    *used+=(size_t)n;return true;
}
char *pgraph_gl_callbacks276_report(NV2AState *d)
{
    X265State *s=qatomic_load_acquire(&d->ledger265);
    if(!s)return x276_unavailable(0,0,1);
    X260Slot *v=&s->boundary;unsigned state=qatomic_load_acquire(&v->state);
    if(state!=6)return x276_unavailable(state,0,2);
    X260CPU *a=&v->cpu[0];unsigned done=qatomic_load_acquire(&a->done);
    if(done!=1)return x276_unavailable(state,done,3);
    /* Once acknowledged, this CPU job never writes its metadata again. The
     * actor and CPU metadata remain allocated even after a failed boundary. */
    if(v->stage!=1 || v->reason!=14 || a->reason || a->count>X260_CALLBACKS ||
       !v->worker_thread || !a->thread || a->thread==v->worker_thread ||
       a->epoch!=1 || a->when<v->started || a->when>v->finished ||
       v->finished>=(uint64_t)v->deadline)return x276_unavailable(state,done,4);
    char *buffer=g_malloc(65536);size_t used=0;
    bool okay=x276_append(buffer,&used,"version=276 available=1 state=%u done=%u error=0 stage=%u phase=0 reason=%u cpu_reason=%u count=%u capacity=%u epoch=%"PRIu64" thread=%"PRIu64" worker=%"PRIu64" when=%"PRIu64" started=%"PRIu64" finished=%"PRIu64" deadline=%"PRIu64" device=%"PRIu64" native_grant=0",
        state,done,v->stage,v->reason,a->reason,a->count,X260_CALLBACKS,a->epoch,
        a->thread,v->worker_thread,a->when,v->started,v->finished,(uint64_t)v->deadline,(uint64_t)(uintptr_t)d);
    for(unsigned i=0;okay && i<a->count;i++) {
        const uint64_t *r=a->rows[i],*e=a->detail276[i];
        okay=x276_append(buffer,&used," c%u=%"PRIu64":%"PRIu64":%"PRIu64":%"PRIu64":%"PRIu64":%"PRIu64":%"PRIu64,
            i,r[0],r[1],r[2],r[3],e[0],e[1],e[2]);
    }
    if(!okay){g_free(buffer);return x276_unavailable(state,done,5);}
    return buffer;
}
