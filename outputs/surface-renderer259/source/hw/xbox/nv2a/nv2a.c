/*
 * QEMU Geforce NV2A implementation
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
#include "qemu/main-loop.h"

void nv2a_update_irq(NV2AState *d)
{
    /* PFIFO */
    if (d->pfifo.pending_interrupts & d->pfifo.enabled_interrupts) {
        d->pmc.pending_interrupts |= NV_PMC_INTR_0_PFIFO;
    } else {
        d->pmc.pending_interrupts &= ~NV_PMC_INTR_0_PFIFO;
    }

    /* PCRTC */
    if (d->pcrtc.pending_interrupts & d->pcrtc.enabled_interrupts) {
        d->pmc.pending_interrupts |= NV_PMC_INTR_0_PCRTC;
    } else {
        d->pmc.pending_interrupts &= ~NV_PMC_INTR_0_PCRTC;
    }

    /* PGRAPH */
    if (d->pgraph.pending_interrupts & d->pgraph.enabled_interrupts) {
        d->pmc.pending_interrupts |= NV_PMC_INTR_0_PGRAPH;
    } else {
        d->pmc.pending_interrupts &= ~NV_PMC_INTR_0_PGRAPH;
    }

    if (d->pmc.pending_interrupts && d->pmc.enabled_interrupts) {
        trace_nv2a_irq(d->pmc.pending_interrupts);
        pci_irq_assert(PCI_DEVICE(d));
    } else {
        pci_irq_deassert(PCI_DEVICE(d));
    }
}

DMAObject nv_dma_load(NV2AState *d, hwaddr dma_obj_address)
{
    assert(dma_obj_address < memory_region_size(&d->ramin));

    uint32_t *dma_obj = (uint32_t *)(d->ramin_ptr + dma_obj_address);
    uint32_t flags = ldl_le_p(dma_obj);
    uint32_t limit = ldl_le_p(dma_obj + 1);
    uint32_t frame = ldl_le_p(dma_obj + 2);

    return (DMAObject){
        .dma_class  = GET_MASK(flags, NV_DMA_CLASS),
        .dma_target = GET_MASK(flags, NV_DMA_TARGET),
        .address    = (frame & NV_DMA_ADDRESS) | GET_MASK(flags, NV_DMA_ADJUST),
        .limit      = limit,
    };
}

void *nv_dma_map(NV2AState *d, hwaddr dma_obj_address, hwaddr *len)
{
    DMAObject dma = nv_dma_load(d, dma_obj_address);

    /* TODO: Handle targets and classes properly */
    trace_nv2a_dma_map(dma_obj_address, dma.dma_class, dma.dma_target,
                       dma.address, dma.limit);
    dma.address &= 0x07FFFFFF;

    assert(dma.address < memory_region_size(d->vram));
    // assert(dma.address + dma.limit < memory_region_size(d->vram));
    *len = dma.limit;
    return d->vram_ptr + dma.address;
}

hwaddr nv_clip_gpu_tile_blit(NV2AState *d, hwaddr blit_base_address, hwaddr len)
{
    const uint32_t *regs = d->pfb.regs;
    hwaddr blit_end = blit_base_address + len;
    for (int i = 0; i < NV_NUM_GPU_TILES; ++i) {
        uint32_t base_and_flags = regs[NV_PFB_TILE_BASE_ADDRESS_AND_FLAGS(i)];
        if (!(base_and_flags & NV_PFB_TILE_FLAGS_VALID)) {
            continue;
        }

        uint32_t limit = regs[NV_PFB_TILE_LIMIT(i)];

        if (blit_base_address < limit && blit_end > limit) {
            // TODO: Determine HW behavior if tiles are consecutive.
            return limit + 1 - blit_base_address;
        }
    }

    return len;
}

const NV2ABlockInfo blocktable[NV_NUM_BLOCKS] = {
    #define ENTRY(NAME, LNAME, OFFSET, SIZE) [NV_##NAME] = {            \
        .name   = #NAME,                                                \
        .offset = OFFSET,                                               \
        .size   = SIZE,                                                 \
        .ops    = { .read = LNAME ## _read, .write = LNAME ## _write }, \
    }
    ENTRY(PMC,      pmc,      0x000000, 0x001000),
    ENTRY(PBUS,     pbus,     0x001000, 0x001000),
    ENTRY(PFIFO,    pfifo,    0x002000, 0x002000),
    ENTRY(PRMA,     prma,     0x007000, 0x001000),
    ENTRY(PVIDEO,   pvideo,   0x008000, 0x001000),
    ENTRY(PTIMER,   ptimer,   0x009000, 0x001000),
    ENTRY(PCOUNTER, pcounter, 0x00a000, 0x001000),
    ENTRY(PVPE,     pvpe,     0x00b000, 0x001000),
    ENTRY(PTV,      ptv,      0x00d000, 0x001000),
    ENTRY(PRMFB,    prmfb,    0x0a0000, 0x020000),
    ENTRY(PRMVIO,   prmvio,   0x0c0000, 0x001000),
    ENTRY(PFB,      pfb,      0x100000, 0x001000),
    ENTRY(PSTRAPS,  pstraps,  0x101000, 0x001000),
    ENTRY(PGRAPH,   pgraph,   0x400000, 0x002000),
    ENTRY(PCRTC,    pcrtc,    0x600000, 0x001000),
    ENTRY(PRMCIO,   prmcio,   0x601000, 0x001000),
    ENTRY(PRAMDAC,  pramdac,  0x680000, 0x001000),
    ENTRY(PRMDIO,   prmdio,   0x681000, 0x001000),
    // ENTRY(PRAMIN,   pramin,   0x700000, 0x100000),
    ENTRY(USER,     user,     0x800000, 0x800000),
};
#undef ENTRY

