/* RAM-primary prototype. GPL-2.0-or-later, as the containing framebuf driver. */
#include "framebuf.h"
#include "row_store.h"
static BOOL XwnRopUsesSource(ROP4 rop)
{
 return ((rop ^ (rop >> 2)) & 0x3333) != 0;
}
static BOOL XwnRopUsesMask(ROP4 rop)
{
 return ((rop ^ (rop >> 8)) & 0xff) != 0;
}
static SURFOBJ *XwnSub(PPDEV p, SURFOBJ *s)
{
 return XwnOwner(s)==p ? p->ShadowObject : s;
}
static VOID XwnUploadBox(PPDEV p, const RECTL *r, XWT_COPY *account)
{
 LONG y; ULONG bytes,fast=0,slow=0; LONGLONG begin;
 if (r->left>=r->right || r->top>=r->bottom) return;
 bytes=(r->right-r->left)*4;
 begin=XwnProfileStart();
 for(y=r->top;y<r->bottom;y++) {
  if(XwCopyRow((BYTE*)p->ScreenPtr+y*p->ScreenDelta+r->left*4,
               (BYTE*)p->ShadowBits+y*p->ScreenDelta+r->left*4,bytes,XWN_UC_STORES))++fast;
  else ++slow;
 }
 XwnProfileEnd(p,2,begin);
 XwnRowRecord(p,fast,slow,bytes);
 if(p->ShadowUploads!=0xffffffff) ++p->ShadowUploads;
 p->ShadowBytes+=(ULONGLONG)bytes*(r->bottom-r->top);
 if(account) XwtCopy(account,(ULONGLONG)bytes*(r->bottom-r->top));
}
static VOID XwnUploadInternal(PPDEV p, const RECTL *rect, const CLIPOBJ *clip, XWT_COPY *account)
{
 RECTL r;
 if (!p->ShadowActive || !p->ScreenPtr || !p->ShadowBits) return;
 r.left=0;r.top=0;r.right=p->ScreenWidth;r.bottom=p->ScreenHeight;
 if(rect) {r.left=max(r.left,rect->left);r.top=max(r.top,rect->top);r.right=min(r.right,rect->right);r.bottom=min(r.bottom,rect->bottom);}
 if(clip) {r.left=max(r.left,clip->rclBounds.left);r.top=max(r.top,clip->rclBounds.top);r.right=min(r.right,clip->rclBounds.right);r.bottom=min(r.bottom,clip->rclBounds.bottom);}
 if(r.left>=r.right || r.top>=r.bottom) return;
 if (clip && clip->iDComplexity==DC_COMPLEX)
 {
  struct { ULONG count; RECTL rects[32]; } batch;
  ULONG step,i; BOOL more;
  /* Relevant-only enumeration has no reliable start count on NT5. */
  CLIPOBJ_cEnumStart((CLIPOBJ*)clip,FALSE,CT_RECTANGLES,CD_ANY,0);
  for (step=0;step<256;step++)
  {
   batch.count=0;
   more=CLIPOBJ_bEnum((CLIPOBJ*)clip,sizeof(batch),&batch.count);
   if (batch.count>32) break;
   for (i=0;i<batch.count;i++)
   {
    RECTL part=batch.rects[i];
    if(part.left>part.right || part.top>part.bottom) goto fallback;
    part.left=max(part.left,r.left);part.top=max(part.top,r.top);
    part.right=min(part.right,r.right);part.bottom=min(part.bottom,r.bottom);
    XwnUploadBox(p,&part,account);
   }
   /* FALSE can contain the final nonempty batch; TRUE can contain none. */
   if (!more) return;
  }
 }
 else {XwnUploadBox(p,&r,account);return;}
fallback:
 /* Partial uploads copy completed RAM pixels: repeating the full box is safe. */
 XwnUploadBox(p,&r,account);
}
VOID XwnUpload(PPDEV p, const RECTL *rect, const CLIPOBJ *clip)
{
 LONGLONG begin=XwnProfileStart();
 XwnUploadInternal(p,rect,clip,NULL);
 XwnProfileEnd(p,3,begin);
}
ULONG XwnCheckScanout(PPDEV p)
{
 ULONG i,n=p->ScreenDelta*p->ScreenHeight/4,bad=0;
 volatile ULONG *screen=(volatile ULONG*)p->ScreenPtr; ULONG *ram=(ULONG*)p->ShadowBits;
 for(i=0;i<n;i++) if ((screen[i]&0xffffff)!=(ram[i]&0xffffff)) ++bad;
 return bad;
}
BOOL APIENTRY XwnBitBlt(SURFOBJ *psoTrg, SURFOBJ *psoSrc, SURFOBJ *psoMask, CLIPOBJ *pco, XLATEOBJ *pxlo, RECTL *prclTrg, POINTL *pptlSrc, POINTL *pptlMask, BRUSHOBJ *pbo, POINTL *pptlBrush, ROP4 rop4)
{
 PPDEV p=NULL; BOOL ok; LONGLONG begin;
 if ((TRUE) && !XwnSelectOwner(&p, psoTrg)) return FALSE;
 if ((XwnRopUsesSource(rop4)) && !XwnSelectOwner(&p, psoSrc)) return FALSE;
 if ((XwnRopUsesMask(rop4)) && !XwnSelectOwner(&p, psoMask)) return FALSE;
 if (!p || !p->ShadowActive) return FALSE;
 if (p->ShadowCalls[0] != 0xffffffff) ++p->ShadowCalls[0];
 begin=XwnProfileStart();
 ok=EngBitBlt((TRUE ? XwnSub(p, psoTrg) : NULL), (XwnRopUsesSource(rop4) ? XwnSub(p, psoSrc) : NULL), (XwnRopUsesMask(rop4) ? XwnSub(p, psoMask) : NULL), pco, pxlo, prclTrg, pptlSrc, pptlMask, pbo, pptlBrush, rop4);
 XwnProfileEnd(p,0,begin);
 if (XwnOwner(psoTrg)) XwnUpload(p, prclTrg, pco);
 return ok;
}

