/* SPDX-License-Identifier: GPL-2.0-or-later
 * Transfer-only staging geometry. No allocation, MMIO, queue or cache changes.
 * The eventual caller must provide owned resident allocations and serialize
 * their lifetime. A successful plan is NOT permission to submit a GPU command.
 * Define XGT_U32, XGT_U64 and XGT_I32 to the project's exact-width types.
 */
#ifndef XGT_TRANSFER_PLAN_H
#define XGT_TRANSFER_PLAN_H
#define XGT_STAGE_MAX 65536u
#define XGT_SURFACE_MAX 4194304u
typedef struct { XGT_U32 width, height, pitch, bytes; } XGT_LAYOUT;
typedef struct { XGT_I32 left, top, right, bottom; } XGT_RECT;
typedef struct {
    XGT_LAYOUT source, destination;
    XGT_U32 x, y, width_bytes, height, stage_bytes, rows_per_strip;
} XGT_PLAN;
typedef struct {
    XGT_U32 source_offset, destination_offset, row_bytes, rows;
    XGT_U32 packed_bytes, next_row;
} XGT_STRIP;

static int XgtLayoutValid(const XGT_LAYOUT *p)
{
    return p && p->width && p->width <= 1920u && p->height &&
        p->height <= 1080u && !(p->pitch & 3u) &&
        p->pitch >= p->width * 4u && p->pitch <= 8192u &&
        p->bytes <= XGT_SURFACE_MAX &&
        (XGT_U64)p->pitch * p->height <= p->bytes;
}

static int XgtPlan(XGT_PLAN *out, const XGT_LAYOUT *source,
                   const XGT_LAYOUT *destination, const XGT_RECT *rect,
                   XGT_U32 stage_bytes)
{
    XGT_PLAN zero = {0};
    XGT_U32 width_bytes;
    if (!out) return 0;
    *out = zero;
    if (!XgtLayoutValid(source) || !XgtLayoutValid(destination) || !rect ||
        source->width != destination->width ||
        source->height != destination->height ||
        rect->left < 0 || rect->top < 0 || rect->right <= rect->left ||
        rect->bottom <= rect->top || (XGT_U32)rect->right > source->width ||
        (XGT_U32)rect->bottom > source->height || !stage_bytes ||
        stage_bytes > XGT_STAGE_MAX) return 0;
    /* Subtraction occurs only after all signed coordinates are bounded. */
    width_bytes = (XGT_U32)(rect->right - rect->left) * 4u;
    if (width_bytes > stage_bytes) return 0;
    out->source = *source;
    out->destination = *destination;
    out->x = (XGT_U32)rect->left;
    out->y = (XGT_U32)rect->top;
    out->width_bytes = width_bytes;
    out->height = (XGT_U32)(rect->bottom - rect->top);
    out->stage_bytes = stage_bytes;
    out->rows_per_strip = stage_bytes / width_bytes;
    return 1;
}

/* Cursor is relative to the rectangle, never a physical/virtual address.
 * A copied plan stays immutable until the complete transfer is drained.
 * Revalidate it here to fail closed on a malformed/corrupted descriptor.
 */
static int XgtStrip(const XGT_PLAN *p, XGT_U32 cursor, XGT_STRIP *out)
{
    XGT_STRIP zero = {0};
    XGT_U32 rows;
    XGT_U64 source, destination, source_end, destination_end;
    if (!out) return 0;
    *out = zero;
    if (!p || !XgtLayoutValid(&p->source) ||
        !XgtLayoutValid(&p->destination) ||
        p->source.width != p->destination.width ||
        p->source.height != p->destination.height || !p->width_bytes ||
        (p->width_bytes & 3u) || p->width_bytes > p->stage_bytes ||
        p->stage_bytes > XGT_STAGE_MAX || !p->height ||
        p->x >= p->source.width || p->y >= p->source.height ||
        p->width_bytes / 4u > p->source.width - p->x ||
        p->height > p->source.height - p->y ||
        p->rows_per_strip != p->stage_bytes / p->width_bytes ||
        !p->rows_per_strip || cursor >= p->height) return 0;
    rows = p->height - cursor;
    if (rows > p->rows_per_strip) rows = p->rows_per_strip;
    source = (XGT_U64)(p->y + cursor) * p->source.pitch + p->x * 4u;
    destination = (XGT_U64)(p->y + cursor) * p->destination.pitch + p->x * 4u;
    source_end = source + (XGT_U64)(rows - 1u) * p->source.pitch + p->width_bytes;
    destination_end = destination + (XGT_U64)(rows - 1u) * p->destination.pitch + p->width_bytes;
    if (source_end > p->source.bytes || destination_end > p->destination.bytes ||
        (XGT_U64)rows * p->width_bytes > p->stage_bytes) return 0;
    out->source_offset = (XGT_U32)source;
    out->destination_offset = (XGT_U32)destination;
    out->row_bytes = p->width_bytes;
    out->rows = rows;
    out->packed_bytes = rows * p->width_bytes;
    out->next_row = cursor + rows;
    return 1;
}
#endif
