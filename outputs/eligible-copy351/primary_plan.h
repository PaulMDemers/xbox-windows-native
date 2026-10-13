/* Bounded same-allocation 32-bit primary copy. SPDX-License-Identifier: GPL-2.0-or-later */
#ifndef XWN_PRIMARY_PLAN_H
#define XWN_PRIMARY_PLAN_H
typedef unsigned int XP_U32;
typedef int XP_I32;
typedef unsigned long long XP_U64;
typedef __UINTPTR_TYPE__ XP_PTR;
typedef char XP_WIDTHS[(sizeof(XP_U32)==4 && sizeof(XP_I32)==4)?1:-1];
typedef struct { XP_I32 left,top,right,bottom; } XP_RECT;
typedef struct { XP_U32 dst,src,bytes,rows,pitch,backward; } XP_PLAN;
/* 0 refuses without modifying the plan; 1 empty; 2 a bounded nonempty copy.
 * The entire original source and destination rectangles must fit before clip.
 * Caller owns the allocation/lifetime and maps only absent/rectangular clips. */
static __inline int XpPlan(XP_PTR base,XP_U32 length,XP_U32 width,XP_U32 height,
                         XP_U32 pitch,const XP_RECT *r,XP_I32 sx,XP_I32 sy,
                         const XP_RECT *clip,XP_PLAN *out)
{
    XP_RECT c; XP_PLAN p; XP_U32 w,h,x,y;
    if(!out || !r || !base || (base&3) || !width || width>1920 || !height ||
       height>1080 || pitch!=width*4 || length!=pitch*height ||
       base>(XP_PTR)-1-length || r->left<0 || r->top<0 ||
       r->right<=r->left || r->bottom<=r->top ||
       (XP_U32)r->right>width || (XP_U32)r->bottom>height || sx<0 || sy<0)
        return 0;
    w=(XP_U32)(r->right-r->left);h=(XP_U32)(r->bottom-r->top);
    if((XP_U32)sx>width-w || (XP_U32)sy>height-h) return 0;
    c=*r;
    if(clip) {
        if(clip->left>clip->right || clip->top>clip->bottom) return 0;
        if(c.left<clip->left)c.left=clip->left;
        if(c.top<clip->top)c.top=clip->top;
        if(c.right>clip->right)c.right=clip->right;
        if(c.bottom>clip->bottom)c.bottom=clip->bottom;
    }
    p.dst=p.src=p.bytes=p.rows=p.backward=0;p.pitch=pitch;
    if(c.left>=c.right || c.top>=c.bottom){*out=p;return 1;}
    x=(XP_U32)sx+(XP_U32)(c.left-r->left);
    y=(XP_U32)sy+(XP_U32)(c.top-r->top);
    p.dst=(XP_U32)c.top*pitch+(XP_U32)c.left*4;
    p.src=y*pitch+x*4;p.bytes=(XP_U32)(c.right-c.left)*4;
    p.rows=(XP_U32)(c.bottom-c.top);p.backward=(XP_U32)c.top>y;
    /* Explicit final-span bounds, independent of earlier rectangle admission. */
    if((XP_U64)p.dst+(XP_U64)(p.rows-1)*pitch+p.bytes>length ||
       (XP_U64)p.src+(XP_U64)(p.rows-1)*pitch+p.bytes>length)return 0;
    *out=p;return 2;
}
/* Private plans only, produced immediately by XpPlan. Horizontal aliasing is
 * delegated to memmove; bottom-up rows preserve downward vertical overlap. */
static __inline void XpExecute(unsigned char *base,const XP_PLAN *p)
{
    XP_U32 i,row;
    for(i=0;i<p->rows;i++) {
        row=p->backward?p->rows-1-i:i;
        memmove(base+p->dst+row*p->pitch,base+p->src+row*p->pitch,p->bytes);
    }
}
#endif
