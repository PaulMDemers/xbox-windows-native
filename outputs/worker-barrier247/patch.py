"""Apply247 only onto exact compiled246; no production renderer disposal."""
from pathlib import Path
def apply(s):
 def change(name,old,new):
  p=s/name;t=p.read_text();assert t.count(old)==1,(name,old[:80]);p.write_text(t.replace(old,new))
 change('hw/xbox/nv2a/nv2a.h','bool xwn_frontend246_request(bool close);','bool xwn_frontend246_closed(void);\nbool xwn_frontend246_request(bool close);')
 change('ui/xemu.c','bool xwn_frontend246_request(bool close)', '''bool xwn_frontend246_closed(void)
{
    return qatomic_load_acquire(&frontend246_state)==2;
}

bool xwn_frontend246_request(bool close)''')
 change('hw/xbox/nv2a/nv2a_int.h','    bool exiting;', '''    bool exiting;
    struct {
        unsigned state, reason, count, dirty, error;
        bool release, ready, old_halt;
        int64_t deadline;
        uint64_t when, thread, context[2], surfaces[128][6];
        int bindings[2][7];
        unsigned fence[2];
    } worker247;''')
 change('hw/xbox/nv2a/nv2a_int.h','bool nv2a_snapshot238_claim(NV2AState *d);','bool pgraph_gl_worker247(NV2AState *d);\nbool nv2a_snapshot238_claim(NV2AState *d);')
 change('hw/xbox/nv2a/pfifo.c','        pgraph_process_pending(d);','''        if (pgraph_gl_worker247(d)) {
            d->pfifo.fifo_kick=true;
            continue;
        }
        pgraph_process_pending(d);''')
 helper=(Path(__file__).parent/'worker.c').read_text()
 change('hw/xbox/nv2a/pgraph/gl/renderer.c','static void pgraph_gl_process_pending(NV2AState *d)',helper+'\nstatic void pgraph_gl_process_pending(NV2AState *d)')
 change('hw/xbox/nv2a/pgraph/gl/surface.c','        // FIXME: We should download all surfaces to ram, but need to', '''        /*247 Observation only: actual latest flags BEFORE natural invalidation.
         * No inferred bytes, dirty clear or new disposal policy. */
        trace_nv2a_lifecycle244(82,qemu_clock_get_ns(QEMU_CLOCK_REALTIME),qemu_get_thread_id(),(uint64_t)(uintptr_t)s,s->vram_addr,s->size);
        trace_nv2a_lifecycle244(83,qemu_clock_get_ns(QEMU_CLOCK_REALTIME),qemu_get_thread_id(),(uint64_t)(uintptr_t)s,s->gl_buffer,(s->draw_dirty?1:0)|(s->download_pending?2:0)|(s->cpu_write_evict_pending?4:0)|(s->upload_pending?8:0));
        // FIXME: We should download all surfaces to ram, but need to''')
 nv='''static void worker247_set(Object *obj, bool value, Error **errp)
{
    NV2AState *d=NV2A_DEVICE(obj);
    if (!value) {
        unsigned state=qatomic_load_acquire(&d->worker247.state);
        if (state<1 || state>3 ||
            qatomic_cmpxchg(&d->worker247.release,false,true)) {
            error_setg(errp,"247 one release only");return;
        }
        pfifo_kick(d);return;
    }
    if (runstate_is_running() || !xwn_frontend246_closed() ||
        d->pgraph.renderer->type!=CONFIG_DISPLAY_RENDERER_OPENGL ||
        qatomic_load_acquire(&d->worker247.state)!=0) {
        error_setg(errp,"247 needs unused stopped CPU and acknowledged UI gate");return;
    }
    if (qemu_mutex_trylock(&d->pfifo.lock)) {
        error_setg(errp,"247 FIFO busy; not accepted");return;
    }
    d->worker247.old_halt=qatomic_read(&d->pfifo.halt);
    d->worker247.deadline=qemu_clock_get_ns(QEMU_CLOCK_REALTIME)+5000000000LL;
    qatomic_set(&d->pfifo.halt,true);
    qatomic_store_release(&d->worker247.state,1);
    trace_nv2a_lifecycle244(70,qemu_clock_get_ns(QEMU_CLOCK_REALTIME),qemu_get_thread_id(),0,1,0);
    qemu_cond_broadcast(&d->pfifo.fifo_cond);
    qemu_mutex_unlock(&d->pfifo.lock);
}

static char *worker247_report(Object *obj, Error **errp)
{
    NV2AState *d=NV2A_DEVICE(obj);
    unsigned state=qatomic_load_acquire(&d->worker247.state);
    if (!qatomic_load_acquire(&d->worker247.ready)) {
        return g_strdup_printf("version=247 state=%u ready=0",state);
    }
    GString *s=g_string_new(NULL);
    g_string_append_printf(s,"version=247 state=%u ready=1 reason=%u count=%u dirty=%u error=%u when=%"PRIu64" thread=%"PRIu64,
        state,d->worker247.reason,d->worker247.count,d->worker247.dirty,
        d->worker247.error,d->worker247.when,d->worker247.thread);
    for (unsigned n=0;n<2;n++) {
        g_string_append_printf(s," context%u=%"PRIu64" fence%u=%u",n,d->worker247.context[n],n,d->worker247.fence[n]);
        for (unsigned i=0;i<7;i++) {g_string_append_printf(s," binding%u=%d",n*7+i,d->worker247.bindings[n][i]);}
    }
    for (unsigned n=0;n<d->worker247.count;n++) {
        for (unsigned i=0;i<6;i++) {g_string_append_printf(s," surface%u_%u=%"PRIu64,n,i,d->worker247.surfaces[n][i]);}
    }
    return g_string_free(s,false);
}

'''
 change('hw/xbox/nv2a/nv2a.c','static void frontend246_set',nv+'static void frontend246_set')
 change('hw/xbox/nv2a/nv2a.c','    object_property_add_bool(OBJECT(d), "xwn-frontend246-close",', '''    object_property_add_bool(OBJECT(d),"xwn-worker247-close",NULL,worker247_set);
    object_property_add_str(OBJECT(d),"xwn-worker247-report",worker247_report,NULL);
    object_property_add_bool(OBJECT(d), "xwn-frontend246-close",''')
