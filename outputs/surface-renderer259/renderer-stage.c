/*259 Internal, deliberately NOT wired to QOM/PFIFO yet. The runtime collector
 * must prove CPU callback-list ownership and stop/worker epochs before calling.
 * This function is compiled now so the GL implementation can be reviewed apart
 * from that future bridge. No native GPU permission is introduced. */
typedef struct X259GLSaved {
    GLint texture,draw_fbo,read_fbo,pack_buffer,unpack_buffer;
    GLint pixel[12];
} X259GLSaved;
static const GLenum x259_pixel_names[12]={
    GL_PACK_ALIGNMENT,GL_PACK_ROW_LENGTH,GL_PACK_SKIP_PIXELS,GL_PACK_SKIP_ROWS,
    GL_PACK_SWAP_BYTES,GL_PACK_LSB_FIRST,
    GL_UNPACK_ALIGNMENT,GL_UNPACK_ROW_LENGTH,GL_UNPACK_SKIP_PIXELS,GL_UNPACK_SKIP_ROWS,
    GL_UNPACK_SWAP_BYTES,GL_UNPACK_LSB_FIRST
};
static bool x259_gl_save(X259GLSaved *s)
{
    /* No glGetError drain: a pre-existing error refuses the diagnostic. */
    if(glGetError()!=GL_NO_ERROR)return false;
    glGetIntegerv(GL_TEXTURE_BINDING_2D,&s->texture);
    glGetIntegerv(GL_DRAW_FRAMEBUFFER_BINDING,&s->draw_fbo);
    glGetIntegerv(GL_READ_FRAMEBUFFER_BINDING,&s->read_fbo);
    glGetIntegerv(GL_PIXEL_PACK_BUFFER_BINDING,&s->pack_buffer);
    glGetIntegerv(GL_PIXEL_UNPACK_BUFFER_BINDING,&s->unpack_buffer);
    for(unsigned i=0;i<12;i++)glGetIntegerv(x259_pixel_names[i],&s->pixel[i]);
    return glGetError()==GL_NO_ERROR;
}
static bool x259_gl_restore(const X259GLSaved *s)
{
    glBindTexture(GL_TEXTURE_2D,s->texture);
    glBindFramebuffer(GL_DRAW_FRAMEBUFFER,s->draw_fbo);
    glBindFramebuffer(GL_READ_FRAMEBUFFER,s->read_fbo);
    glBindBuffer(GL_PIXEL_PACK_BUFFER,s->pack_buffer);
    glBindBuffer(GL_PIXEL_UNPACK_BUFFER,s->unpack_buffer);
    for(unsigned i=0;i<12;i++)glPixelStorei(x259_pixel_names[i],s->pixel[i]);
    X259GLSaved after;
    if(!x259_gl_save(&after))return false;
    if(after.texture!=s->texture||after.draw_fbo!=s->draw_fbo||after.read_fbo!=s->read_fbo||
       after.pack_buffer!=s->pack_buffer||after.unpack_buffer!=s->unpack_buffer)return false;
    for(unsigned i=0;i<12;i++)if(after.pixel[i]!=s->pixel[i])return false;
    return true;
}
static void x259_gl_clean_pixels(void)
{
    glBindBuffer(GL_PIXEL_PACK_BUFFER,0);glBindBuffer(GL_PIXEL_UNPACK_BUFFER,0);
    for(unsigned i=0;i<12;i++)glPixelStorei(x259_pixel_names[i],i==0||i==6?1:0);
}
static uint8_t x259_cpu_byte(unsigned i,unsigned seed)
{return (uint8_t)((37*i+19*(i/16)+7*(i/256))^(83*seed));}
static void x259_upload_pixels(unsigned variant,uint8_t pixels[572])
{
    /* GPU source generator is independent of the guest's expected-byte header. */
    unsigned n=0;
    for(unsigned row=0;row<11;row++)for(unsigned column=0;column<13;column++){
        pixels[n++]=(column*17+row*29+3+variant*31)&255;
        pixels[n++]=(column*71+row*11+19+variant*47)&255;
        pixels[n++]=(column*5+row*97+101+variant*67)&255;pixels[n++]=255;
    }
}
static bool x259_in_list(PGRAPHGLState *r,uintptr_t identity,SurfaceBinding **found)
{
    SurfaceBinding *s;unsigned walked=0;
    QTAILQ_FOREACH(s,&r->surfaces,entry){
        if(++walked>128)return false;
        if((uintptr_t)s==identity){*found=s;return true;}
    }
    *found=NULL;return true;
}
/* Caller: actual stopped guest + closed frontend + halted producer + context
 * fences + renderer/PG locks held, on the renderer thread. The bridge has not
 * been implemented, so this exported internal function currently has NO caller.
 * stages:1 age/delete,2 fresh dirty surface,3 second dirty update,4 retired/store.
 * x259_admit is an additional check, not a substitute for collecting evidence.
 */