BOOL APIENTRY XwnCopyBits(SURFOBJ *psoDest, SURFOBJ *psoSrc, CLIPOBJ *pco, XLATEOBJ *pxlo, RECTL *prclDest, POINTL *pptlSrc)
{
 PPDEV p=NULL; BOOL ok; LONGLONG begin;
 if ((TRUE) && !XwnSelectOwner(&p, psoDest)) return FALSE;
 if ((TRUE) && !XwnSelectOwner(&p, psoSrc)) return FALSE;
 if (!p || !p->ShadowActive) return FALSE;
 if (p->ShadowCalls[1] != 0xffffffff) ++p->ShadowCalls[1];
 begin=XwnProfileStart();
 ok=EngCopyBits((TRUE ? XwnSub(p, psoDest) : NULL), (TRUE ? XwnSub(p, psoSrc) : NULL), pco, pxlo, prclDest, pptlSrc);
 XwnProfileEnd(p,1,begin);
 if (XwnOwner(psoDest)) XwnUpload(p, prclDest, pco);
 return ok;
}

BOOL APIENTRY XwnTextOut(SURFOBJ *pso, STROBJ *pstro, FONTOBJ *pfo, CLIPOBJ *pco, RECTL *prclExtra, RECTL *prclOpaque, BRUSHOBJ *pboFore, BRUSHOBJ *pboOpaque, POINTL *pptlOrg, MIX mix)
{
 PPDEV p=NULL; BOOL ok; ULONG reason; LONGLONG begin;
 XWT_RECT string={0,0,0,0},opaque={0,0,0,0},bound={0,0,0,0};
 RECTL rect,inputClip={0,0,0,0}; ULONG complexity=0; const RECTL *chosen=NULL; XWT_COPY copied={0,0,0}; ULONG glyphs=0;
 if ((TRUE) && !XwnSelectOwner(&p, pso)) return FALSE;
 if (!p || !p->ShadowActive) return FALSE;
 if (p->ShadowCalls[2] != 0xffffffff) ++p->ShadowCalls[2];
 /* Snapshot metadata before Eng can consume an enumeration. No glyph walk. */
 if(pstro) {glyphs=pstro->cGlyphs;string.left=pstro->rclBkGround.left;
  string.top=pstro->rclBkGround.top;string.right=pstro->rclBkGround.right;string.bottom=pstro->rclBkGround.bottom;}
 if(prclOpaque) {opaque.left=prclOpaque->left;opaque.top=prclOpaque->top;
  opaque.right=prclOpaque->right;opaque.bottom=prclOpaque->bottom;}
 if(pco) {inputClip=pco->rclBounds;complexity=pco->iDComplexity;}
 reason=XwtBounds(pstro!=NULL,glyphs,&string,prclOpaque?&opaque:NULL,prclExtra!=NULL,&bound);
 ok=EngTextOut((TRUE ? XwnSub(p, pso) : NULL), pstro, pfo, pco, prclExtra, prclOpaque, pboFore, pboOpaque, pptlOrg, mix);
 if (XwnOwner(pso)) {
  if(!ok) reason=XWT_ENGINE_FAILED;
  if(XWN_TEXT_BOUNDS && reason==XWT_BOUNDED) {
   rect.left=bound.left;rect.top=bound.top;rect.right=bound.right;rect.bottom=bound.bottom;chosen=&rect;
  }
  begin=XwnProfileStart();
  if(!(XWN_TEXT_BOUNDS && reason==XWT_EMPTY)) XwnUploadInternal(p,chosen,pco,&copied);
  XwnProfileEnd(p,3,begin);
  XwnTextRecord(p,reason,glyphs,&bound,&copied,pco?&inputClip:NULL,complexity);
 }
 return ok;
}