static int nv2a_get_bpp(VGACommonState *s)
{
    NV2AState *d = container_of(s, NV2AState, vga);

    int depth = s->cr[0x28] & 3;

    int bpp;
    switch (depth) {
    case 0:
        /* FIXME: This case is sometimes hit during early Xbox startup.
         *        Presumably a race-condition where VGA isn't initialized, yet.
         *        `bpp = 0` mimics old code that did `bpp = depth * 8;`.
         *        This works around the issue of this mode being unhandled.
         *        However, QEMU VGA uses a 4bpp mode if `bpp = 0`.
         *        We don't know if Xbox hardware would do the same. */
        bpp = 0;
        break;
    case 2:
        bpp = d->pramdac.general_control &
              NV_PRAMDAC_GENERAL_CONTROL_ALT_MODE_SEL ? 16 : 15;
        break;
    case 3:
        bpp = 32;
        break;
    default:
        /* This is only a fallback path */
        bpp = depth * 8;
        fprintf(stderr, "Unknown VGA depth: %d\n", depth);
        assert(!"Unknown VGA depth - check logs for depth value");
        break;
    }

    return bpp;
}

static void nv2a_get_params(VGACommonState *s, VGADisplayParams *params)
{
    NV2AState *d = container_of(s, NV2AState, vga);
    params->line_offset = (s->cr[0x13] | ((s->cr[0x19] & 0xe0) << 3) |
                           ((s->cr[0x25] & 0x20) << 6))
                          << 3;
    params->start_addr = d->pcrtc.start / 4;
    params->line_compare = s->cr[VGA_CRTC_LINE_COMPARE] |
                           ((s->cr[VGA_CRTC_OVERFLOW] & 0x10) << 4) |
                           ((s->cr[VGA_CRTC_MAX_SCAN] & 0x40) << 3);
}

const uint8_t *nv2a_get_dac_palette(void)
{
    return g_nv2a->puserdac.palette;
}

int nv2a_get_screen_off(void)
{
    return g_nv2a->vga.sr[VGA_SEQ_CLOCK_MODE] & VGA_SR01_SCREEN_OFF;
}

static void nv2a_vga_gfx_update(void *opaque)
{
    VGACommonState *vga = opaque;
    vga->hw_ops->gfx_update(vga);

    NV2AState *d = container_of(vga, NV2AState, vga);
    d->pcrtc.pending_interrupts |= NV_PCRTC_INTR_0_VBLANK;
    d->pcrtc.raster = 0;

    nv2a_update_irq(d);
}

static void nv2a_init_memory(NV2AState *d, MemoryRegion *ram)
{
    /* xbox is UMA - vram *is* ram */
    d->vram = ram;

     /* PCI exposed vram */
    memory_region_init_alias(&d->vram_pci, OBJECT(d), "nv2a-vram-pci", d->vram,
                             0, getenv("XWN_NV2A_RESOURCE_MODEL") ? 0x08000000 : memory_region_size(d->vram));
    pci_register_bar(PCI_DEVICE(d), 1, PCI_BASE_ADDRESS_MEM_PREFETCH, &d->vram_pci);


    /* RAMIN - should be in vram somewhere, but not quite sure where atm */
    memory_region_init_ram(&d->ramin, OBJECT(d), "nv2a-ramin", 0x100000, &error_fatal);
    /* memory_region_init_alias(&d->ramin, "nv2a-ramin", &d->vram,
                         memory_region_size(d->vram) - 0x100000,
                         0x100000); */

    memory_region_add_subregion(&d->mmio, 0x700000, &d->ramin);
    /* Resource-allocation experiment only, not a complete hardware model.
     * "128-only" isolates BAR1 size; "128-plus-extra" also exposes the
     * physical registry's 512 KiB prefetchable BAR2 requirement. */
    if (getenv("XWN_NV2A_RESOURCE_MODEL") &&
        !strcmp(getenv("XWN_NV2A_RESOURCE_MODEL"), "128-plus-extra")) {
        memory_region_init_alias(&d->resource_test_bar2, OBJECT(d),
                                 "nv2a-resource-test-bar2", &d->ramin, 0, 0x80000);
        pci_register_bar(PCI_DEVICE(d), 2, PCI_BASE_ADDRESS_MEM_PREFETCH,
                         &d->resource_test_bar2);
    }



    d->vram_ptr = memory_region_get_ram_ptr(d->vram);
    d->ramin_ptr = memory_region_get_ram_ptr(&d->ramin);

    memory_region_set_log(d->vram, true, DIRTY_MEMORY_NV2A);
    memory_region_set_log(d->vram, true, DIRTY_MEMORY_NV2A_TEX);
    memory_region_set_dirty(d->vram, 0, memory_region_size(d->vram));

    pgraph_init(d);

    /* fire up pfifo */
    qemu_thread_create(&d->pfifo.thread, "nv2a.pfifo_thread",
                       pfifo_thread, d, QEMU_THREAD_JOINABLE);
}

static void nv2a_init_vga(NV2AState *d)
{
    VGACommonState *vga = &d->vga;
    vga->vram_size_mb = memory_region_size(d->vram) / MiB;

    vga_common_init(vga, OBJECT(d), &error_fatal);
    vga->get_bpp = nv2a_get_bpp;
    vga->get_params = nv2a_get_params;
    // vga->overlay_draw_line = nv2a_overlay_draw_line;

    d->hw_ops = *vga->hw_ops;
    d->hw_ops.gfx_update = nv2a_vga_gfx_update;
    vga->con = graphic_console_init(DEVICE(d), 0, &d->hw_ops, vga);

    /* hacky. swap out vga's vram */
    memory_region_destroy(&vga->vram);
    // memory_region_unref(&vga->vram); // FIXME: Is ths right?
    memory_region_init_alias(&vga->vram, OBJECT(d), "vga.vram",
                             d->vram, 0, memory_region_size(d->vram));
    vga->vram_ptr = memory_region_get_ram_ptr(&vga->vram);
    vga_dirty_log_start(vga);
}

