"""Diagnostic-only child of the exact265 source. No object disposal or joins."""
from pathlib import Path
k=Path(__file__).resolve().parent
def replace(p,old,new):
    t=p.read_text();assert t.count(old)==1,(str(p),old);p.write_text(t.replace(old,new))
def apply(root):
    gl=root/'hw/xbox/nv2a/pgraph/gl'
    p=gl/'renderer.h'
    replace(p,'typedef struct ShaderBinding {',(k/'actor-core.h').read_text()+'\nunsigned pgraph_gl_actor267_overflow(void);\n\ntypedef struct ShaderBinding {')
    replace(p,'    QemuThread *save_thread;','    QemuThread *save_thread;\n    X267Actor *actor267;')
    replace(p,'    QemuThread shader_disk_thread;','    QemuThread shader_disk_thread;\n    X267Actor *loader267;')
    p=gl/'shaders.c'
    replace(p,'static void *shader_reload_lru_from_disk(void *arg)',(k/'actors.c').read_text()+'\nstatic void *shader_reload_lru_from_disk(void *arg)')
    replace(p,'    binding->save_thread = NULL;\n}', '    binding->save_thread = NULL;\n    binding->actor267 = NULL;\n}')
    replace(p,'    qemu_thread_create(binding->save_thread, name, shader_write_to_disk, binding, QEMU_THREAD_JOINABLE);',
              '    x267_create(binding->save_thread,name,shader_write_to_disk,binding,1,&binding->actor267);')
    replace(p,'    qemu_thread_create(&r->shader_disk_thread, "pgraph.renderer_state->shader_cache",\n                       shader_reload_lru_from_disk, pg, QEMU_THREAD_JOINABLE);',
              '    x267_create(&r->shader_disk_thread,"pgraph.renderer_state->shader_cache",\n                shader_reload_lru_from_disk,pg,2,&r->loader267);')
    off=root/'hw/xbox/nv2a/pgraph/thirdparty/gloffscreen'
    replace(off/'gloffscreen.h','#include <stdbool.h>','#include <stdbool.h>\n#include <stdint.h>')
    replace(off/'gloffscreen.h','void glo_set_current(GloContext *context);','void glo_set_current(GloContext *context);\nbool glo_context_observe267(GloContext *context,uintptr_t out[4]);')
    p=off/'sdl.c';p.write_text(p.read_text()+'''
/*267 Actual native identities, queried on the owning current-context thread. */
bool glo_context_observe267(GloContext *context,uintptr_t out[4])
{
    out[0]=(uintptr_t)(context?context->gl_context:NULL);
    out[1]=(uintptr_t)SDL_GL_GetCurrentContext();
    out[2]=(uintptr_t)(context?context->window:NULL);
    out[3]=(uintptr_t)SDL_GL_GetCurrentWindow();
    return out[0] && out[0]==out[1] && out[2] && out[2]==out[3];
}
''')
    extra=(k/'context-extra.c').read_text()
    p=gl/'renderer.c'
    helper='''
static bool x267_actor(X265State *s,uintptr_t owner,X267Actor *a,unsigned kind)
{
    unsigned state=x267_state(a);
    /* acquire>=2 publishes thread; state1 has immutable identity but no thread. */
    if(!a || a->owner!=owner || a->kind!=kind || !a->epoch || state<1 || state>3) return false;
    if(state!=3) s->shader_jobs_unknown++;
    return x265_add(&s->ledger,50,owner,(uintptr_t)a,a->epoch,state,
                    state>=2?a->thread:0,kind,(uintptr_t)a->function);
}
static bool x267_context(X265Rows *out,PGRAPHGLState *r,unsigned role,int64_t deadline)
{
    uintptr_t ids[4];GloContext *ctx=role==1?g_nv2a_context_render:g_nv2a_context_display;
    bool match=glo_context_observe267(ctx,ids);
    if(!x265_add(out,51,role,(uintptr_t)ctx,ids[0],ids[1],ids[2],ids[3],match) || !match) return false;
    if(!x267_indexed(out,role,deadline)) return false;
    if(role==1) {
        return x267_fbo(out,role,r->gl_framebuffer,deadline) &&
               x267_fbo(out,role,r->s2t_rndr.fbo,deadline) &&
               x267_vao(out,role,r->gl_vertex_array,deadline) &&
               x267_vao(out,role,r->s2t_rndr.vao,deadline) &&
               x267_program(out,role,r->s2t_rndr.prog);
    }
    return x267_fbo(out,role,r->disp_rndr.fbo,deadline) &&
           x267_vao(out,role,r->disp_rndr.vao,deadline) &&
           x267_program(out,role,r->disp_rndr.prog);
}
'''
    replace(p,'static bool x265_binding(X265State *s,TextureBinding *binding,bool unit)',extra+'\n'+helper+'\nstatic bool x265_binding(X265State *s,TextureBinding *binding,bool unit)')
    replace(p,'        if (b->save_thread) s->shader_jobs_unknown++;','''        if (b->save_thread && !x267_actor(s,(uintptr_t)b,b->actor267,1)) {okay=false;break;}
        if (b->initialized && !x267_program(out,1,b->gl_program)) {okay=false;break;}''')
    replace(p,'    /* Loader completion is not instrumented in this read-only diagnostic. */\n    s->shader_jobs_unknown++;','''    if (!x267_actor(s,(uintptr_t)pg,r->loader267,2) || pgraph_gl_actor267_overflow()) okay=false;''')
    replace(p,'    if (!x265_context(&s->ledger,1,v->deadline)) {reason=8;goto finish;}',
        '    if (!x265_context(&s->ledger,1,v->deadline) || !x267_context(&s->ledger,r,1,v->deadline)) {reason=8;goto finish;}')
    replace(p,'    bool context_ok=x265_context(&s->ledger,2,v->deadline);','    bool context_ok=x265_context(&s->ledger,2,v->deadline) && x267_context(&s->ledger,r,2,v->deadline);')
    p=root/'ui/xemu.c'
    replace(p,'static void x265_ui_capture(void)',extra+'\nstatic void x265_ui_capture(struct xemu_console *scon)')
    replace(p,'    if (!x265_context(&ui265_rows,3,deadline)) ui265_error=2;','''    /* VGA surface metadata is read under its ordinary BQL owner lock. */
    xemu_main_loop_lock();
    DisplaySurface *surface=scon->surface;
    bool owner=x265_add(&ui265_rows,64,(uintptr_t)scon,(uintptr_t)surface,
        surface?surface->texture:0,surface?surface_width(surface):0,
        surface?surface_height(surface):0,(uintptr_t)scon->winctx,(uintptr_t)scon->real_window);
    xemu_main_loop_unlock();
    owner &= x265_add(&ui265_rows,65,(uintptr_t)SDL_GL_GetCurrentContext(),
        (uintptr_t)SDL_GL_GetCurrentWindow(),(uintptr_t)scon->winctx,
        (uintptr_t)scon->real_window,0,0,0);
    GLint fbo=0,read=0,vao=0,program=0;
    glGetIntegerv(GL_DRAW_FRAMEBUFFER_BINDING,&fbo);glGetIntegerv(GL_READ_FRAMEBUFFER_BINDING,&read);
    glGetIntegerv(GL_VERTEX_ARRAY_BINDING,&vao);glGetIntegerv(GL_CURRENT_PROGRAM,&program);
    if (!owner || !x265_context(&ui265_rows,3,deadline) ||
        !x267_indexed(&ui265_rows,3,deadline) || !x267_fbo(&ui265_rows,3,fbo,deadline) ||
        (read!=fbo && !x267_fbo(&ui265_rows,3,read,deadline)) ||
        !x267_vao(&ui265_rows,3,vao,deadline) || !x267_program(&ui265_rows,3,program)) ui265_error=2;''')
    replace(p,'            x265_ui_capture();','            x265_ui_capture(scon);')
