/*
 * Geforce NV2A PGRAPH OpenGL Renderer
 *
 * Copyright (c) 2012 espes
 * Copyright (c) 2015 Jannik Vogel
 * Copyright (c) 2018-2025 Matt Borgerson
 *
 * This library is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free Software Foundation; either
 * version 2 of the License, or (at your option) any later version.
 *
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public
 * License along with this library; if not, see <http://www.gnu.org/licenses/>.
 */

#include "hw/xbox/nv2a/nv2a_int.h"
#include "hw/xbox/nv2a/pgraph/pgraph.h"
#include "debug.h"
#include "renderer.h"

GloContext *g_nv2a_context_render;
GloContext *g_nv2a_context_display;

static void early_context_init(void)
{
    g_nv2a_context_render = glo_context_create();
    g_nv2a_context_display = glo_context_create();

    // Note: Due to use of shared contexts, this must happen after some other
    // context is created so the temporary context will not become the thread
    // context. After destroying the context, some a durable context should be
    // selected.
    GloContext *context = glo_context_create();
    pgraph_gl_determine_gpu_properties();
    glo_context_destroy(context);
    glo_set_current(g_nv2a_context_display);
}

static void pgraph_gl_init(NV2AState *d, Error **errp)
{
    PGRAPHState *pg = &d->pgraph;

    pg->gl_renderer_state = g_malloc0(sizeof(*pg->gl_renderer_state));
    PGRAPHGLState *r = pg->gl_renderer_state;

    /* fire up opengl */
    glo_set_current(g_nv2a_context_render);

#if DEBUG_NV2A_GL
    gl_debug_initialize();
#endif

    /* DXT textures */
    assert(glo_check_extension("GL_EXT_texture_compression_s3tc"));
    /*  Internal RGB565 texture format */
    assert(glo_check_extension("GL_ARB_ES2_compatibility"));

    glGetFloatv(GL_SMOOTH_LINE_WIDTH_RANGE, r->supported_smooth_line_width_range);
    glGetFloatv(GL_ALIASED_LINE_WIDTH_RANGE, r->supported_aliased_line_width_range);

    pgraph_gl_init_surfaces(pg);
    pgraph_gl_init_reports(d);
    pgraph_gl_init_textures(d);
    pgraph_gl_init_buffers(d);
    pgraph_gl_init_shaders(pg);
    pgraph_gl_init_display(d);

    pgraph_gl_update_entire_memory_buffer(d);

    pg->uniform_attrs = 0;
    pg->swizzle_attrs = 0;

    r->supported_extensions.texture_filter_anisotropic =
        glo_check_extension("GL_EXT_texture_filter_anisotropic");
}

static void pgraph_gl_finalize(NV2AState *d)
{
    PGRAPHState *pg = &d->pgraph;

    glo_set_current(g_nv2a_context_render);

    pgraph_gl_finalize_surfaces(pg);
    pgraph_gl_finalize_shaders(pg);
    pgraph_gl_finalize_textures(pg);
    pgraph_gl_finalize_reports(pg);
    pgraph_gl_finalize_buffers(pg);
    pgraph_gl_finalize_display(pg);

    glo_set_current(NULL);

    g_free(pg->gl_renderer_state);
    pg->gl_renderer_state = NULL;
}

static void pgraph_gl_flip_stall(NV2AState *d)
{
    NV2A_GL_DFRAME_TERMINATOR();
    glFinish();
}

static void pgraph_gl_flush(NV2AState *d)
{
    pgraph_gl_surface_flush(d);
    pgraph_gl_mark_textures_possibly_dirty(d, 0, memory_region_size(d->vram));
    pgraph_gl_update_entire_memory_buffer(d);
    /* FIXME: Flush more? */

    qatomic_set(&d->pgraph.flush_pending, false);
    qemu_event_set(&d->pgraph.flush_complete);
}

/*242 Read-only paired inventory. Caller owns renderer and PG locks, FIFO
 * admission already closed. Shader lock is TRY only. This does not query GL
 * bindings, retire references, join workers or inspect CPU callback queues. */