static void nv2a_lock_fifo(NV2AState *d)
{
    qemu_mutex_lock(&d->pfifo.lock);
    qemu_cond_broadcast(&d->pfifo.fifo_cond);
    bql_unlock();
    qemu_cond_wait(&d->pfifo.fifo_idle_cond, &d->pfifo.lock);
    bql_lock();
    qemu_mutex_lock(&d->pgraph.lock);
}

static void nv2a_unlock_fifo(NV2AState *d)
{
    pfifo_kick(d);
    qemu_mutex_unlock(&d->pgraph.lock);
    qemu_mutex_unlock(&d->pfifo.lock);
}

static void nv2a_reset(NV2AState *d)
{
    nv2a_lock_fifo(d);
    bool halted = qatomic_read(&d->pfifo.halt);
    if (!halted) {
        qatomic_set(&d->pfifo.halt, true);
    }
    qemu_event_reset(&d->pgraph.flush_complete);
    qatomic_set(&d->pgraph.flush_pending, true);
    nv2a_unlock_fifo(d);
    bql_unlock();
    qemu_event_wait(&d->pgraph.flush_complete);
    bql_lock();
    nv2a_lock_fifo(d);
    if (!halted) {
        qatomic_set(&d->pfifo.halt, false);
    }

    nv2a_wait233_record(d, 7, 0, true);
    memset(d->pfifo.regs, 0, sizeof(d->pfifo.regs));
    memset(d->pgraph.regs_, 0, sizeof(d->pgraph.regs_));
    memset(d->pvideo.regs, 0, sizeof(d->pvideo.regs));

    d->pcrtc.start = 0;
    d->pramdac.core_clock_coeff = 0x00011C01; /* 189MHz...? */
    d->pramdac.core_clock_freq = 233333324;
    d->pramdac.memory_clock_coeff = 0;
    d->pramdac.video_clock_coeff = 0x0003C20D; /* 25182Khz...? */

    d->pfifo.regs[NV_PFIFO_CACHE1_STATUS] |= NV_PFIFO_CACHE1_STATUS_LOW_MARK;

    vga_common_reset(&d->vga);
    /* seems to start in color mode */
    d->vga.msr = VGA_MIS_COLOR;

    d->pgraph.waiting_for_nop = false;
    d->pgraph.waiting_for_flip = false;
    d->pgraph.waiting_for_context_switch = false;

    d->pmc.pending_interrupts = 0;
    d->pfifo.pending_interrupts = 0;
    d->ptimer.pending_interrupts = 0;
    d->pcrtc.pending_interrupts = 0;

    for (int i = 0; i < 256; i++) {
        d->puserdac.palette[i*3]   = i;
        d->puserdac.palette[i*3+1] = i;
        d->puserdac.palette[i*3+2] = i;
    }

    nv2a_wait233_record(d, 8, 0, true);
    nv2a_unlock_fifo(d);
}

/*227 stopped-VM diagnostic. No driver/guest ownership grant. */
static bool preserve227_get(Object *obj, Error **errp)
{
    NV2AState *d = NV2A_DEVICE(obj);
    return qatomic_load_acquire(&d->preserve227.state) == 3;
}

static void worker247_set(Object *obj, bool value, Error **errp)
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

static void frontend246_set(Object *obj, bool value, Error **errp)
{
    if (!xwn_frontend246_request(value)) {
        error_setg(errp, "246 one close and one reopen, never retry/reset");
    }
}

static char *frontend246_report_get(Object *obj, Error **errp)
{
    return xwn_frontend246_report();
}

static void lifecycle244_mark_set(Object *obj, bool value, Error **errp)
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

static void preserve227_set(Object *obj, bool value, Error **errp)
{
    NV2AState *d = NV2A_DEVICE(obj);
    if (!value || qatomic_load_acquire(&d->preserve227.state) != 0 ||
        !(runstate_check(RUN_STATE_PAUSED) || runstate_check(RUN_STATE_DEBUG))) {
        error_setg(errp, "preserve227 needs unused stopped-VM request");
        return;
    }
    if (d->pgraph.renderer->type != CONFIG_DISPLAY_RENDERER_OPENGL) {
        error_setg(errp, "preserve227 supports OpenGL only");
        return;
    }
    /* Never block the monitor on a worker that might need the BQL. */
    if (qemu_mutex_trylock(&d->pfifo.lock)) {
        error_setg(errp, "preserve227 FIFO lock busy; request not accepted");
        return;
    }
    int64_t now = qemu_clock_get_ns(QEMU_CLOCK_REALTIME);
    if (now > INT64_MAX - 5000000000LL) {
        qemu_mutex_unlock(&d->pfifo.lock);
        error_setg(errp, "preserve227 deadline overflow; request not accepted");
        return;
    }
    d->preserve227.old_halt = qatomic_read(&d->pfifo.halt);
    d->preserve227.deadline = now + 5000000000LL;
    qatomic_set(&d->pfifo.halt, true);
    nv2a_preserve231_snapshot(d, d->preserve227.request_fifo);
    qatomic_store_release(&d->preserve227.state, 1);
    pfifo_kick(d);
    qemu_mutex_unlock(&d->pfifo.lock);
}

