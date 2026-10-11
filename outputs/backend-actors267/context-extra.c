/*267 Bounded query of indexed references and known context-local containers.
 * Uninstantiated reserved names are recorded, never bound into existence.
 * All selection changes are restored and recorded, including failure paths.
 */
static bool x267_indexed(X265Rows *out,unsigned role,int64_t deadline)
{
    const GLenum limits[]={GL_MAX_UNIFORM_BUFFER_BINDINGS,GL_MAX_TRANSFORM_FEEDBACK_BUFFERS};
    const GLenum bindings[]={GL_UNIFORM_BUFFER_BINDING,GL_TRANSFORM_FEEDBACK_BUFFER_BINDING};
    const GLenum starts[]={GL_UNIFORM_BUFFER_START,GL_TRANSFORM_FEEDBACK_BUFFER_START};
    const GLenum sizes[]={GL_UNIFORM_BUFFER_SIZE,GL_TRANSFORM_FEEDBACK_BUFFER_SIZE};
    for(unsigned family=0;family<2;family++) {
        GLint count=0;glGetIntegerv(limits[family],&count);
        if(count<1 || count>1024) return false;
        if(!x265_add(out,52,role,family,count,0,0,0,0)) return false;
        for(unsigned i=0;i<(unsigned)count;i++) {
            if(qemu_clock_get_ns(QEMU_CLOCK_REALTIME)>=deadline) return false;
            GLint name=0;GLint64 start=0,size=0;
            glGetIntegeri_v(bindings[family],i,&name);
            glGetInteger64i_v(starts[family],i,&start);
            glGetInteger64i_v(sizes[family],i,&size);
            if(start<0 || size<0 || !x265_add(out,53,role,family,i,(unsigned)name,start,size,0)) return false;
        }
    }
    /* Scope is the GL4.0 interfaces used by this pinned backend. No assertion
     * that future SSBO/atomic-counter/image/extension references are absent. */
    return glGetError()==GL_NO_ERROR;
}
static bool x267_fbo(X265Rows *out,unsigned role,GLuint name,int64_t deadline)
{
    bool live=name && glIsFramebuffer(name);
    if(!x265_add(out,54,role,name,live,0,0,0,0)) return false;
    if(!live) return glGetError()==GL_NO_ERROR;
    GLint old_draw=0,old_read=0,count=0;
    glGetIntegerv(GL_DRAW_FRAMEBUFFER_BINDING,&old_draw);
    glGetIntegerv(GL_READ_FRAMEBUFFER_BINDING,&old_read);
    glGetIntegerv(GL_MAX_COLOR_ATTACHMENTS,&count);
    if(count<1 || count>64) return false;
    glBindFramebuffer(GL_FRAMEBUFFER,name);
    bool okay=true;
    for(unsigned i=0;i<(unsigned)count+2;i++) {
        if(qemu_clock_get_ns(QEMU_CLOCK_REALTIME)>=deadline) {okay=false;break;}
        GLenum attachment=i<(unsigned)count?GL_COLOR_ATTACHMENT0+i:
                          i==(unsigned)count?GL_DEPTH_ATTACHMENT:GL_STENCIL_ATTACHMENT;
        GLint type=0,object=0,level=0,layer=0;
        glGetFramebufferAttachmentParameteriv(GL_FRAMEBUFFER,attachment,GL_FRAMEBUFFER_ATTACHMENT_OBJECT_TYPE,&type);
        if(type!=GL_NONE) glGetFramebufferAttachmentParameteriv(GL_FRAMEBUFFER,attachment,GL_FRAMEBUFFER_ATTACHMENT_OBJECT_NAME,&object);
        if(type==GL_TEXTURE) {
            glGetFramebufferAttachmentParameteriv(GL_FRAMEBUFFER,attachment,GL_FRAMEBUFFER_ATTACHMENT_TEXTURE_LEVEL,&level);
            glGetFramebufferAttachmentParameteriv(GL_FRAMEBUFFER,attachment,GL_FRAMEBUFFER_ATTACHMENT_TEXTURE_LAYER,&layer);
        }
        if(!x265_add(out,55,role,name,attachment,type,(unsigned)object,(unsigned)level,(unsigned)layer)) {okay=false;break;}
    }
    glBindFramebuffer(GL_DRAW_FRAMEBUFFER,old_draw);glBindFramebuffer(GL_READ_FRAMEBUFFER,old_read);
    GLint draw=0,read=0;glGetIntegerv(GL_DRAW_FRAMEBUFFER_BINDING,&draw);glGetIntegerv(GL_READ_FRAMEBUFFER_BINDING,&read);
    okay &= x265_add(out,56,role,name,(unsigned)old_draw,(unsigned)draw,(unsigned)old_read,(unsigned)read,count);
    return okay && draw==old_draw && read==old_read && glGetError()==GL_NO_ERROR;
}
static bool x267_vao(X265Rows *out,unsigned role,GLuint name,int64_t deadline)
{
    bool live=name && glIsVertexArray(name);
    if(!x265_add(out,57,role,name,live,0,0,0,0)) return false;
    if(!live) return glGetError()==GL_NO_ERROR;
    GLint old=0,count=0,element=0;
    glGetIntegerv(GL_VERTEX_ARRAY_BINDING,&old);glGetIntegerv(GL_MAX_VERTEX_ATTRIBS,&count);
    if(count<1 || count>64) return false;
    glBindVertexArray(name);glGetIntegerv(GL_ELEMENT_ARRAY_BUFFER_BINDING,&element);
    bool okay=x265_add(out,58,role,name,(unsigned)element,count,0,0,0);
    for(unsigned i=0;okay && i<(unsigned)count;i++) {
        if(qemu_clock_get_ns(QEMU_CLOCK_REALTIME)>=deadline) {okay=false;break;}
        GLint enabled=0,buffer=0,divisor=0;void *pointer=NULL;
        glGetVertexAttribiv(i,GL_VERTEX_ATTRIB_ARRAY_ENABLED,&enabled);
        glGetVertexAttribiv(i,GL_VERTEX_ATTRIB_ARRAY_BUFFER_BINDING,&buffer);
        glGetVertexAttribiv(i,GL_VERTEX_ATTRIB_ARRAY_DIVISOR,&divisor);
        glGetVertexAttribPointerv(i,GL_VERTEX_ATTRIB_ARRAY_POINTER,&pointer);
        okay=x265_add(out,59,role,name,i,enabled,(unsigned)buffer,(unsigned)divisor,(uintptr_t)pointer);
    }
    glBindVertexArray(old);GLint restored=0;glGetIntegerv(GL_VERTEX_ARRAY_BINDING,&restored);
    okay &= x265_add(out,60,role,name,(unsigned)old,(unsigned)restored,0,0,0);
    return okay && restored==old && glGetError()==GL_NO_ERROR;
}
static bool x267_program(X265Rows *out,unsigned role,GLuint name)
{
    bool live=name && glIsProgram(name);
    if(!x265_add(out,61,role,name,live,0,0,0,0)) return false;
    if(!live) return glGetError()==GL_NO_ERROR;
    GLint count=0;glGetProgramiv(name,GL_ATTACHED_SHADERS,&count);
    if(count<0 || count>64) return false;
    GLuint names[64];GLsizei actual=0;glGetAttachedShaders(name,64,&actual,names);
    if(actual!=count || !x265_add(out,62,role,name,count,0,0,0,0)) return false;
    for(unsigned i=0;i<(unsigned)count;i++)
        if(!x265_add(out,63,role,name,i,names[i],0,0,0)) return false;
    return glGetError()==GL_NO_ERROR;
}