static bool inventory242_alive(NV2AState *d)
{
    return qatomic_load_acquire(&d->preserve227.state) == 2 &&
        qemu_clock_get_ns(QEMU_CLOCK_REALTIME) < d->preserve227.deadline;
}

static bool inventory242_copy(NV2AState *d, unsigned slot)
{
    if (slot >= 2 || !inventory242_alive(d)) { return false; }
    PGRAPHState *pg = &d->pgraph;
    PGRAPHGLState *r = pg->gl_renderer_state;
    NV2AInventorySlot242 *v = &d->inventory242.slots[slot];
    if (!r || v->valid || qemu_mutex_trylock(&r->shader_cache_lock)) {
        return false;
    }
    v->when = qemu_clock_get_ns(QEMU_CLOCK_REALTIME);
    NV2AWaitRow233 row;
    nv2a_wait233_fill(d, &row, 9, 0, false);
    uint64_t context[20] = {
        pg->primitive_mode, pg->draw_arrays_length, pg->inline_array_length,
        pg->inline_elements_length, pg->inline_buffer_length,
        pg->framebuffer_in_use, qatomic_read(&pg->flush_pending),
        qatomic_read(&pg->sync_pending), pgraph_reg_r(pg, NV_PGRAPH_CTX_USER),
        pgraph_reg_r(pg, NV_PGRAPH_SURFACE), pg->dma_color, pg->dma_zeta,
        pg->context_surfaces_2d.object_instance,
        pg->context_surfaces_2d.dma_image_source,
        pg->context_surfaces_2d.dma_image_dest, pg->image_blit.context_surfaces,
        r != NULL, pg->renderer->type, r->color_binding != NULL,
        r->zeta_binding != NULL,
    };
    memcpy(v->context, context, sizeof(context));
    uint64_t stats[48] = {
        qatomic_read(&d->pfifo.halt), row.waits, row.pending, row.enabled,
        qatomic_read(&r->downloads_pending),
        qatomic_read(&r->download_dirty_surfaces_pending),
        qatomic_read(&r->shader_cache_writeback_pending),
        r->gl_framebuffer, r->gl_display_buffer,
        r->gl_display_buffer_width, r->gl_display_buffer_height,
        g_nv2a_context_render != NULL, g_nv2a_context_display != NULL,
        r->texture_cache.num_used, r->texture_cache.num_free,
        r->shader_cache.num_used, r->shader_cache.num_free,
        r->shader_module_cache.num_used, r->shader_module_cache.num_free,
        r->element_cache.num_used, r->element_cache.num_free,
        r->shader_binding != NULL,
        r->shader_binding && r->shader_binding->initialized ?
            r->shader_binding->gl_program : 0,
        r->gl_inline_array_buffer, r->gl_memory_buffer, r->gl_vertex_array,
        r->disp_rndr.fbo, r->disp_rndr.vao, r->disp_rndr.vbo,
        r->disp_rndr.prog, r->disp_rndr.pvideo_tex,
        r->s2t_rndr.fbo, r->s2t_rndr.vao, r->s2t_rndr.vbo, r->s2t_rndr.prog,
        r->gl_zpass_pixel_count_query_count,
    };
    memcpy(v->stats, stats, sizeof(stats));
    for (unsigned i = 0; i < NV2A_VERTEXSHADER_ATTRIBUTES; i++) {
        v->stats[36] += r->gl_inline_buffer[i] != 0;
    }
    for (unsigned i = 0; i < NV2A_MAX_TEXTURES; i++) {
        TextureBinding *b = r->texture_binding[i];
        v->bindings[i][0] = b != NULL;
        if (b) {
            v->bindings[i][1] = b->gl_texture;
            v->bindings[i][2] = b->refcnt;
            v->bindings[i][3] = b->gl_target;
        }
    }
    bool ok = true;
    SurfaceBinding *s;
    QTAILQ_FOREACH(s, &r->surfaces, entry) {
        if (v->surface_count == 128 || !inventory242_alive(d)) {
            ok = false; break;
        }
        uint64_t fields[12] = {
            s->vram_addr, s->size, s->pitch, s->width, s->height,
            (s->draw_dirty ? 1 : 0) | (s->download_pending ? 2 : 0) |
            (s->cpu_write_evict_pending ? 4 : 0) | (s->upload_pending ? 8 : 0) |
            (s->cleared ? 16 : 0) | (s->color ? 32 : 0) | (s->swizzle ? 64 : 0),
            s->access_cb != NULL, s == r->color_binding,
            s == r->zeta_binding, s->gl_buffer, s->dma_addr, s->dma_len,
        };
        memcpy(v->surfaces[v->surface_count++], fields, sizeof(fields));
    }
    LruNode *node;
    unsigned walked = 0;
    QTAILQ_FOREACH(node, &r->texture_cache.global, next_global) {
        if (walked == 512 || !inventory242_alive(d)) { ok = false; break; }
        walked++;
        if (!lru_is_node_in_use(&r->texture_cache, node)) { continue; }
        TextureLruNode *t = container_of(node, TextureLruNode, node);
        TextureBinding *b = t->binding;
        uint64_t fields[10] = {
            t->key.texture_vram_offset, t->key.texture_length,
            t->key.palette_vram_offset, t->key.palette_length,
            b != NULL, b ? b->gl_texture : 0, b ? b->refcnt : 0,
            t->possibly_dirty, b ? b->gl_target : 0, node->hash,
        };
        memcpy(v->textures[v->texture_count++], fields, sizeof(fields));
    }
    v->stats[37] = walked;
    ok &= r->texture_cache.num_used >= 0 &&
          v->texture_count == (unsigned)r->texture_cache.num_used;
    walked = 0;
    QTAILQ_FOREACH(node, &r->shader_cache.global, next_global) {
        if (walked == 51200 || !inventory242_alive(d)) { ok = false; break; }
        walked++;
        if (!lru_is_node_in_use(&r->shader_cache, node)) { continue; }
        ShaderBinding *b = container_of(node, ShaderBinding, node);
        v->stats[38]++;
        v->stats[39] += b->initialized;
        v->stats[40] += b->program != NULL;
        /* A non-null save handle does NOT say the thread is still running. */
        v->stats[41] += b->save_thread != NULL;
    }
    v->stats[42] = walked;
    ok &= r->shader_cache.num_used >= 0 &&
          v->stats[38] == (uint64_t)r->shader_cache.num_used;
    walked = 0;
    QTAILQ_FOREACH(node, &r->shader_module_cache.global, next_global) {
        if (walked == 51200 || !inventory242_alive(d)) { ok = false; break; }
        walked++;
        if (lru_is_node_in_use(&r->shader_module_cache, node)) { v->stats[43]++; }
    }
    v->stats[44] = walked;
    ok &= r->shader_module_cache.num_used >= 0 &&
          v->stats[43] == (uint64_t)r->shader_module_cache.num_used;
    walked = 0;
    QTAILQ_FOREACH(node, &r->element_cache.global, next_global) {
        if (walked == 51200 || !inventory242_alive(d)) { ok = false; break; }
        walked++;
        if (!lru_is_node_in_use(&r->element_cache, node)) { continue; }
        VertexLruNode *b = container_of(node, VertexLruNode, node);
        v->stats[45]++;
        v->stats[46] += b->initialized;
    }
    v->stats[47] = walked;
    ok &= r->element_cache.num_used >= 0 &&
          v->stats[45] == (uint64_t)r->element_cache.num_used;
    qemu_mutex_unlock(&r->shader_cache_lock);
    v->valid = ok && inventory242_alive(d);
    return v->valid;
}

