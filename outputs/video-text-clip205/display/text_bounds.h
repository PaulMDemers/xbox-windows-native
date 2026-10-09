/* GPL-2.0-or-later, as framebuf. No coordinate subtraction or pointer enumeration. */
#ifndef XWN_TEXT_BOUNDS_H
#define XWN_TEXT_BOUNDS_H
#include <stdint.h>
typedef struct { int32_t left, top, right, bottom; } XWT_RECT;
enum { XWT_BOUNDED=0, XWT_EMPTY=1, XWT_NO_STRING=2, XWT_EXTRA=3,
       XWT_BAD_STRING=4, XWT_BAD_OPAQUE=5, XWT_ENGINE_FAILED=6 };
static inline int XwtValid(const XWT_RECT *r)
{ return r && r->left<r->right && r->top<r->bottom; }
static inline unsigned XwtBounds(int has_string, uint32_t glyphs,
 const XWT_RECT *string, const XWT_RECT *opaque, int extra, XWT_RECT *out)
{
    XWT_RECT r={0,0,0,0};
    if (!has_string) return XWT_NO_STRING;
    if (extra) return XWT_EXTRA; /* Unexpected on documented GDI calls: never scan it. */
    if (glyphs && !XwtValid(string)) return XWT_BAD_STRING;
    if (opaque && !XwtValid(opaque)) return XWT_BAD_OPAQUE;
    if (glyphs) r=*string;
    if (opaque) {
        if (!glyphs) r=*opaque;
        else {
            if (opaque->left<r.left) r.left=opaque->left;
            if (opaque->top<r.top) r.top=opaque->top;
            if (opaque->right>r.right) r.right=opaque->right;
            if (opaque->bottom>r.bottom) r.bottom=opaque->bottom;
        }
    }
    *out=r;
    return glyphs || opaque ? XWT_BOUNDED : XWT_EMPTY;
}
typedef struct { uint64_t bytes; uint32_t boxes, overflow; } XWT_COPY;
typedef struct {
    uint32_t calls, bounded, fallback, empty, reasons[7], overflow;
    uint64_t bytes;
    uint32_t boxes, last_glyphs, last_reason, last_mode;
    XWT_RECT last;
    XWT_COPY copied;
} XWT_STATS;
static inline void XwtInc(uint32_t *p, uint32_t *overflow)
{ if (*p!=UINT32_MAX) ++*p; else *overflow=1; }
static inline void XwtCopy(XWT_COPY *p, uint64_t bytes)
{
    XwtInc(&p->boxes,&p->overflow);
    if (UINT64_MAX-p->bytes<bytes) {p->bytes=UINT64_MAX;p->overflow=1;}
    else p->bytes+=bytes;
}
static inline void XwtRecord(XWT_STATS *s, unsigned mode, unsigned reason,
 uint32_t glyphs, const XWT_RECT *r, const XWT_COPY *copied)
{
    XwtInc(&s->calls,&s->overflow);
    if (reason>6) {s->overflow=1;return;}
    XwtInc(&s->reasons[reason],&s->overflow);
    if (mode && reason==XWT_BOUNDED) XwtInc(&s->bounded,&s->overflow);
    else if (mode && reason==XWT_EMPTY) XwtInc(&s->empty,&s->overflow);
    else XwtInc(&s->fallback,&s->overflow);
    if (UINT64_MAX-s->bytes<copied->bytes) {s->bytes=UINT64_MAX;s->overflow=1;}
    else s->bytes+=copied->bytes;
    if (UINT32_MAX-s->boxes<copied->boxes) {s->boxes=UINT32_MAX;s->overflow=1;}
    else s->boxes+=copied->boxes;
    s->overflow |= copied->overflow;
    s->last_glyphs=glyphs;s->last_reason=reason;s->last_mode=mode;
    s->last=*r;s->copied=*copied;
}
#endif