BOOL APIENTRY XwnStrokePath(SURFOBJ *pso, PATHOBJ *ppo, CLIPOBJ *pco, XFORMOBJ *pxo, BRUSHOBJ *pbo, POINTL *pptlBrushOrg, LINEATTRS *plineattrs, MIX mix)
{
 PPDEV p=NULL; BOOL ok;
 if ((TRUE) && !XwnSelectOwner(&p, pso)) return FALSE;
 if (!p || !p->ShadowActive) return FALSE;
 if (p->ShadowCalls[3] != 0xffffffff) ++p->ShadowCalls[3];
 ok=EngStrokePath((TRUE ? XwnSub(p, pso) : NULL), ppo, pco, pxo, pbo, pptlBrushOrg, plineattrs, mix);
 if (XwnOwner(pso)) XwnUpload(p, NULL, pco);
 return ok;
}

BOOL APIENTRY XwnFillPath(SURFOBJ *pso, PATHOBJ *ppo, CLIPOBJ *pco, BRUSHOBJ *pbo, POINTL *pptlBrushOrg, MIX mix, FLONG flOptions)
{
 PPDEV p=NULL; BOOL ok;
 if ((TRUE) && !XwnSelectOwner(&p, pso)) return FALSE;
 if (!p || !p->ShadowActive) return FALSE;
 if (p->ShadowCalls[4] != 0xffffffff) ++p->ShadowCalls[4];
 ok=EngFillPath((TRUE ? XwnSub(p, pso) : NULL), ppo, pco, pbo, pptlBrushOrg, mix, flOptions);
 if (XwnOwner(pso)) XwnUpload(p, NULL, pco);
 return ok;
}

BOOL APIENTRY XwnStrokeAndFillPath(SURFOBJ *pso, PATHOBJ *ppo, CLIPOBJ *pco, XFORMOBJ *pxo, BRUSHOBJ *pboStroke, LINEATTRS *plineattrs, BRUSHOBJ *pboFill, POINTL *pptlBrushOrg, MIX mixFill, FLONG flOptions)
{
 PPDEV p=NULL; BOOL ok;
 if ((TRUE) && !XwnSelectOwner(&p, pso)) return FALSE;
 if (!p || !p->ShadowActive) return FALSE;
 if (p->ShadowCalls[5] != 0xffffffff) ++p->ShadowCalls[5];
 ok=EngStrokeAndFillPath((TRUE ? XwnSub(p, pso) : NULL), ppo, pco, pxo, pboStroke, plineattrs, pboFill, pptlBrushOrg, mixFill, flOptions);
 if (XwnOwner(pso)) XwnUpload(p, NULL, pco);
 return ok;
}