/* Caller owns actual FIFO lock; samples bracket the separate PG interval. */
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

/*247 One-shot worker checkpoint. Entry/exit own FIFO; all fence waits own NONE
 * of BQL/FIFO/PG/renderer locks. The stopped CPU and acknowledged UI gate are
 * mandatory. No delete, cache flush, dirty clear, callback retirement or permit.
 * State0 unused,1 requested,2 capturing,3 parked,5 released,6 refused/expired.
 * ready publishes an immutable scalar/object record once, independently state.
 */
static void worker247_trace(unsigned phase, uint64_t key, uint64_t a, uint64_t b)
{
    trace_nv2a_lifecycle244(phase, qemu_clock_get_ns(QEMU_CLOCK_REALTIME),
                          qemu_get_thread_id(), key, a, b);
}

static bool worker247_alive(NV2AState *d)
{
    return !qatomic_load_acquire(&d->worker247.release) &&
        qemu_clock_get_ns(QEMU_CLOCK_REALTIME) < d->worker247.deadline &&
        xwn_frontend246_closed();
}

static bool worker247_context(NV2AState *d, unsigned index, GloContext *context)
{
    if (!context || !worker247_alive(d) || bql_locked()) { return false; }
    glo_set_current(context);
    d->worker247.context[index] = (uint64_t)(uintptr_t)context;
    const GLenum fields[7] = { GL_TEXTURE_BINDING_2D, GL_CURRENT_PROGRAM,
        GL_ARRAY_BUFFER_BINDING, GL_ELEMENT_ARRAY_BUFFER_BINDING,
        GL_DRAW_FRAMEBUFFER_BINDING, GL_VERTEX_ARRAY_BINDING, GL_ACTIVE_TEXTURE };
    for (unsigned i=0;i<7;i++) {
        glGetIntegerv(fields[i], &d->worker247.bindings[index][i]);
        worker247_trace(73, index*7+i, d->worker247.bindings[index][i],
                        d->worker247.context[index]);
    }
    GLenum error=glGetError();
    if (error) { d->worker247.error=error; return false; }
    GLsync fence=glFenceSync(GL_SYNC_GPU_COMMANDS_COMPLETE,0);
    if (!fence) { return false; }
    worker247_trace(74,index,100000000,0);
    GLenum result=glClientWaitSync(fence,GL_SYNC_FLUSH_COMMANDS_BIT,100000000);
    glDeleteSync(fence); /* Only the newly-created diagnostic fence. */
    d->worker247.fence[index]=result;
    error=glGetError();d->worker247.error=error;
    worker247_trace(75,index,result,error);
    return !error && (result==GL_ALREADY_SIGNALED ||
                     result==GL_CONDITION_SATISFIED) && worker247_alive(d);
}