/*242 No monitor dereference of live renderer objects. Only worker-published
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

static char *preserve227_report(Object *obj, Error **errp)
{
    NV2AState *d = NV2A_DEVICE(obj);
    unsigned state = qatomic_load_acquire(&d->preserve227.state);
    if ((state == 1 || state == 2) &&
        qemu_clock_get_ns(QEMU_CLOCK_REALTIME) >= d->preserve227.deadline) {
        qatomic_cmpxchg(&d->preserve227.state, state, 5);
        state = qatomic_load_acquire(&d->preserve227.state);
    }
    /* Only a worker-published terminal state orders its mutable tuple.
     * Timeout5 can precede late worker stores; never expose that tuple. Request
     * words are immutable before release1. There is no reuse/reset operation. */
    bool published = state == 3 || state == 4 || state == 6;
    GString *report = g_string_new(NULL);
    g_string_append_printf(report,
        "state=%u tuple_published=%u publication_version=232"
        " surfaces=%u dirty=%u downloaded=%u bytes=%" PRIu64
        " error=%u reason=%u references_retired=0 native_grant=0 old_halt=%u",
        state, published,
        published ? qatomic_read(&d->preserve227.surfaces) : 0,
        published ? qatomic_read(&d->preserve227.dirty) : 0,
        published ? qatomic_read(&d->preserve227.downloaded) : 0,
        published ? qatomic_read(&d->preserve227.bytes) : 0,
        published ? qatomic_read(&d->preserve227.error) : 0,
        published ? qatomic_read(&d->preserve227.reason) : 0,
        state ? d->preserve227.old_halt : 0);
    for (unsigned i = 0; i < 10; i++) {
        g_string_append_printf(report, " request%u=%u gate%u=%u", i,
            state ? qatomic_read(&d->preserve227.request_fifo[i]) : 0, i,
            published ? qatomic_read(&d->preserve227.gate_fifo[i]) : 0);
    }
    g_string_append_printf(report,
        " consume_stop=%u consume_steps=%u consume_words=%u wait_before=%u wait_after=%u",
        published ? qatomic_read(&d->preserve227.consume_stop) : 0,
        published ? qatomic_read(&d->preserve227.consume_steps) : 0,
        published ? qatomic_read(&d->preserve227.consume_words) : 0,
        published ? qatomic_read(&d->preserve227.wait_before) : 0,
        published ? qatomic_read(&d->preserve227.wait_after) : 0);
    return g_string_free(report, false);
}

/*231 caller holds FIFO lock. Raw words, not a synthetic idle predicate.
 * PGRAPH FIFO has its existing atomic-access contract. Snapshots do not retire
 * references or write emulated registers. */
void nv2a_preserve231_snapshot(NV2AState *d, uint32_t words[10])
{
    const hwaddr offsets[9] = {
        NV_PFIFO_CACHE1_DMA_GET, NV_PFIFO_CACHE1_DMA_PUT,
        NV_PFIFO_CACHE1_DMA_STATE, NV_PFIFO_CACHE1_PUSH0,
        NV_PFIFO_CACHE1_PUSH1, NV_PFIFO_CACHE1_DMA_PUSH,
        NV_PFIFO_CACHE1_PULL0, NV_PFIFO_CACHE1_STATUS,
        NV_PFIFO_CACHE1_DMA_SUBROUTINE,
    };
    for (unsigned i = 0; i < 9; i++) {
        qatomic_set(&words[i], d->pfifo.regs[offsets[i]]);
    }
    qatomic_set(&words[9], qatomic_read(&d->pgraph.regs_[NV_PGRAPH_FIFO]));
}

/*228 claim terminal publication before restoring admission. State7 is a
 * nonblocking publication phase, never a new request or ownership permit. */
void nv2a_preserve227_finish(NV2AState *d, unsigned result)
{
    unsigned expected = qatomic_load_acquire(&d->preserve227.state);
    if (expected != 1 && expected != 2) { return; }
    if (qemu_clock_get_ns(QEMU_CLOCK_REALTIME) >= d->preserve227.deadline) {
        result = 5;
    }
    if (qatomic_cmpxchg(&d->preserve227.state, expected, 7) != expected) {
        return;
    }
    if (result == 3 || result == 4) {
        qatomic_set(&d->pfifo.halt, d->preserve227.old_halt);
    }
    qatomic_store_release(&d->preserve227.state, result);
}

/*238 ONE request: 0 unused,1 requested,2 worker copying,7 publication
 * claimed,3 immutable terminal,5 timeout. No reset/reuse or guest-state write.
 * Deadline initialized before request release; reader only expires 1/2. */
static unsigned snapshot238_expire(NV2AState *d)
{
    unsigned state = qatomic_load_acquire(&d->snapshot238.state);
    if ((state == 1 || state == 2) &&
        qemu_clock_get_ns(QEMU_CLOCK_REALTIME) >= d->snapshot238.deadline) {
        qatomic_cmpxchg(&d->snapshot238.state, state, 5);
        state = qatomic_load_acquire(&d->snapshot238.state);
    }
    return state;
}

bool nv2a_snapshot238_claim(NV2AState *d)
{
    return snapshot238_expire(d) == 1 &&
        qatomic_cmpxchg(&d->snapshot238.state, 1, 2) == 1;
}

/* Actual FIFO lock is already owned; PG is NOT acquired here. */
void nv2a_snapshot238_fifo(NV2AState *d)
{
    uint32_t words[10];
    nv2a_preserve231_snapshot(d, words);
    d->snapshot238.fifo_when = qemu_clock_get_ns(QEMU_CLOCK_REALTIME);
    d->snapshot238.fifo[0] = d->pfifo.halt;
    d->snapshot238.fifo[1] = d->pfifo.fifo_kick;
    d->snapshot238.fifo[2] = d->pfifo.pending_interrupts;
    d->snapshot238.fifo[3] = d->pfifo.enabled_interrupts;
    for (unsigned i = 0; i < 10; i++) {
        d->snapshot238.fifo[4+i] = words[i];
    }
}