BOOL APIENTRY XwnLineTo(SURFOBJ *pso, CLIPOBJ *pco, BRUSHOBJ *pbo, LONG x1, LONG y1, LONG x2, LONG y2, RECTL *prclBounds, MIX mix)
{
 PPDEV p=NULL; BOOL ok;
 if ((TRUE) && !XwnSelectOwner(&p, pso)) return FALSE;
 if (!p || !p->ShadowActive) return FALSE;
 if (p->ShadowCalls[6] != 0xffffffff) ++p->ShadowCalls[6];
 ok=EngLineTo((TRUE ? XwnSub(p, pso) : NULL), pco, pbo, x1, y1, x2, y2, prclBounds, mix);
 /* NT5 supplies conservative bounds including both integer endpoints.
    Keep the old full-clip fallback for absent or degenerate bounds. */
 if (XwnOwner(pso)) XwnUpload(p,
     prclBounds && prclBounds->left < prclBounds->right &&
     prclBounds->top < prclBounds->bottom ? prclBounds : NULL, pco);
 return ok;
}

BOOL APIENTRY XwnPaint(SURFOBJ *pso, CLIPOBJ *pco, BRUSHOBJ *pbo, POINTL *pptlBrushOrg, MIX mix)
{
 PPDEV p=NULL; BOOL ok;
 if ((TRUE) && !XwnSelectOwner(&p, pso)) return FALSE;
 if (!p || !p->ShadowActive) return FALSE;
 if (p->ShadowCalls[7] != 0xffffffff) ++p->ShadowCalls[7];
 ok=EngPaint((TRUE ? XwnSub(p, pso) : NULL), pco, pbo, pptlBrushOrg, mix);
 if (XwnOwner(pso)) XwnUpload(p, NULL, pco);
 return ok;
}

BOOL APIENTRY XwnStretchBlt(SURFOBJ *psoDest, SURFOBJ *psoSrc, SURFOBJ *psoMask, CLIPOBJ *pco, XLATEOBJ *pxlo, COLORADJUSTMENT *pca, POINTL *pptlHTOrg, RECTL *prclDest, RECTL *prclSrc, POINTL *pptlMask, ULONG iMode)
{
 PPDEV p=NULL; BOOL ok;
 if ((TRUE) && !XwnSelectOwner(&p, psoDest)) return FALSE;
 if ((TRUE) && !XwnSelectOwner(&p, psoSrc)) return FALSE;
 if ((TRUE) && !XwnSelectOwner(&p, psoMask)) return FALSE;
 if (!p || !p->ShadowActive) return FALSE;
 if (p->ShadowCalls[8] != 0xffffffff) ++p->ShadowCalls[8];
 ok=EngStretchBlt((TRUE ? XwnSub(p, psoDest) : NULL), (TRUE ? XwnSub(p, psoSrc) : NULL), (TRUE ? XwnSub(p, psoMask) : NULL), pco, pxlo, pca, pptlHTOrg, prclDest, prclSrc, pptlMask, iMode);
 if (XwnOwner(psoDest)) XwnUpload(p, NULL, pco);
 return ok;
}

BOOL APIENTRY XwnStretchBltROP(SURFOBJ *psoDest, SURFOBJ *psoSrc, SURFOBJ *psoMask, CLIPOBJ *pco, XLATEOBJ *pxlo, COLORADJUSTMENT *pca, POINTL *pptlHTOrg, RECTL *prclDest, RECTL *prclSrc, POINTL *pptlMask, ULONG iMode, BRUSHOBJ *pbo, DWORD rop4)
{
 PPDEV p=NULL; BOOL ok;
 if ((TRUE) && !XwnSelectOwner(&p, psoDest)) return FALSE;
 if ((XwnRopUsesSource(rop4)) && !XwnSelectOwner(&p, psoSrc)) return FALSE;
 if ((XwnRopUsesMask(rop4)) && !XwnSelectOwner(&p, psoMask)) return FALSE;
 if (!p || !p->ShadowActive) return FALSE;
 if (p->ShadowCalls[9] != 0xffffffff) ++p->ShadowCalls[9];
 ok=EngStretchBltROP((TRUE ? XwnSub(p, psoDest) : NULL), (XwnRopUsesSource(rop4) ? XwnSub(p, psoSrc) : NULL), (XwnRopUsesMask(rop4) ? XwnSub(p, psoMask) : NULL), pco, pxlo, pca, pptlHTOrg, prclDest, prclSrc, pptlMask, iMode, pbo, rop4);
 if (XwnOwner(psoDest)) XwnUpload(p, NULL, pco);
 return ok;
}