/* Called solely by PFIFO worker with FIFO lock, before pending/pusher/reports. */
bool pgraph_gl_worker247(NV2AState *d)
{
    if (qatomic_load_acquire(&d->worker247.state)!=1) { return false; }
    if (qatomic_cmpxchg(&d->worker247.state,1,2)!=1) { return false; }
    PGRAPHState *pg=&d->pgraph;PGRAPHGLState *r=pg->gl_renderer_state;
    unsigned reason=0;
    d->worker247.thread=qemu_get_thread_id();
    d->worker247.when=qemu_clock_get_ns(QEMU_CLOCK_REALTIME);
    worker247_trace(71,0,2,0);
    bool renderer=!qemu_mutex_trylock(&pg->renderer_lock);
    bool graph=renderer && !qemu_mutex_trylock(&pg->lock);
    if (!renderer || !graph) { reason=1; }
    else if (!worker247_alive(d) || !r || bql_locked() ||
             !d->pfifo.halt || pg->framebuffer_in_use) { reason=2; }
    else if (d->pfifo.regs[NV_PFIFO_CACHE1_DMA_GET]!=
             d->pfifo.regs[NV_PFIFO_CACHE1_DMA_PUT] ||
             (d->pfifo.regs[NV_PFIFO_CACHE1_DMA_STATE] &
              (NV_PFIFO_CACHE1_DMA_STATE_METHOD_COUNT|NV_PFIFO_CACHE1_DMA_STATE_ERROR)) ||
             pg->primitive_mode!=PRIM_TYPE_INVALID || pg->draw_arrays_length ||
             pg->inline_array_length || pg->inline_elements_length ||
             pg->inline_buffer_length || pg->waiting_for_nop ||
             pg->waiting_for_flip || pg->waiting_for_context_switch ||
             pg->renderer_switch_phase!=PGRAPH_RENDERER_SWITCH_PHASE_IDLE ||
             qatomic_read(&pg->flush_pending) || qatomic_read(&pg->sync_pending) ||
             qatomic_read(&r->downloads_pending) ||
             qatomic_read(&r->download_dirty_surfaces_pending) ||
             qatomic_read(&r->shader_cache_writeback_pending)) { reason=3; }
    if (graph && r) {
        SurfaceBinding *s;
        QTAILQ_FOREACH(s,&r->surfaces,entry) {
            if (d->worker247.count==128) { reason=4;break; }
            unsigned n=d->worker247.count++;
            uint64_t flags=(s->draw_dirty?1:0)|(s->download_pending?2:0)|
                (s->cpu_write_evict_pending?4:0)|(s->upload_pending?8:0);
            uint64_t values[6]={(uint64_t)(uintptr_t)s,s->vram_addr,s->size,
                               s->gl_buffer,flags,s->access_cb!=NULL};
            memcpy(d->worker247.surfaces[n],values,sizeof(values));
            worker247_trace(76,values[0],values[1],values[2]);
            worker247_trace(77,values[0],values[3],flags);
            if (flags) { d->worker247.dirty++;if (!reason) {reason=5;} }
        }
    }
    if (graph) {qemu_mutex_unlock(&pg->lock);}
    if (renderer) {qemu_mutex_unlock(&pg->renderer_lock);}
    qemu_mutex_unlock(&d->pfifo.lock);
    /* No renderer/PG/FIFO/BQL ownership spans either finite GL fence wait. */
    if (!reason && !worker247_context(d,0,g_nv2a_context_render)) { reason=6; }
    if (!reason && !worker247_context(d,1,g_nv2a_context_display)) { reason=7; }
    glo_set_current(g_nv2a_context_render);
    qemu_mutex_lock(&d->pfifo.lock);
    d->worker247.reason=reason;
    qatomic_store_release(&d->worker247.ready,true);
    if (!reason && worker247_alive(d)) {
        qatomic_store_release(&d->worker247.state,3);
        worker247_trace(78,0,3,0);
        while (worker247_alive(d)) {
            /* Releases FIFO throughout the bounded park; no other locks held. */
            qemu_cond_timedwait(&d->pfifo.fifo_cond,&d->pfifo.lock,20);
        }
    }
    bool explicit_release=qatomic_load_acquire(&d->worker247.release);
    qatomic_set(&d->pfifo.halt,d->worker247.old_halt);
    qatomic_store_release(&d->worker247.state,
                         !reason && explicit_release ? 5 : 6);
    worker247_trace(80,0,qatomic_read(&d->worker247.state),reason);
    return true; /* Skip pending/pusher/reports for this iteration, even refusal. */
}