/* Caller holds actual PG lock, FIFO has been released. No FIFO reads. */
void nv2a_snapshot238_copy(NV2AState *d)
{
    d->snapshot238.total = d->wait233.total;
    d->snapshot238.count = d->wait233.count;
    nv2a_wait233_fill(d, &d->snapshot238.current, 9, 0, false);
    unsigned start = (d->wait233.next + NV2A_WAIT233_CAPACITY -
                      d->wait233.count) % NV2A_WAIT233_CAPACITY;
    for (unsigned i = 0; i < d->wait233.count; i++) {
        d->snapshot238.rows[i] =
            d->wait233.rows[(start + i) % NV2A_WAIT233_CAPACITY];
    }
}

/* All copied bytes precede release3. Timeout's CAS wins over late completion;
 * unpublished late storage stays invisible and can never be requested again. */
void nv2a_snapshot238_publish(NV2AState *d)
{
    if (snapshot238_expire(d) != 2) { return; }
    if (qatomic_cmpxchg(&d->snapshot238.state, 2, 7) != 2) { return; }
    qatomic_store_release(&d->snapshot238.state, 3);
}

static void wait233_format(GString *s, const NV2AWaitRow233 *row)
{
    g_string_append_printf(s, " row=%" PRIu64 ",%" PRIu64 ",%u,%u,%u,%u,%u,%u,%u,%u,%u",
        row->seq, row->when, row->kind, row->value, row->pending,
        row->enabled, row->nsource, row->trapped, row->data, row->waits,
        row->fifo_valid);
    for (unsigned i = 0; i < 10; i++) { g_string_append_printf(s, ",%u", row->fifo[i]); }
}

static void snapshot238_request(Object *obj, bool value, Error **errp)
{
    NV2AState *d = NV2A_DEVICE(obj);
    if (!value || qatomic_load_acquire(&d->snapshot238.state) != 0) {
        error_setg(errp, "snapshot238 requires ONE true request"); return;
    }
    /* Monitor owns BQL. Never block it waiting for FIFO or PG. */
    if (qemu_mutex_trylock(&d->pfifo.lock)) {
        error_setg(errp, "snapshot238 FIFO busy; request NOT accepted"); return;
    }
    d->snapshot238.deadline = qemu_clock_get_ns(QEMU_CLOCK_REALTIME) +
                              INT64_C(5000000000);
    qatomic_store_release(&d->snapshot238.state, 1);
    pfifo_kick(d);
    qemu_mutex_unlock(&d->pfifo.lock);
}

static bool snapshot238_requested(Object *obj, Error **errp)
{
    NV2AState *d = NV2A_DEVICE(obj);
    return qatomic_load_acquire(&d->snapshot238.state) != 0;
}

static char *snapshot238_report(Object *obj, Error **errp)
{
    NV2AState *d = NV2A_DEVICE(obj);
    unsigned state = snapshot238_expire(d);
    bool published = state == 3;
    GString *report = g_string_new(NULL);
    g_string_append_printf(report, "version=238 state=%u tuple_published=%u total=%" PRIu64 " count=%u capacity=256 overwritten=%" PRIu64,
        state, published, published ? d->snapshot238.total : 0,
        published ? d->snapshot238.count : 0,
        published ? d->snapshot238.total - d->snapshot238.count : 0);
    if (published) {
        NV2AWaitSnapshot238 *v = &d->snapshot238;
        g_string_append_printf(report, " fifo_when=%" PRIu64
            " renderer_valid=%u surface_count=%u surface_truncated=%u fifo=",
            v->fifo_when, v->renderer_valid, v->surface_count, v->surface_truncated);
        for (unsigned i = 0; i < 14; i++) {
            g_string_append_printf(report, "%s%" PRIu64, i ? "," : "", v->fifo[i]);
        }
        g_string_append_printf(report, " context=");
        for (unsigned i = 0; i < 20; i++) {
            g_string_append_printf(report, "%s%" PRIu64, i ? "," : "", v->context[i]);
        }
        for (unsigned n = 0; n < v->surface_count; n++) {
            g_string_append_printf(report, " surface=");
            for (unsigned i = 0; i < 12; i++) {
                g_string_append_printf(report, "%s%" PRIu64, i ? "," : "", v->surfaces[n][i]);
            }
        }
        wait233_format(report, &d->snapshot238.current);
        for (unsigned i = 0; i < d->snapshot238.count; i++) {
            wait233_format(report, &d->snapshot238.rows[i]);
        }
    }
    return g_string_free(report, false);
}

static void nv2a_realize(PCIDevice *dev, Error **errp)
{
    NV2AState *d = NV2A_DEVICE(dev);

    /* setting subsystem ids again, see comment in nv2a_class_init() */
    pci_set_word(dev->config + PCI_SUBSYSTEM_VENDOR_ID, 0);
    pci_set_word(dev->config + PCI_SUBSYSTEM_ID, 0);
    dev->config[PCI_INTERRUPT_PIN] = 0x01;

    /* mmio */
    memory_region_init(&d->mmio, OBJECT(dev), "nv2a-mmio", 0x1000000);
    pci_register_bar(PCI_DEVICE(d), 0, PCI_BASE_ADDRESS_SPACE_MEMORY, &d->mmio);

    for (int i=0; i < ARRAY_SIZE(blocktable); i++) {
        if (!blocktable[i].name) continue;
        memory_region_init_io(&d->block_mmio[i], OBJECT(dev),
                              &blocktable[i].ops, d,
                              blocktable[i].name, blocktable[i].size);
        memory_region_add_subregion(&d->mmio, blocktable[i].offset,
                                    &d->block_mmio[i]);
    }

    qemu_mutex_init(&d->pfifo.lock);
    qemu_cond_init(&d->pfifo.fifo_cond);
    qemu_cond_init(&d->pfifo.fifo_idle_cond);
    object_property_add_str(OBJECT(d), "xwn-inventory242-report", inventory242_report, NULL);
    object_property_add_bool(OBJECT(d), "xwn-preserve227", preserve227_get,
                             preserve227_set);
    object_property_add_bool(OBJECT(d),"xwn-worker247-close",NULL,worker247_set);
    object_property_add_str(OBJECT(d),"xwn-worker247-report",worker247_report,NULL);
    object_property_add_bool(OBJECT(d), "xwn-frontend246-close", NULL, frontend246_set);
    object_property_add_str(OBJECT(d), "xwn-frontend246-report", frontend246_report_get, NULL);
    object_property_add_bool(OBJECT(d), "xwn-lifecycle244-mark", NULL, lifecycle244_mark_set);
    object_property_add_bool(OBJECT(d), "xwn-snapshot238",
                             snapshot238_requested, snapshot238_request);
    object_property_add_str(OBJECT(d), "xwn-snapshot238-report", snapshot238_report, NULL);
    object_property_add_str(OBJECT(d), "xwn-preserve227-report",
                            preserve227_report, NULL);
}

