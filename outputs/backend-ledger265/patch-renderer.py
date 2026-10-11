"""Append opt-in observation to exact263. Never alter ordinary disposal paths."""
from pathlib import Path

HERE = Path(__file__).resolve().parent

def replace(path, old, new):
    text = path.read_text()
    assert text.count(old) == 1, (str(path), old)
    path.write_text(text.replace(old, new))

def apply(root):
    shared = (HERE/'ledger-core.h').read_text() + '\n' + (HERE/'context.c').read_text()
    p = root/'hw/xbox/nv2a/pgraph/gl/renderer.c'
    p.write_text(p.read_text() + '\n' + shared + '\n' + (HERE/'renderer.c').read_text())
    p = root/'hw/xbox/nv2a/nv2a_int.h'
    replace(p,'    void *pattern260; /* opt-in host metadata, retained until process exit */',
        '    void *ledger265; /* immutable observation only; process lifetime */\n'
        '    unsigned ui265_page; /* monitor-only immutable read cursor */\n'
        '    void *pattern260; /* opt-in host metadata, retained until process exit */')
    prototypes = '''bool pgraph_gl_ledger265_worker(NV2AState *d);
void pgraph_gl_ledger265_request(NV2AState *d,const char *value,Error **errp);
void pgraph_gl_ledger265_page(NV2AState *d,const char *value,Error **errp);
char *pgraph_gl_ledger265_report(NV2AState *d);
char *pgraph_gl_ledger265_data(NV2AState *d);
char *xwn_ui265_report(void);
char *xwn_ui265_data(unsigned page);
'''
    replace(p,'bool pgraph_gl_pattern260_worker(NV2AState *d);',prototypes+'bool pgraph_gl_pattern260_worker(NV2AState *d);')
    p = root/'hw/xbox/nv2a/pfifo.c'
    replace(p,'        if (pgraph_gl_pattern260_worker(d)) {',
        '        if (pgraph_gl_ledger265_worker(d)) {\n'
        '            d->pfifo.fifo_kick=true;\n            continue;\n        }\n'
        '        if (pgraph_gl_pattern260_worker(d)) {')
    p = root/'hw/xbox/nv2a/nv2a.c'
    replace(p,'#include "qemu/main-loop.h"','#include "qemu/main-loop.h"\n#include "qemu/cutils.h"')
    wrappers = '''static void ledger265_set(Object *obj,const char *value,Error **errp)
{ pgraph_gl_ledger265_request(NV2A_DEVICE(obj),value,errp); }
static void ledger265_page_set(Object *obj,const char *value,Error **errp)
{ pgraph_gl_ledger265_page(NV2A_DEVICE(obj),value,errp); }
static char *ledger265_report(Object *obj,Error **errp)
{ return pgraph_gl_ledger265_report(NV2A_DEVICE(obj)); }
static char *ledger265_data(Object *obj,Error **errp)
{ return pgraph_gl_ledger265_data(NV2A_DEVICE(obj)); }
static char *ui265_report(Object *obj,Error **errp)
{ return xwn_ui265_report(); }
static char *ui265_data(Object *obj,Error **errp)
{ return xwn_ui265_data(NV2A_DEVICE(obj)->ui265_page); }
static void ui265_page_set(Object *obj,const char *value,Error **errp)
{
    uint64_t page=0;const char *end=NULL;
    if (qemu_strtou64(value,&end,10,&page) || !end || *end || page>=32) {
        error_setg(errp,"265 invalid UI page");return;
    }
    NV2A_DEVICE(obj)->ui265_page=page;
}
'''
    replace(p,'static void pattern260_set(Object *obj, const char *value, Error **errp)',
        wrappers+'\nstatic void pattern260_set(Object *obj, const char *value, Error **errp)')
    anchor='    object_property_add_str(OBJECT(d),"xwn-pattern260",NULL,pattern260_set);'
    replace(p,anchor,'''    object_property_add_str(OBJECT(d),"xwn-ledger265",NULL,ledger265_set);
    object_property_add_str(OBJECT(d),"xwn-ledger265-page",ledger265_data,ledger265_page_set);
    object_property_add_str(OBJECT(d),"xwn-ledger265-report",ledger265_report,NULL);
    object_property_add_str(OBJECT(d),"xwn-ui265-page",ui265_data,ui265_page_set);
    object_property_add_str(OBJECT(d),"xwn-ui265-report",ui265_report,NULL);
'''+anchor)
    p=root/'ui/xemu.c'
    replace(p,'static void frontend246_trace(int phase, uint64_t a, uint64_t b)',
        shared+'\n'+(HERE/'ui.c').read_text()+'\nstatic void frontend246_trace(int phase, uint64_t a, uint64_t b)')
    anchor='            frontend246_record.texture_live = glIsTexture(frontend246_record.texture);'
    replace(p,anchor,anchor+'\n            x265_ui_capture();\n'
        '            if (ui265_error) frontend246_record.error=7;')
    for name,variable,function in [('ui/xui/main.cc','g_tex','xwn_hud265_texture'),
                                  ('ui/xemu-thumbnail.cc','display_tex','xwn_thumbnail265_texture')]:
        p=root/name
        p.write_text(p.read_text()+f'\n/*265 Read by the actual UI actor only. */\nextern "C" unsigned {function}(void) {{ return {variable}; }}\n')