static void pgraph_gl_process_pending(NV2AState *d)
{
    PGRAPHState *pg = &d->pgraph;
    PGRAPHGLState *r = pg->gl_renderer_state;

    /*238 FIFO-owned sample first. Renderer lock is TRY only, then FIFO is
     * released BEFORE PG acquisition. Never block FIFO/BQL on renderer lock.
     * This is not a producer halt, reference release, fence or readback. */
    if (nv2a_snapshot238_claim(d)) {
        nv2a_snapshot238_fifo(d);
        bool renderer_locked = !qemu_mutex_trylock(&pg->renderer_lock);
        qemu_mutex_unlock(&d->pfifo.lock);
        qemu_mutex_lock(&pg->lock);
        nv2a_snapshot238_copy(d);
        NV2AWaitSnapshot238 *v = &d->snapshot238;
        uint64_t context[20] = {
            pg->primitive_mode, pg->draw_arrays_length, pg->inline_array_length,
            pg->inline_elements_length, pg->inline_buffer_length,
            renderer_locked ? pg->framebuffer_in_use : 0,
            qatomic_read(&pg->flush_pending), qatomic_read(&pg->sync_pending),
            pgraph_reg_r(pg, NV_PGRAPH_CTX_USER), pgraph_reg_r(pg, NV_PGRAPH_SURFACE),
            pg->dma_color, pg->dma_zeta,
            pg->context_surfaces_2d.object_instance,
            pg->context_surfaces_2d.dma_image_source,
            pg->context_surfaces_2d.dma_image_dest, pg->image_blit.context_surfaces,
            r != NULL, pg->renderer->type,
            renderer_locked && r ? r->color_binding != NULL : 0,
            renderer_locked && r ? r->zeta_binding != NULL : 0,
        };
        memcpy(v->context, context, sizeof(context));
        v->renderer_valid = renderer_locked && r != NULL;
        if (v->renderer_valid) {
            SurfaceBinding *surface;
            QTAILQ_FOREACH(surface, &r->surfaces, entry) {
                if (v->surface_count == 128) {
                    v->surface_truncated = 1; break;
                }
                uint64_t fields[12] = {
                    surface->vram_addr, surface->size, surface->pitch,
                    surface->width, surface->height,
                    (surface->draw_dirty ? 1 : 0) |
                    (surface->download_pending ? 2 : 0) |
                    (surface->cpu_write_evict_pending ? 4 : 0) |
                    (surface->upload_pending ? 8 : 0) |
                    (surface->cleared ? 16 : 0) |
                    (surface->color ? 32 : 0) | (surface->swizzle ? 64 : 0),
                    surface->access_cb != NULL, surface == r->color_binding,
                    surface == r->zeta_binding, surface->gl_buffer,
                    surface->dma_addr, surface->dma_len,
                };
                memcpy(v->surfaces[v->surface_count++], fields, sizeof(fields));
            }
        }
        qemu_mutex_unlock(&pg->lock);
        if (renderer_locked) { qemu_mutex_unlock(&pg->renderer_lock); }
        nv2a_snapshot238_publish(d);
        qemu_mutex_lock(&d->pfifo.lock);
    }

    /* Request is one-shot and producer admission was halted under FIFO lock.
     * Frontend references are explicitly not retired by this diagnostic. */
    if (qatomic_load_acquire(&d->preserve227.state) == 1) {
        nv2a_preserve232_consume(d);
        nv2a_preserve231_snapshot(d, d->preserve227.gate_fifo);
        unsigned result = 4;
        bool frontend_locked = !qemu_mutex_trylock(&pg->renderer_lock);
        if (!frontend_locked) { qatomic_set(&d->preserve227.reason, 2); }
        unsigned stop = qatomic_read(&d->preserve227.consume_stop);
        if (stop == 6 || stop == 7 || stop == 8) {
            result = 6;
            qatomic_set(&d->preserve227.reason, 16 + stop);
        } else if (frontend_locked && !stop) {
            bool queue_empty =
                d->pfifo.regs[NV_PFIFO_CACHE1_DMA_GET] ==
                d->pfifo.regs[NV_PFIFO_CACHE1_DMA_PUT] &&
                !(d->pfifo.regs[NV_PFIFO_CACHE1_DMA_STATE] &
                  (NV_PFIFO_CACHE1_DMA_STATE_METHOD_COUNT |
                   NV_PFIFO_CACHE1_DMA_STATE_ERROR));
            if (!queue_empty) { qatomic_set(&d->preserve227.reason, 1); }
            if (queue_empty &&
                qatomic_cmpxchg(&d->preserve227.state, 1, 2) == 1) {
                inventory242_fifo(d, 0);
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
                inventory242_fifo(d, 1);
            }
        }
        if (frontend_locked) { qemu_mutex_unlock(&pg->renderer_lock); }
        if (stop && result == 4) { qatomic_set(&d->preserve227.reason, 16 + stop); }
        /* Timeout is terminal; a late worker result never unhalts admission. */
        nv2a_preserve227_finish(d, result);
    }

    if (qatomic_read(&r->downloads_pending) ||
        qatomic_read(&r->download_dirty_surfaces_pending) ||
        qatomic_read(&d->pgraph.sync_pending) ||
        qatomic_read(&d->pgraph.flush_pending) ||
        qatomic_read(&r->shader_cache_writeback_pending)) {
        qemu_mutex_unlock(&d->pfifo.lock);
        qemu_mutex_lock(&d->pgraph.lock);
        if (qatomic_read(&r->downloads_pending)) {
            pgraph_gl_process_pending_downloads(d);
        }
        if (qatomic_read(&r->download_dirty_surfaces_pending)) {
            pgraph_gl_download_dirty_surfaces(d);
        }
        if (qatomic_read(&d->pgraph.sync_pending)) {
            pgraph_gl_sync(d);
        }
        if (qatomic_read(&d->pgraph.flush_pending)) {
            pgraph_gl_flush(d);
        }
        if (qatomic_read(&r->shader_cache_writeback_pending)) {
            pgraph_gl_shader_write_cache_reload_list(&d->pgraph);
        }
        qemu_mutex_unlock(&d->pgraph.lock);
        qemu_mutex_lock(&d->pfifo.lock);
    }
}