static void nv2a_exitfn(PCIDevice *dev)
{
    NV2AState *d;
    d = NV2A_DEVICE(dev);

    d->exiting = true;

    qemu_cond_broadcast(&d->pfifo.fifo_cond);
    qemu_thread_join(&d->pfifo.thread);

    pgraph_destroy(&d->pgraph);
}

static void nv2a_reset_hold(Object *obj, ResetType type)
{
    NV2AState *s = NV2A_DEVICE(obj);
    nv2a_reset(s);
}

// Note: This is handled as a VM state change and not as a `pre_save` callback
// because we want to halt the FIFO before any VM state is saved/restored to
// avoid corruption.
static void nv2a_vm_state_change(void *opaque, bool running, RunState state)
{
    NV2AState *d = opaque;
    if (state == RUN_STATE_SAVE_VM) {
        nv2a_lock_fifo(d);
        qatomic_set(&d->pfifo.halt, true);
        pgraph_pre_savevm_trigger(d);
        nv2a_unlock_fifo(d);
        bql_unlock();
        pgraph_pre_savevm_wait(d);
        bql_lock();
        nv2a_lock_fifo(d);
    } else if (state == RUN_STATE_RESTORE_VM) {
        nv2a_lock_fifo(d);
        qatomic_set(&d->pfifo.halt, true);
        nv2a_unlock_fifo(d);
    } else if (state == RUN_STATE_RUNNING) {
        nv2a_lock_fifo(d);
        qatomic_set(&d->pfifo.halt, false);
        nv2a_unlock_fifo(d);
    } else if (state == RUN_STATE_SHUTDOWN) {
        nv2a_lock_fifo(d);
        pgraph_pre_shutdown_trigger(d);
        nv2a_unlock_fifo(d);
        bql_unlock();
        pgraph_pre_shutdown_wait(d);
        bql_lock();
    }
}

static int nv2a_post_save(void *opaque)
{
    NV2AState *d = opaque;
    nv2a_unlock_fifo(d);
    return 0;
}

static int nv2a_pre_load(void *opaque)
{
    NV2AState *d = opaque;
    nv2a_lock_fifo(d);
    return 0;
}

static int nv2a_post_load(void *opaque, int version_id)
{
    NV2AState *d = opaque;
    qatomic_set(&d->pgraph.flush_pending, true);
    nv2a_unlock_fifo(d);
    return 0;
}

const VMStateDescription vmstate_nv2a_pgraph_vertex_attributes = {
    .name = "nv2a/pgraph/vertex-attr",
    .version_id = 1,
    .minimum_version_id = 1,
    .fields = (VMStateField[]) {
        // FIXME
        VMSTATE_END_OF_LIST()
    }
};

