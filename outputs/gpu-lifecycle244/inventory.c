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
