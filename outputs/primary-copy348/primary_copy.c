/* Owned primary-to-primary copies only. SPDX-License-Identifier: GPL-2.0-or-later */
#include "framebuf.h"
#include "primary_plan.h"

int XwnTryPrimaryCopy(PPDEV p,SURFOBJ *dst,SURFOBJ *src,CLIPOBJ *clip,
                      XLATEOBJ *xlate,RECTL *rect,POINTL *point,ULONGLONG *bytes)
{
    SURFOBJ *s; XP_RECT r,c; XP_PLAN plan; int result;
    *bytes=0;
    if(!p || !p->ShadowActive || !dst || !src || !rect || !point ||
       XwnOwner(dst)!=p || XwnOwner(src)!=p || p->BitsPerPixel!=32 ||
       dst->iBitmapFormat!=BMF_32BPP || src->iBitmapFormat!=BMF_32BPP ||
       dst->sizlBitmap.cx!=(LONG)p->ScreenWidth || src->sizlBitmap.cx!=(LONG)p->ScreenWidth ||
       dst->sizlBitmap.cy!=(LONG)p->ScreenHeight || src->sizlBitmap.cy!=(LONG)p->ScreenHeight ||
       (xlate && xlate->flXlate!=XO_TRIVIAL) ||
       (clip && clip->iDComplexity!=DC_TRIVIAL && clip->iDComplexity!=DC_RECT))return -1;
    s=p->ShadowObject;
    if(!s || s->iType!=STYPE_BITMAP || s->iBitmapFormat!=BMF_32BPP ||
       (s->fjBitmap&BMF_NOTSYSMEM) || s->pvBits!=p->ShadowBits || s->pvScan0!=p->ShadowBits ||
       s->hsurf!=p->ShadowSurface || s->hdev!=p->hDevEng ||
       s->sizlBitmap.cx!=(LONG)p->ScreenWidth || s->sizlBitmap.cy!=(LONG)p->ScreenHeight ||
       s->lDelta!=(LONG)p->ScreenDelta || s->cjBits!=p->ScreenDelta*p->ScreenHeight)return -1;
    r.left=rect->left;r.top=rect->top;r.right=rect->right;r.bottom=rect->bottom;
    if(clip && clip->iDComplexity==DC_RECT) {
        c.left=clip->rclBounds.left;c.top=clip->rclBounds.top;
        c.right=clip->rclBounds.right;c.bottom=clip->rclBounds.bottom;
    }
    result=XpPlan((XP_PTR)p->ShadowBits,s->cjBits,p->ScreenWidth,p->ScreenHeight,
                  p->ScreenDelta,&r,point->x,point->y,
                  clip && clip->iDComplexity==DC_RECT?&c:NULL,&plan);
    if(!result)return -1;
    *bytes=(ULONGLONG)plan.bytes*plan.rows;
    if(!XWN_PRIMARY_COPY)return -2; /* Eligible but OFF: call original engine. */
    if(result==1)return 0;
    XpExecute((unsigned char*)p->ShadowBits,&plan);
    return 1;
}