static const VMStateDescription vmstate_nv2a = {
    .name = "nv2a",
    .version_id = 3,
    .minimum_version_id = 1,
    .post_save = nv2a_post_save,
    .post_load = nv2a_post_load,
    .pre_load = nv2a_pre_load,
    .fields = (VMStateField[]) {
        // FIXME: Split this up into subsections
        VMSTATE_PCI_DEVICE(parent_obj, NV2AState),
        VMSTATE_STRUCT(vga, NV2AState, 0, vmstate_vga_common, VGACommonState),
        VMSTATE_UINT32(pgraph.pending_interrupts, NV2AState),
        VMSTATE_UINT32(pgraph.enabled_interrupts, NV2AState),
        VMSTATE_UINT64(pgraph.context_surfaces_2d.object_instance, NV2AState),
        VMSTATE_UINT64(pgraph.context_surfaces_2d.dma_image_source, NV2AState),
        VMSTATE_UINT64(pgraph.context_surfaces_2d.dma_image_dest, NV2AState),
        VMSTATE_UINT32(pgraph.context_surfaces_2d.color_format, NV2AState),
        VMSTATE_UINT32(pgraph.context_surfaces_2d.source_pitch, NV2AState),
        VMSTATE_UINT32(pgraph.context_surfaces_2d.dest_pitch, NV2AState),
        VMSTATE_UINT64(pgraph.context_surfaces_2d.source_offset, NV2AState),
        VMSTATE_UINT64(pgraph.context_surfaces_2d.dest_offset, NV2AState),
        VMSTATE_UINT64(pgraph.image_blit.object_instance, NV2AState),
        VMSTATE_UINT64(pgraph.image_blit.context_surfaces, NV2AState),
        VMSTATE_UINT32(pgraph.image_blit.operation, NV2AState),
        VMSTATE_UINT32(pgraph.image_blit.in_x, NV2AState),
        VMSTATE_UINT32(pgraph.image_blit.in_y, NV2AState),
        VMSTATE_UINT32(pgraph.image_blit.out_x, NV2AState),
        VMSTATE_UINT32(pgraph.image_blit.out_y, NV2AState),
        VMSTATE_UINT32(pgraph.image_blit.width, NV2AState),
        VMSTATE_UINT32(pgraph.image_blit.height, NV2AState),
        VMSTATE_UINT64(pgraph.kelvin.object_instance, NV2AState),
        VMSTATE_UINT64(pgraph.dma_color, NV2AState),
        VMSTATE_UINT64(pgraph.dma_zeta, NV2AState),
        VMSTATE_BOOL(pgraph.surface_color.draw_dirty, NV2AState),
        VMSTATE_BOOL(pgraph.surface_zeta.draw_dirty, NV2AState),
        VMSTATE_BOOL(pgraph.surface_color.buffer_dirty, NV2AState),
        VMSTATE_BOOL(pgraph.surface_zeta.buffer_dirty, NV2AState),
        VMSTATE_BOOL(pgraph.surface_color.write_enabled_cache, NV2AState),
        VMSTATE_BOOL(pgraph.surface_zeta.write_enabled_cache, NV2AState),
        VMSTATE_UINT32(pgraph.surface_color.pitch, NV2AState),
        VMSTATE_UINT32(pgraph.surface_zeta.pitch, NV2AState),
        VMSTATE_UINT64(pgraph.surface_color.offset, NV2AState),
        VMSTATE_UINT64(pgraph.surface_zeta.offset, NV2AState),
        VMSTATE_UINT32(pgraph.surface_type, NV2AState),
        VMSTATE_UINT32(pgraph.surface_shape.z_format, NV2AState),
        VMSTATE_UINT32(pgraph.surface_shape.color_format, NV2AState),
        VMSTATE_UINT32(pgraph.surface_shape.zeta_format, NV2AState),
        VMSTATE_UINT32(pgraph.surface_shape.log_width, NV2AState),
        VMSTATE_UINT32(pgraph.surface_shape.log_height, NV2AState),
        VMSTATE_UINT32(pgraph.surface_shape.clip_x, NV2AState),
        VMSTATE_UINT32_V(pgraph.surface_shape.clip_y, NV2AState, 2),
        VMSTATE_UINT32(pgraph.surface_shape.clip_width, NV2AState),
        VMSTATE_UINT32(pgraph.surface_shape.clip_height, NV2AState),
        VMSTATE_UINT32(pgraph.surface_shape.anti_aliasing, NV2AState),
        VMSTATE_UINT32(pgraph.last_surface_shape.z_format, NV2AState),
        VMSTATE_UINT32(pgraph.last_surface_shape.color_format, NV2AState),
        VMSTATE_UINT32(pgraph.last_surface_shape.zeta_format, NV2AState),
        VMSTATE_UINT32(pgraph.last_surface_shape.log_width, NV2AState),
        VMSTATE_UINT32(pgraph.last_surface_shape.log_height, NV2AState),
        VMSTATE_UINT32(pgraph.last_surface_shape.clip_x, NV2AState),
        VMSTATE_UINT32_V(pgraph.last_surface_shape.clip_y, NV2AState, 2),
        VMSTATE_UINT32(pgraph.last_surface_shape.clip_width, NV2AState),
        VMSTATE_UINT32(pgraph.last_surface_shape.clip_height, NV2AState),
        VMSTATE_UINT32(pgraph.last_surface_shape.anti_aliasing, NV2AState),
        VMSTATE_UINT64(pgraph.dma_a, NV2AState),
        VMSTATE_UINT64(pgraph.dma_b, NV2AState),
        VMSTATE_UINT64(pgraph.dma_state, NV2AState),
        VMSTATE_UINT64(pgraph.dma_notifies, NV2AState),
        VMSTATE_UINT64(pgraph.dma_semaphore, NV2AState),
        VMSTATE_UINT64(pgraph.dma_report, NV2AState),
        VMSTATE_UINT64(pgraph.report_offset, NV2AState),
        VMSTATE_UINT64(pgraph.dma_vertex_a, NV2AState),
        VMSTATE_UINT64(pgraph.dma_vertex_b, NV2AState),
        VMSTATE_UINT32(pgraph.primitive_mode, NV2AState),
        VMSTATE_UINT32_ARRAY(pgraph.vertex_state_shader_v0, NV2AState, 4),
        VMSTATE_UINT32_2DARRAY(pgraph.program_data, NV2AState, NV2A_MAX_TRANSFORM_PROGRAM_LENGTH, VSH_TOKEN_SIZE),
        VMSTATE_UINT32_2DARRAY(pgraph.vsh_constants, NV2AState, NV2A_VERTEXSHADER_CONSTANTS, 4),
        VMSTATE_BOOL_ARRAY(pgraph.vsh_constants_dirty, NV2AState, NV2A_VERTEXSHADER_CONSTANTS),
        VMSTATE_UINT32_2DARRAY(pgraph.ltctxa, NV2AState, NV2A_LTCTXA_COUNT, 4),
        VMSTATE_BOOL_ARRAY(pgraph.ltctxa_dirty, NV2AState, NV2A_LTCTXA_COUNT),
        VMSTATE_UINT32_2DARRAY(pgraph.ltctxb, NV2AState, NV2A_LTCTXB_COUNT, 4),
        VMSTATE_BOOL_ARRAY(pgraph.ltctxb_dirty, NV2AState, NV2A_LTCTXB_COUNT),
        VMSTATE_UINT32_2DARRAY(pgraph.ltc1, NV2AState, NV2A_LTC1_COUNT, 4),
        VMSTATE_BOOL_ARRAY(pgraph.ltc1_dirty, NV2AState, NV2A_LTC1_COUNT),
        VMSTATE_STRUCT_ARRAY(pgraph.vertex_attributes, NV2AState, NV2A_VERTEXSHADER_ATTRIBUTES, 1, vmstate_nv2a_pgraph_vertex_attributes, VertexAttribute),
        VMSTATE_UINT32(pgraph.inline_array_length, NV2AState),
        VMSTATE_UINT32_SUB_ARRAY(pgraph.inline_array, NV2AState, 0, NV2A_MAX_BATCH_LENGTH_V2),
        VMSTATE_UINT32_SUB_ARRAY_V(pgraph.inline_array, NV2AState, NV2A_MAX_BATCH_LENGTH_V2, NV2A_MAX_BATCH_LENGTH - NV2A_MAX_BATCH_LENGTH_V2, 3),
        VMSTATE_UINT32(pgraph.inline_elements_length, NV2AState), // fixme
        VMSTATE_UINT32_SUB_ARRAY(pgraph.inline_elements, NV2AState, 0, NV2A_MAX_BATCH_LENGTH_V2),
        VMSTATE_UINT32_SUB_ARRAY_V(pgraph.inline_elements, NV2AState, NV2A_MAX_BATCH_LENGTH_V2, NV2A_MAX_BATCH_LENGTH - NV2A_MAX_BATCH_LENGTH_V2, 3),
        VMSTATE_UINT32(pgraph.inline_buffer_length, NV2AState), // fixme
        VMSTATE_UINT32(pgraph.draw_arrays_length, NV2AState),
        VMSTATE_UINT32(pgraph.draw_arrays_max_count, NV2AState),
        VMSTATE_INT32_ARRAY(pgraph.draw_arrays_start, NV2AState, 1250),
        VMSTATE_INT32_ARRAY(pgraph.draw_arrays_count, NV2AState, 1250),
        VMSTATE_UINT32_ARRAY(pgraph.regs_, NV2AState, 0x2000),
        VMSTATE_UINT32(pmc.pending_interrupts, NV2AState),
        VMSTATE_UINT32(pmc.enabled_interrupts, NV2AState),
        VMSTATE_UINT32(pfifo.pending_interrupts, NV2AState),
        VMSTATE_UINT32(pfifo.enabled_interrupts, NV2AState),
        VMSTATE_UINT32_ARRAY(pfifo.regs, NV2AState, 0x2000),
        VMSTATE_UINT32_ARRAY(pvideo.regs, NV2AState, 0x1000),
        VMSTATE_UINT32(ptimer.pending_interrupts, NV2AState),
        VMSTATE_UINT32(ptimer.enabled_interrupts, NV2AState),
        VMSTATE_UINT32(ptimer.numerator, NV2AState),
        VMSTATE_UINT32(ptimer.denominator, NV2AState),
        VMSTATE_UINT32(ptimer.alarm_time, NV2AState),
        VMSTATE_UINT32_ARRAY(pfb.regs, NV2AState, 0x1000),
        VMSTATE_UINT32(pcrtc.pending_interrupts, NV2AState),
        VMSTATE_UINT32(pcrtc.enabled_interrupts, NV2AState),
        VMSTATE_UINT64(pcrtc.start, NV2AState),
        VMSTATE_UINT32(pramdac.core_clock_coeff, NV2AState),
        VMSTATE_UINT64(pramdac.core_clock_freq, NV2AState),
        VMSTATE_UINT32(pramdac.memory_clock_coeff, NV2AState),
        VMSTATE_UINT32(pramdac.video_clock_coeff, NV2AState),
        VMSTATE_UINT16(puserdac.write_mode_address, NV2AState),
        VMSTATE_UINT8_ARRAY(puserdac.palette, NV2AState, 256*3),
        VMSTATE_BOOL(pgraph.waiting_for_flip, NV2AState),
        VMSTATE_BOOL(pgraph.waiting_for_nop, NV2AState),
        VMSTATE_UNUSED(1),
        VMSTATE_BOOL(pgraph.waiting_for_context_switch, NV2AState),
        VMSTATE_END_OF_LIST()
    },
};

