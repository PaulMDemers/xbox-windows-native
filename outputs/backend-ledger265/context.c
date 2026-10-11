/*265 Shared read-only context observer. Query only; restore ACTIVE_TEXTURE.
 * Rows:30 context header;31 integer binding;32 texture unit/target;33 attribute.
 * No GL object creation/deletion, no binding changes except texture-unit selection.
 */
static bool x265_context(X265Rows *out, unsigned context, int64_t deadline)
{
    static const GLenum integers[] = {
        GL_CURRENT_PROGRAM, GL_VERTEX_ARRAY_BINDING, GL_ARRAY_BUFFER_BINDING,
        GL_ELEMENT_ARRAY_BUFFER_BINDING, GL_DRAW_FRAMEBUFFER_BINDING,
        GL_READ_FRAMEBUFFER_BINDING, GL_RENDERBUFFER_BINDING,
        GL_PIXEL_PACK_BUFFER_BINDING, GL_PIXEL_UNPACK_BUFFER_BINDING,
        GL_COPY_READ_BUFFER_BINDING, GL_COPY_WRITE_BUFFER_BINDING,
        GL_UNIFORM_BUFFER_BINDING, GL_TRANSFORM_FEEDBACK_BUFFER_BINDING
    };
    static const GLenum targets[] = {
        GL_TEXTURE_BINDING_1D, GL_TEXTURE_BINDING_2D, GL_TEXTURE_BINDING_3D,
        GL_TEXTURE_BINDING_CUBE_MAP, GL_TEXTURE_BINDING_RECTANGLE,
        GL_TEXTURE_BINDING_CUBE_MAP_ARRAY,
        GL_TEXTURE_BINDING_1D_ARRAY, GL_TEXTURE_BINDING_2D_ARRAY,
        GL_TEXTURE_BINDING_BUFFER, GL_TEXTURE_BINDING_2D_MULTISAMPLE,
        GL_TEXTURE_BINDING_2D_MULTISAMPLE_ARRAY
    };
    GLint active=0, units=0, attrs=0;
    if (glGetError()!=GL_NO_ERROR) return false; /* Preserve as diagnostic failure. */
    glGetIntegerv(GL_ACTIVE_TEXTURE,&active);
    glGetIntegerv(GL_MAX_COMBINED_TEXTURE_IMAGE_UNITS,&units);
    glGetIntegerv(GL_MAX_VERTEX_ATTRIBS,&attrs);
    if (units<1 || units>256 || attrs<1 || attrs>64) return false;
    x265_add(out,30,context,qemu_get_thread_id(),active,units,attrs,0,0);
    for (unsigned i=0;i<G_N_ELEMENTS(integers);i++) {
        GLint value=0; glGetIntegerv(integers[i],&value);
        x265_add(out,31,context,integers[i],(unsigned)value,0,0,0,0);
    }
    bool okay=true;
    for (unsigned unit=0;unit<(unsigned)units;unit++) {
        if (qemu_clock_get_ns(QEMU_CLOCK_REALTIME)>=deadline) {okay=false;break;}
        glActiveTexture(GL_TEXTURE0+unit);
        for (unsigned t=0;t<G_N_ELEMENTS(targets);t++) {
            GLint value=0; glGetIntegerv(targets[t],&value);
            if (!x265_add(out,32,context,unit,targets[t],(unsigned)value,0,0,0)) {
                okay=false;break;
            }
        }
        if (!okay) break;
    }
    glActiveTexture(active);
    GLint restored=0; glGetIntegerv(GL_ACTIVE_TEXTURE,&restored);
    for (unsigned i=0;okay && i<(unsigned)attrs;i++) {
        GLint enabled=0,buffer=0,stride=0,size=0,type=0;
        void *pointer=NULL;
        glGetVertexAttribiv(i,GL_VERTEX_ATTRIB_ARRAY_ENABLED,&enabled);
        glGetVertexAttribiv(i,GL_VERTEX_ATTRIB_ARRAY_BUFFER_BINDING,&buffer);
        glGetVertexAttribiv(i,GL_VERTEX_ATTRIB_ARRAY_STRIDE,&stride);
        glGetVertexAttribiv(i,GL_VERTEX_ATTRIB_ARRAY_SIZE,&size);
        glGetVertexAttribiv(i,GL_VERTEX_ATTRIB_ARRAY_TYPE,&type);
        glGetVertexAttribPointerv(i,GL_VERTEX_ATTRIB_ARRAY_POINTER,&pointer);
        okay=x265_add(out,33,context,i,enabled,(unsigned)buffer,
            ((uint64_t)(unsigned)stride<<32)|(unsigned)size,type,(uintptr_t)pointer);
    }
    return okay && !out->overflow && restored==active && glGetError()==GL_NO_ERROR;
}
static char *x265_rows_page(const X265Rows *rows, unsigned page, unsigned epoch)
{
    unsigned pages=x265_page_count(rows->count);
    GString *out=g_string_new(NULL);
    g_string_append_printf(out,"version=265 epoch=%u page=%u pages=%u rows=%u overflow=%u",
        epoch,page,pages,rows->count,rows->overflow);
    if (page>=pages) {g_string_append(out," invalid=1");return g_string_free(out,false);}
    unsigned end=MIN(rows->count,(page+1)*X265_PAGE);
    for (unsigned i=page*X265_PAGE;i<end;i++) {
        g_string_append_printf(out," r%u=",i);
        for (unsigned j=0;j<X265_COLUMNS;j++)
            g_string_append_printf(out,"%s%"PRIu64,j?":":"",rows->rows[i][j]);
    }
    return g_string_free(out,false);
}
