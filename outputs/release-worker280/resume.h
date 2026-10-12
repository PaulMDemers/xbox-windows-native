/* Across actual guest work clocks may change; owner and selected textures may not. */
static bool x280_resume(const X277Proof *a,const X277Proof *b,unsigned candidate)
{
    if(x280_validate(a,candidate) || x280_validate(b,candidate) || a->stage!=1 || b->stage!=3 ||
       a->worker!=b->worker || a->device!=b->device || a->region!=b->region || a->function!=b->function ||
       a->ram_base!=b->ram_base || a->ram_bytes!=b->ram_bytes ||
       a->render_context!=b->render_context || a->display_context!=b->display_context ||
       b->started<a->finished || a->cpu[1].thread!=b->cpu[0].thread)return false;
    for(unsigned i=0;i<4;i++)
        if(memcmp(&a->textures[i],&b->textures[i],sizeof(X277Texture)))return false;
    return true;
}