static void nv2a_class_init(ObjectClass *klass, const void *data)
{
    DeviceClass *dc = DEVICE_CLASS(klass);
    ResettableClass *rc = RESETTABLE_CLASS(klass);
    PCIDeviceClass *k = PCI_DEVICE_CLASS(klass);

    k->vendor_id = PCI_VENDOR_ID_NVIDIA;
    k->device_id = PCI_DEVICE_ID_NVIDIA_GEFORCE_NV2A;
    k->revision  = 0xA1;
    k->class_id  = PCI_CLASS_DISPLAY_VGA;
    /* When both subsystem ids are set to 0, QEMU sets them to its own
     * default values. However we set them anyway in case upstream decides
     * to change this behavior. */
    k->subsystem_vendor_id = 0;
    k->subsystem_id = 0;
    k->realize   = nv2a_realize;
    k->exit      = nv2a_exitfn;

    rc->phases.hold = nv2a_reset_hold;

    dc->desc = "GeForce NV2A Integrated Graphics";
    dc->vmsd = &vmstate_nv2a;
}

static const TypeInfo nv2a_info = {
    .name          = "nv2a",
    .parent        = TYPE_PCI_DEVICE,
    .instance_size = sizeof(NV2AState),
    .class_init    = nv2a_class_init,
    .interfaces          = (InterfaceInfo[]) {
        { INTERFACE_CONVENTIONAL_PCI_DEVICE },
        { },
    },
};

static void nv2a_register(void)
{
    type_register_static(&nv2a_info);
}
type_init(nv2a_register);

void nv2a_init(PCIBus *bus, int devfn, MemoryRegion *ram)
{
    PCIDevice *dev = pci_create_simple(bus, devfn, "nv2a");
    NV2AState *d = NV2A_DEVICE(dev);
    nv2a_init_memory(d, ram);
    nv2a_init_vga(d);
    qemu_add_vm_change_state_handler(nv2a_vm_state_change, d);
}
