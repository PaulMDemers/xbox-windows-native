/* Compare actual pre/post state without rewriting fields to satisfy old277. */
static bool x280_link(const X277Proof *a,const X277Proof *b,unsigned candidate)
{
    if(x280_validate(a,candidate) || x280_validate(b,candidate) || a->stage!=1 || b->stage!=2 ||
       a->worker!=b->worker || a->device!=b->device || a->region!=b->region || a->function!=b->function ||
       a->ram_base!=b->ram_base || a->ram_bytes!=b->ram_bytes ||
       a->render_context!=b->render_context || a->display_context!=b->display_context ||
       b->started<a->finished || a->cpu[1].thread!=b->cpu[0].thread ||
       a->cpu[1].clock!=b->cpu[0].clock || a->cpu[1].count!=b->cpu[0].count ||
       memcmp(a->cpu[1].callbacks,b->cpu[0].callbacks,a->cpu[1].count*sizeof(X277Callback)) ||
       memcmp(a->graph[1].surfaces,b->graph[0].surfaces,a->graph[1].count*sizeof(X277Surface)))return false;
    for(unsigned i=0;i<4;i++)
        if(memcmp(&a->textures[i],&b->textures[i],8*sizeof(uint64_t)))return false;
    return true;
}