static void pgraph_gl_pre_savevm_trigger(NV2AState *d)
{
    PGRAPHState *pg = &d->pgraph;
    PGRAPHGLState *r = pg->gl_renderer_state;

    qatomic_set(&r->download_dirty_surfaces_pending, true);
    qemu_event_reset(&r->dirty_surfaces_download_complete);
}

static void pgraph_gl_pre_savevm_wait(NV2AState *d)
{
    PGRAPHState *pg = &d->pgraph;
    PGRAPHGLState *r = pg->gl_renderer_state;

    qemu_event_wait(&r->dirty_surfaces_download_complete);
}

static void pgraph_gl_pre_shutdown_trigger(NV2AState *d)
{
    PGRAPHState *pg = &d->pgraph;
    PGRAPHGLState *r = pg->gl_renderer_state;

    qatomic_set(&r->shader_cache_writeback_pending, true);
    qemu_event_reset(&r->shader_cache_writeback_complete);
}

static void pgraph_gl_pre_shutdown_wait(NV2AState *d)
{
    PGRAPHState *pg = &d->pgraph;
    PGRAPHGLState *r = pg->gl_renderer_state;

    qemu_event_wait(&r->shader_cache_writeback_complete);
}

static PGRAPHRenderer pgraph_gl_renderer = {
    .type = CONFIG_DISPLAY_RENDERER_OPENGL,
    .name = "OpenGL",
    .ops = {
        .init = pgraph_gl_init,
        .early_context_init = early_context_init,
        .finalize = pgraph_gl_finalize,
        .clear_report_value = pgraph_gl_clear_report_value,
        .clear_surface = pgraph_gl_clear_surface,
        .draw_begin = pgraph_gl_draw_begin,
        .draw_end = pgraph_gl_draw_end,
        .flip_stall = pgraph_gl_flip_stall,
        .flush_draw = pgraph_gl_flush_draw,
        .get_report = pgraph_gl_get_report,
        .image_blit = pgraph_gl_image_blit,
        .pre_savevm_trigger = pgraph_gl_pre_savevm_trigger,
        .pre_savevm_wait = pgraph_gl_pre_savevm_wait,
        .pre_shutdown_trigger = pgraph_gl_pre_shutdown_trigger,
        .pre_shutdown_wait = pgraph_gl_pre_shutdown_wait,
        .process_pending = pgraph_gl_process_pending,
        .process_pending_reports = pgraph_gl_process_pending_reports,
        .surface_update = pgraph_gl_surface_update,
        .set_surface_scale_factor = pgraph_gl_set_surface_scale_factor,
        .get_surface_scale_factor = pgraph_gl_get_surface_scale_factor,
        .get_framebuffer_surface = pgraph_gl_get_framebuffer_surface,
        .get_gpu_properties = pgraph_gl_get_gpu_properties,
    }
};

static void __attribute__((constructor)) register_renderer(void)
{
    pgraph_renderer_register(&pgraph_gl_renderer);
}