BOOL APIENTRY XwnPlgBlt(SURFOBJ *psoTrg, SURFOBJ *psoSrc, SURFOBJ *psoMsk, CLIPOBJ *pco, XLATEOBJ *pxlo, COLORADJUSTMENT *pca, POINTL *pptlBrushOrg, POINTFIX *pptfx, RECTL *prcl, POINTL *pptl, ULONG iMode)
{
 PPDEV p=NULL; BOOL ok;
 if ((TRUE) && !XwnSelectOwner(&p, psoTrg)) return FALSE;
 if ((TRUE) && !XwnSelectOwner(&p, psoSrc)) return FALSE;
 if ((TRUE) && !XwnSelectOwner(&p, psoMsk)) return FALSE;
 if (!p || !p->ShadowActive) return FALSE;
 if (p->ShadowCalls[10] != 0xffffffff) ++p->ShadowCalls[10];
 ok=EngPlgBlt((TRUE ? XwnSub(p, psoTrg) : NULL), (TRUE ? XwnSub(p, psoSrc) : NULL), (TRUE ? XwnSub(p, psoMsk) : NULL), pco, pxlo, pca, pptlBrushOrg, pptfx, prcl, pptl, iMode);
 if (XwnOwner(psoTrg)) XwnUpload(p, NULL, pco);
 return ok;
}

BOOL APIENTRY XwnAlphaBlend(SURFOBJ *psoDest, SURFOBJ *psoSrc, CLIPOBJ *pco, XLATEOBJ *pxlo, RECTL *prclDest, RECTL *prclSrc, BLENDOBJ *pBlendObj)
{
 PPDEV p=NULL; BOOL ok;
 if ((TRUE) && !XwnSelectOwner(&p, psoDest)) return FALSE;
 if ((TRUE) && !XwnSelectOwner(&p, psoSrc)) return FALSE;
 if (!p || !p->ShadowActive) return FALSE;
 if (p->ShadowCalls[11] != 0xffffffff) ++p->ShadowCalls[11];
 ok=EngAlphaBlend((TRUE ? XwnSub(p, psoDest) : NULL), (TRUE ? XwnSub(p, psoSrc) : NULL), pco, pxlo, prclDest, prclSrc, pBlendObj);
 if (XwnOwner(psoDest)) XwnUpload(p, prclDest, pco);
 return ok;
}

BOOL APIENTRY XwnGradientFill(SURFOBJ *psoDest, CLIPOBJ *pco, XLATEOBJ *pxlo, TRIVERTEX *pVertex, ULONG nVertex, PVOID pMesh, ULONG nMesh, RECTL *prclExtents, POINTL *pptlDitherOrg, ULONG ulMode)
{
 PPDEV p=NULL; BOOL ok;
 if ((TRUE) && !XwnSelectOwner(&p, psoDest)) return FALSE;
 if (!p || !p->ShadowActive) return FALSE;
 if (p->ShadowCalls[12] != 0xffffffff) ++p->ShadowCalls[12];
 ok=EngGradientFill((TRUE ? XwnSub(p, psoDest) : NULL), pco, pxlo, pVertex, nVertex, pMesh, nMesh, prclExtents, pptlDitherOrg, ulMode);
 if (XwnOwner(psoDest)) XwnUpload(p, NULL, pco);
 return ok;
}

BOOL APIENTRY XwnTransparentBlt(SURFOBJ *psoDst, SURFOBJ *psoSrc, CLIPOBJ *pco, XLATEOBJ *pxlo, RECTL *prclDst, RECTL *prclSrc, ULONG iTransColor, ULONG ulReserved)
{
 PPDEV p=NULL; BOOL ok;
 if ((TRUE) && !XwnSelectOwner(&p, psoDst)) return FALSE;
 if ((TRUE) && !XwnSelectOwner(&p, psoSrc)) return FALSE;
 if (!p || !p->ShadowActive) return FALSE;
 if (p->ShadowCalls[13] != 0xffffffff) ++p->ShadowCalls[13];
 ok=EngTransparentBlt((TRUE ? XwnSub(p, psoDst) : NULL), (TRUE ? XwnSub(p, psoSrc) : NULL), pco, pxlo, prclDst, prclSrc, iTransColor, ulReserved);
 if (XwnOwner(psoDst)) XwnUpload(p, prclDst, pco);
 return ok;
}
