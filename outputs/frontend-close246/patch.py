"""One-shot UI frame admission close; never dispose or grant native ownership."""
def apply(s):
 def change(name, old, new):
  p=s/name;t=p.read_text();assert t.count(old)==1,(name,old[:80]);p.write_text(t.replace(old,new))
 change('hw/xbox/nv2a/nv2a.h','#endif', '''/*246 Diagnostic implemented by the actual UI frame actor. */
bool xwn_frontend246_request(bool close);
char *xwn_frontend246_report(void);
int nv2a_frontend246_loan(void);
#endif''')
 change('hw/xbox/nv2a/pgraph/pgraph.c','int nv2a_get_framebuffer_surface(void)', '''/*246 Try only: no wait under BQL or any other actor lock. */
int nv2a_frontend246_loan(void)
{
    PGRAPHState *pg = &g_nv2a->pgraph;
    if (qemu_mutex_trylock(&pg->renderer_lock)) { return -1; }
    int loan = pg->framebuffer_in_use;
    qemu_mutex_unlock(&pg->renderer_lock);
    return loan;
}

int nv2a_get_framebuffer_surface(void)''')
 helper=(__import__('pathlib').Path(__file__).parent/'frontend.c').read_text()
 change('ui/xemu.c','static void gl_render_frame(struct xemu_console *scon)',helper+'\nstatic void gl_render_frame(struct xemu_console *scon)')
 change('ui/xemu.c','    SDL_GL_MakeCurrent(scon->real_window, scon->winctx);\n\n    bool flip_required', '''    if (frontend246_gate(scon)) {
        qatomic_set(&rendering, false);
        return;
    }

    SDL_GL_MakeCurrent(scon->real_window, scon->winctx);

    bool flip_required''')
 change('ui/xemu.c','    trace_nv2a_lifecycle244(30,', '''    frontend246_last_texture = tex;
    frontend246_last_fallback = release_surface_texture;
    trace_nv2a_lifecycle244(30,''')
 nv='''static void frontend246_set(Object *obj, bool value, Error **errp)
{
    if (!xwn_frontend246_request(value)) {
        error_setg(errp, "246 one close and one reopen, never retry/reset");
    }
}

static char *frontend246_report_get(Object *obj, Error **errp)
{
    return xwn_frontend246_report();
}

'''
 change('hw/xbox/nv2a/nv2a.c','static void lifecycle244_mark_set',nv+'static void lifecycle244_mark_set')
 change('hw/xbox/nv2a/nv2a.c','    object_property_add_bool(OBJECT(d), "xwn-lifecycle244-mark",', '''    object_property_add_bool(OBJECT(d), "xwn-frontend246-close", NULL, frontend246_set);
    object_property_add_str(OBJECT(d), "xwn-frontend246-report", frontend246_report_get, NULL);
    object_property_add_bool(OBJECT(d), "xwn-lifecycle244-mark",''')
