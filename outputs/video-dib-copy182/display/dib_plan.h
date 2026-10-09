/* Bounded 32-bit address geometry, shared by NT5 and host checks.
 * SPDX-License-Identifier: GPL-2.0-or-later */
#ifndef XWN_DIB_PLAN_H
#define XWN_DIB_PLAN_H
typedef unsigned int XD_U32;
typedef int XD_I32;
typedef unsigned long long XD_U64;
typedef long long XD_I64;
typedef char XD_WIDTH_CHECK[(sizeof(XD_U32)==4 && sizeof(XD_I32)==4)?1:-1];
typedef struct { XD_U32 base, size, scan; XD_I32 stride, width, height; } XD_SURFACE;
typedef struct { XD_I32 left, top, right, bottom; } XD_RECT;
typedef struct {
    XD_U32 source, target, bytes, rows;
    XD_I32 source_step, target_step;
} XD_PLAN;
enum { XD_HIT=1, XD_EMPTY, XD_DISABLED, XD_FORMAT, XD_CLIP,
       XD_GEOMETRY, XD_ALIAS };

/* Validate the whole advertised bitmap, including every row's padding-free
 * pixel span. All sums/products precede narrowing and fit signed64 arithmetic.
 * Reject overlapping allocations even if this particular copy is disjoint. */
static int XdSurface(const XD_SURFACE *s)
{
    XD_I64 last, low, high, pitch;
    if (!s->base || !s->size || s->width<=0 || s->height<=0 || !s->stride ||
        (XD_U64)s->base+s->size>0x100000000ULL) return 0;
    pitch=s->stride;
    if (pitch<0) pitch=-pitch;
    if ((XD_I64)s->width*4>pitch) return 0;
    last=(XD_I64)s->scan+(XD_I64)(s->height-1)*s->stride;
    low=last<s->scan?last:s->scan;
    high=(last>s->scan?last:s->scan)+(XD_I64)s->width*4;
    return low>=s->base && high<=(XD_I64)s->base+s->size;
}
static int XdPlan(const XD_SURFACE *dst, const XD_SURFACE *src,
                  XD_RECT r, XD_I32 sx, XD_I32 sy,
                  const XD_RECT *clip, XD_PLAN *out)
{
    XD_I64 w=(XD_I64)r.right-r.left, h=(XD_I64)r.bottom-r.top;
    XD_I64 x=sx, y=sy, from, to;
    XD_PLAN plan;
    if (!XdSurface(dst) || !XdSurface(src) || w<=0 || h<=0 ||
        r.left<0 || r.top<0 || r.right>dst->width || r.bottom>dst->height ||
        sx<0 || sy<0 || x+w>src->width || y+h>src->height) return XD_GEOMETRY;
    if ((XD_U64)dst->base<(XD_U64)src->base+src->size &&
        (XD_U64)src->base<(XD_U64)dst->base+dst->size) return XD_ALIAS;
    if (clip) {
        if (clip->left>clip->right || clip->top>clip->bottom) return XD_CLIP;
        if (r.left<clip->left) { x+=(XD_I64)clip->left-r.left; r.left=clip->left; }
        if (r.top<clip->top) { y+=(XD_I64)clip->top-r.top; r.top=clip->top; }
        if (r.right>clip->right) r.right=clip->right;
        if (r.bottom>clip->bottom) r.bottom=clip->bottom;
        if (r.left>=r.right || r.top>=r.bottom) return XD_EMPTY;
    }
    from=(XD_I64)src->scan+y*src->stride+x*4-src->base;
    to=(XD_I64)dst->scan+(XD_I64)r.top*dst->stride+(XD_I64)r.left*4-dst->base;
    /* Full-surface bounds above imply these spans; keep explicit checks before
     * publishing a plan so callers never partially write on a rejection. */
    w=(XD_I64)r.right-r.left; h=(XD_I64)r.bottom-r.top;
    if (from<0 || to<0 || from+w*4>src->size || to+w*4>dst->size ||
        x<0 || y<0 || x+w>src->width || y+h>src->height) return XD_GEOMETRY;
    plan.source=(XD_U32)from; plan.target=(XD_U32)to;
    plan.bytes=(XD_U32)(w*4); plan.rows=(XD_U32)h;
    plan.source_step=src->stride; plan.target_step=dst->stride;
    *out=plan;
    return XD_HIT;
}
#endif
