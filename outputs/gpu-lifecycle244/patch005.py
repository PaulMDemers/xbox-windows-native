"""Observation only: log actual callback unlink/free and frontend fence paths."""
from pathlib import Path

def apply(s):
 def change(name, old, new):
  p=s/name;t=p.read_text(encoding='utf-8');assert t.count(old)==1,(name,old[:90]);p.write_text(t.replace(old,new),encoding='utf-8')
 def nv(phase,ref='0',a='0',b='0'):
  return f'trace_nv2a_lifecycle244({phase}, qemu_clock_get_ns(QEMU_CLOCK_REALTIME), qemu_get_thread_id(), (uint64_t)(uintptr_t)({ref}), {a}, {b});'
 def cpu(phase,ref='cb',addr='cb->addr',length='cb->len'):
  return f'trace_xwn_mem_callback244({phase}, qemu_clock_get_ns(QEMU_CLOCK_REALTIME), qemu_get_thread_id(), (uint64_t)(uintptr_t)({ref}), {addr}, {length}, qatomic_read(&cpu->stopped));'
 change('system/trace-events','# balloon.c', 'xwn_mem_callback244(int phase, uint64_t when, uint64_t thread, uint64_t ref, uint64_t addr, uint64_t len, int stopped) "phase=%d when=%"PRIu64" thread=%"PRIu64" ref=%"PRIu64" addr=%"PRIu64" len=%"PRIu64" stopped=%d"\n\n# balloon.c')
 change('hw/xbox/nv2a/trace-events','# nv2a.c', 'nv2a_lifecycle244(int phase, uint64_t when, uint64_t thread, uint64_t ref, uint64_t a, uint64_t b) "phase=%d when=%"PRIu64" thread=%"PRIu64" ref=%"PRIu64" a=%"PRIu64" b=%"PRIu64\n\n# nv2a.c')
 change('system/physmem.c','    QTAILQ_INSERT_TAIL(&cpu->mem_access_callbacks, cb, entry);','    QTAILQ_INSERT_TAIL(&cpu->mem_access_callbacks, cb, entry);\n    '+cpu(2))
 change('system/physmem.c','    async_safe_run_on_cpu(cpu, do_mem_access_callback_insert,','    '+cpu(1)+'\n    async_safe_run_on_cpu(cpu, do_mem_access_callback_insert,')
 change('system/physmem.c','    QTAILQ_REMOVE(&cpu->mem_access_callbacks, cb, entry);\n    g_free(cb);',
        '    /*244 Copy scalar identity before actual unlink/free; never dereference later. */\n    uint64_t identity = (uintptr_t)cb;\n    uint64_t addr = cb->addr, len = cb->len;\n    QTAILQ_REMOVE(&cpu->mem_access_callbacks, cb, entry);\n    '+cpu(4,'identity','addr','len')+'\n    g_free(cb);\n    '+cpu(5,'identity','addr','len'))
 change('system/physmem.c','    async_safe_run_on_cpu(cpu, do_mem_access_callback_remove_by_ref,','    '+cpu(3)+'\n    async_safe_run_on_cpu(cpu, do_mem_access_callback_remove_by_ref,')
 change('hw/xbox/nv2a/pgraph/gl/surface.c','                &surface_access_callback, d);','                &surface_access_callback, d);\n            '+nv(1,'surface->access_cb','surface->vram_addr','surface->size'))
 change('hw/xbox/nv2a/pgraph/gl/surface.c','    trace_nv2a_pgraph_surface_invalidated(surface->vram_addr);',
        '    /*244 Scalar observation survives the existing disposal, not a new owner. */\n    uint64_t cb244 = (uintptr_t)surface->access_cb;\n    uint64_t addr244 = surface->vram_addr, size244 = surface->size;\n    '+nv(2,'cb244','addr244','size244')+'\n    trace_nv2a_pgraph_surface_invalidated(surface->vram_addr);')
 change('hw/xbox/nv2a/pgraph/gl/surface.c','    g_free(surface);\n}', '    g_free(surface);\n    '+nv(3,'cb244','addr244','size244')+'\n}')
 change('hw/xbox/nv2a/pgraph/gl/surface.c','    /* Clear last surface shape to force recreation of buffers at next draw */','    '+nv(4)+'\n    /* Clear last surface shape to force recreation of buffers at next draw */')
 change('hw/xbox/nv2a/pgraph/gl/surface.c','        pgraph_gl_surface_invalidate(d, s);\n    }\n}\n\nvoid pgraph_gl_finalize_surfaces','        pgraph_gl_surface_invalidate(d, s);\n    }\n    '+nv(5)+'\n}\n\nvoid pgraph_gl_finalize_surfaces')
 change('hw/xbox/nv2a/pgraph/pgraph.c','    pg->framebuffer_in_use = true;','    pg->framebuffer_in_use = true;\n    '+nv(10))
 change('hw/xbox/nv2a/pgraph/pgraph.c','    return s;\n}\n\nvoid nv2a_release_framebuffer_surface','    '+nv(11,'s')+'\n    return s;\n}\n\nvoid nv2a_release_framebuffer_surface')
 change('hw/xbox/nv2a/pgraph/pgraph.c','    pg->framebuffer_in_use = false;\n    qemu_cond_broadcast','    pg->framebuffer_in_use = false;\n    '+nv(12)+'\n    qemu_cond_broadcast')
 change('hw/xbox/nv2a/pgraph/gl/display.c','void pgraph_gl_sync(NV2AState *d)\n{','void pgraph_gl_sync(NV2AState *d)\n{\n    '+nv(20,'0','d->pcrtc.start','qatomic_read(&d->pgraph.sync_pending)'))
 change('hw/xbox/nv2a/pgraph/gl/display.c','        qemu_event_set(&d->pgraph.sync_complete);\n        return;','        qemu_event_set(&d->pgraph.sync_complete);\n        '+nv(21,'0','0','qatomic_read(&d->pgraph.sync_pending)')+'\n        return;')
 change('hw/xbox/nv2a/pgraph/gl/display.c','    qatomic_set(&d->pgraph.sync_pending, false);','    '+nv(22,'surface->gl_buffer')+'\n    qatomic_set(&d->pgraph.sync_pending, false);')
 change('ui/xemu.c','#include "hw/xbox/nv2a/nv2a.h"','#include "hw/xbox/nv2a/nv2a.h"\n#include "hw/xbox/nv2a/trace.h"\n#include "qemu/timer.h"')
 change('ui/xemu.c','    glClearColor(0, 0, 0, 0);','    '+nv(30,'tex','release_surface_texture')+'\n    glClearColor(0, 0, 0, 0);')
 change('ui/xemu.c','    xemu_hud_render();\n    glFinish();','    xemu_hud_render();\n    glFinish();\n    '+nv(31,'tex','release_surface_texture'))
 change('ui/xemu.c','    nv2a_release_framebuffer_surface();','    nv2a_release_framebuffer_surface();\n    '+nv(32,'tex','release_surface_texture'))
 # Only diagnostic marker count. No reference, admission or guest-state mutation.
 change('hw/xbox/nv2a/nv2a_int.h', '    bool exiting;', '    bool exiting;\n    unsigned lifecycle244_marks;')
 change('hw/xbox/nv2a/nv2a_int.h', '} NV2AState;', '} NV2AState;\nG_STATIC_ASSERT(offsetof(NV2AState, parent_obj) == 0);')
 marker='''static void lifecycle244_mark_set(Object *obj, bool value, Error **errp)
{
    NV2AState *d = NV2A_DEVICE(obj);
    if (!value || d->lifecycle244_marks >= 2) {
        error_setg(errp, "244 only two true markers, never reset/replay");
        return;
    }
    ++d->lifecycle244_marks;
    trace_nv2a_lifecycle244(40 + d->lifecycle244_marks,
        qemu_clock_get_ns(QEMU_CLOCK_REALTIME), qemu_get_thread_id(), 0, 0, 0);
}

'''
 p=s/'hw/xbox/nv2a/nv2a.c';t=p.read_text();anchor='static void preserve227_set';assert t.count(anchor)==1;t=t.replace(anchor,marker+anchor)
 anchor='    object_property_add_bool(OBJECT(d), "xwn-snapshot238"';assert t.count(anchor)==1;t=t.replace(anchor,'    object_property_add_bool(OBJECT(d), "xwn-lifecycle244-mark", NULL, lifecycle244_mark_set);\n'+anchor);p.write_text(t)