unsigned pgraph_gl_pattern259_stage(NV2AState *d,X259RendererState *state,
    const X259Admission *a,const X259Ref *refs,const int64_t *ages,unsigned stage)
{
    PGRAPHState *pg=&d->pgraph;PGRAPHGLState *r=pg->gl_renderer_state;
    if(stage<1||stage>4||stage!=state->next_stage||state->failed)return 100;
    /* Epoch-specific collector excludes ONLY the exact owned test surface and
     * callback on stages3/4; it must attest them separately, never hide others. */
    unsigned reason=x259_admit(a,refs,ages,a->expected[X259_SURFACE]);
    if(reason)return 110+reason;
    if(!r||!qatomic_read(&d->pfifo.halt)||!xwn_frontend246_closed()||
       !qatomic_read(&qemu_get_cpu(0)->stopped)||bql_locked()||
       pg->surface_scale_factor!=1||pg->primitive_mode!=PRIM_TYPE_INVALID||
       pg->frame_time!=a->frame_time)return 120;
    if(stage==1){state->physical=a->physical;state->owner=a->owner;state->generation=a->generation;}
    else if(state->physical!=a->physical||state->owner!=a->owner||state->generation!=a->generation)return 121;
    SurfaceBinding *s=NULL;
    if(!x259_in_list(r,state->surface,&s))return 122;
    if((stage==3&&!s)||(stage!=3&&s))return 123;
    if(stage==4){
        /* No host store; a guest CPU store must already have won. */
        for(unsigned i=0;i<16384;i++)if(d->vram_ptr[a->physical+i]!=x259_cpu_byte(i,1))return 124;
        state->next_stage=5;return 0;
    }
    if(stage==1){
        for(unsigned i=0;i<16384;i++)if(d->vram_ptr[a->physical+i]!=x259_cpu_byte(i,0))return 125;
    }
    if(stage==3 && (s->vram_addr!=a->physical+4096||s->size!=704||s->width!=13||s->height!=11||
       s->pitch!=64||s->draw_dirty||s->download_pending||s->cpu_write_evict_pending||s->upload_pending||
       (uintptr_t)s->access_cb!=state->callback||s->gl_buffer!=state->texture))return 126;
    /* Recheck actual list before age invalidation; never alter global time or
     * another surface's age. Reject pointer/range uncertainty before any GL call. */
    SurfaceBinding *other;unsigned walked=0;
    QTAILQ_FOREACH(other,&r->surfaces,entry){
        if(++walked>128)return 127;
        if(other==s)continue;
        if(other->frame_time<0||other->frame_time>pg->frame_time||pg->frame_time-other->frame_time>=5)return 128;
        if(other->vram_addr>=a->ram_bytes||!other->size||other->size>a->ram_bytes-other->vram_addr)return 129;
        if(other->vram_addr<a->physical+16384 && a->physical<other->vram_addr+other->size)return 130;
    }
    X259GLSaved saved;
    if(!x259_gl_save(&saved))return 131;
    GLuint fbo=0;bool fresh=stage!=3,linked=false;unsigned result=0;
    x259_gl_clean_pixels();
    if(fresh){
        s=g_new0(SurfaceBinding,1);s->vram_addr=a->physical+4096;s->size=704;
        s->width=13;s->height=11;s->pitch=64;s->color=true;s->frame_time=pg->frame_time;
        s->fmt.bytes_per_pixel=4;s->fmt.gl_attachment=GL_COLOR_ATTACHMENT0;
        s->fmt.gl_internal_format=GL_RGBA8;s->fmt.gl_format=GL_BGRA;s->fmt.gl_type=GL_UNSIGNED_BYTE;
        glGenTextures(1,&s->gl_buffer);
    }
    glBindTexture(GL_TEXTURE_2D,s->gl_buffer);
    glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_BASE_LEVEL,0);
    glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAX_LEVEL,0);
    glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_NEAREST);
    glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_NEAREST);
    uint8_t pixels[572];x259_upload_pixels(stage-1,pixels);
    if(fresh)glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA8,13,11,0,GL_BGRA,GL_UNSIGNED_BYTE,pixels);
    else glTexSubImage2D(GL_TEXTURE_2D,0,0,0,13,11,GL_BGRA,GL_UNSIGNED_BYTE,pixels);
    if(glGetError()!=GL_NO_ERROR){result=132;goto restore;}
    if(fresh){
        /* Register through the REAL asynchronous CPU callback path. The host
         * must observe actual insertion before executing a guest memory load. */
        QTAILQ_INSERT_TAIL(&r->surfaces,s,entry);linked=true;
        register_cpu_access_callback(d,s);
        state->surface=(uintptr_t)s;state->callback=(uintptr_t)s->access_cb;state->texture=s->gl_buffer;
        if(!s->access_cb){result=133;goto restore;}
    }
    s->draw_dirty=true;
    if(stage==1){
        glGenFramebuffers(1,&fbo);glBindFramebuffer(GL_FRAMEBUFFER,fbo);
        glFramebufferTexture2D(GL_FRAMEBUFFER,GL_COLOR_ATTACHMENT0,GL_TEXTURE_2D,s->gl_buffer,0);
        if(glCheckFramebufferStatus(GL_FRAMEBUFFER)!=GL_FRAMEBUFFER_COMPLETE){result=134;goto restore;}
        s->frame_time=pg->frame_time-5;
        surface_evict_old(d); /* Actual download + common unlink/delete/free. */
        s=NULL;linked=false;
        SurfaceBinding *remaining=NULL;
        if(!x259_in_list(r,state->surface,&remaining)||remaining||glIsTexture(state->texture))result=135;
        /* Callback removal is queued, not yet proved complete by this result. */
    }
restore:
    if(glGetError()!=GL_NO_ERROR && !result)result=136;
    /* Never unlink a published surface on an uncertain failure. Close the
     * sacrificial emulator instead; its guest allocation is held until reboot. */
    if(result && fresh && !linked && s){glDeleteTextures(1,&s->gl_buffer);g_free(s);}
    if(fbo)glDeleteFramebuffers(1,&fbo);
    if(!x259_gl_restore(&saved)&&!result)result=137;
    if(result)state->failed=true;else state->next_stage++;
    return result;
}
