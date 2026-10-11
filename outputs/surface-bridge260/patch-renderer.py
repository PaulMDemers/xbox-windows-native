"""Opt-in260 bridge on frozen259. Never mutate the parent capsule."""
from pathlib import Path

def apply(s):
    k=Path(__file__).resolve().parent
    def append(name,body):
        p=s/name;t=p.read_text();assert 'pattern260' not in t,name
        p.write_text(t+'\n'+body+'\n')
    h=s/'hw/xbox/nv2a/nv2a_int.h';t=h.read_text()
    needle='    bool exiting;\n';assert t.count(needle)==1
    t=t.replace(needle,needle+'    void *pattern260; /* opt-in host metadata, retained until process exit */\n')
    needle='bool pgraph_gl_worker247(NV2AState *d);';assert t.count(needle)==1
    t=t.replace(needle,needle+'''
bool pgraph_gl_pattern260_worker(NV2AState *d);
void pgraph_gl_pattern260_request(NV2AState *d, const char *value, Error **errp);
char *pgraph_gl_pattern260_report(NV2AState *d);
bool pgraph_gl_pattern260_callback_owned(NV2AState *d, MemAccessCallback *cb);
''');h.write_text(t)
    append('hw/xbox/nv2a/pgraph/gl/renderer.c',(k/'callback-check.h').read_text()+'\n'+
        (k/'callback-check.c').read_text().split('\n',1)[1]+'\n'+(k/'bridge.c').read_text())
    append('hw/xbox/nv2a/pgraph/gl/surface.c','''
/* Read only from the CPU-exclusive callback inventory job. */
bool pgraph_gl_pattern260_callback_owned(NV2AState *d, MemAccessCallback *cb)
{
    return cb->mr==d->vram && cb->func==surface_access_callback && cb->opaque==d;
}
''')
    p=s/'hw/xbox/nv2a/nv2a.c';t=p.read_text();assert 'pattern260' not in t
    needle='static void worker247_set(Object *obj, bool value, Error **errp)'
    assert t.count(needle)==1
    t=t.replace(needle,'''static void pattern260_set(Object *obj, const char *value, Error **errp)
{
    pgraph_gl_pattern260_request(NV2A_DEVICE(obj), value, errp);
}
static char *pattern260_report(Object *obj, Error **errp)
{
    return pgraph_gl_pattern260_report(NV2A_DEVICE(obj));
}

'''+needle)
    needle='    object_property_add_bool(OBJECT(d),"xwn-worker247-close",NULL,worker247_set);'
    assert t.count(needle)==1
    t=t.replace(needle,'''    object_property_add_str(OBJECT(d),"xwn-pattern260",NULL,pattern260_set);
    object_property_add_str(OBJECT(d),"xwn-pattern260-report",pattern260_report,NULL);
'''+needle);p.write_text(t)
    p=s/'hw/xbox/nv2a/pfifo.c';t=p.read_text();assert 'pattern260' not in t
    needle='        if (pgraph_gl_worker247(d)) {';assert t.count(needle)==1
    t=t.replace(needle,'''        if (pgraph_gl_pattern260_worker(d)) {
            d->pfifo.fifo_kick=true;
            continue;
        }
'''+needle);p.write_text(t)
