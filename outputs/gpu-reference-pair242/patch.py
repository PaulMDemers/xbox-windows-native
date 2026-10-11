"""Paired observations share the sole preservation owner's terminal publication."""
from pathlib import Path
def replace(p,old,new):
 s=p.read_text(encoding='utf-8');assert s.count(old)==1,(p,old)
 p.write_text(s.replace(old,new),encoding='utf-8')
def apply(root):
 k=Path(__file__).resolve().parent;base=root/'hw/xbox/nv2a'
 header=base/'nv2a_int.h'
 replace(header,'typedef struct NV2AState {','''/*242 Separate finite before/after slots; no reuse of238 observer. Owned by
 * the sole227 worker and published by its release-terminal state. Timeout5
 * hides these slots even if a late worker still writes them. */
typedef struct NV2AInventorySlot242 {
    unsigned valid, surface_count, texture_count;
    uint64_t when, fifo_when, fifo[14], context[20], stats[48];
    uint64_t surfaces[128][12], textures[512][10], bindings[4][4];
} NV2AInventorySlot242;

typedef struct NV2AState {''')
 replace(header,'    NV2AWaitSnapshot238 snapshot238;','''    NV2AWaitSnapshot238 snapshot238;
    struct { NV2AInventorySlot242 slots[2]; } inventory242;''')
 nv=base/'nv2a.c'
 report='''/*242 No monitor dereference of live renderer objects. Only worker-published
 * 3/4/6 orders slot writes; report never times out/read-copies mutable slots. */
static char *inventory242_report(Object *obj, Error **errp)
{
    NV2AState *d = NV2A_DEVICE(obj);
    unsigned state = qatomic_load_acquire(&d->preserve227.state);
    bool published = state == 3 || state == 4 || state == 6;
    GString *out = g_string_new(NULL);
    g_string_append_printf(out, "version=242 state=%u published=%u"
        " cpu_callbacks_observed=0 gl_bindings_observed=0 retired=0 native_grant=0",
        state, published);
    if (published) {
        for (unsigned j = 0; j < 2; j++) {
            NV2AInventorySlot242 *v = &d->inventory242.slots[j];
            g_string_append_printf(out, " slot%u_valid=%u", j, v->valid);
            if (!v->valid) { continue; }
            g_string_append_printf(out, " slot%u_when=%" PRIu64
                " slot%u_fifo_when=%" PRIu64 " slot%u_surfaces=%u slot%u_textures=%u",
                j, v->when, j, v->fifo_when, j, v->surface_count, j, v->texture_count);
            for (unsigned i = 0; i < 14; i++) {
                g_string_append_printf(out, " f%u_%u=%" PRIu64, j, i, v->fifo[i]);
            }
            for (unsigned i = 0; i < 20; i++) {
                g_string_append_printf(out, " c%u_%u=%" PRIu64, j, i, v->context[i]);
            }
            for (unsigned i = 0; i < 48; i++) {
                g_string_append_printf(out, " r%u_%u=%" PRIu64, j, i, v->stats[i]);
            }
            for (unsigned i = 0; i < v->surface_count; i++) {
                for (unsigned x = 0; x < 12; x++) {
                    g_string_append_printf(out, " s%u_%u_%u=%" PRIu64, j, i, x, v->surfaces[i][x]);
                }
            }
            for (unsigned i = 0; i < v->texture_count; i++) {
                for (unsigned x = 0; x < 10; x++) {
                    g_string_append_printf(out, " t%u_%u_%u=%" PRIu64, j, i, x, v->textures[i][x]);
                }
            }
            for (unsigned i = 0; i < 4; i++) {
                for (unsigned x = 0; x < 4; x++) {
                    g_string_append_printf(out, " b%u_%u_%u=%" PRIu64, j, i, x, v->bindings[i][x]);
                }
            }
        }
    }
    return g_string_free(out, false);
}

'''
 replace(nv,'static char *preserve227_report',report+'static char *preserve227_report')
 replace(nv,'    object_property_add_bool(OBJECT(d), "xwn-preserve227", preserve227_get,','''    object_property_add_str(OBJECT(d), "xwn-inventory242-report", inventory242_report, NULL);
    object_property_add_bool(OBJECT(d), "xwn-preserve227", preserve227_get,''')
 renderer=base/'pgraph/gl/renderer.c'
 code=(k/'inventory.c').read_text(encoding='utf-8')
 fifo='''/* Caller owns actual FIFO lock; samples bracket the separate PG interval. */
static void inventory242_fifo(NV2AState *d, unsigned slot)
{
    NV2AInventorySlot242 *v = &d->inventory242.slots[slot];
    uint32_t words[10];
    nv2a_preserve231_snapshot(d, words);
    v->fifo_when = qemu_clock_get_ns(QEMU_CLOCK_REALTIME);
    v->fifo[0] = qatomic_read(&d->pfifo.halt);
    v->fifo[1] = d->pfifo.fifo_kick;
    v->fifo[2] = d->pfifo.pending_interrupts;
    v->fifo[3] = d->pfifo.enabled_interrupts;
    for (unsigned i = 0; i < 10; i++) { v->fifo[4+i] = words[i]; }
}

'''
 replace(renderer,'static void pgraph_gl_process_pending',code+'\n'+fifo+'static void pgraph_gl_process_pending')
 replace(renderer,'''                qemu_mutex_unlock(&d->pfifo.lock);
                qemu_mutex_lock(&pg->lock);
                result = pgraph_gl_preserve227(d);
                qemu_mutex_unlock(&pg->lock);
                qemu_mutex_lock(&d->pfifo.lock);''','''                inventory242_fifo(d, 0);
                qemu_mutex_unlock(&d->pfifo.lock);
                qemu_mutex_lock(&pg->lock);
                if (inventory242_copy(d, 0)) {
                    result = pgraph_gl_preserve227(d);
                    if (result == 3 && !inventory242_copy(d, 1)) {
                        qatomic_set(&d->preserve227.reason, 43); result = 6;
                    }
                } else {
                    qatomic_set(&d->preserve227.reason, 42);
                }
                qemu_mutex_unlock(&pg->lock);
                qemu_mutex_lock(&d->pfifo.lock);
                inventory242_fifo(d, 1);''')
