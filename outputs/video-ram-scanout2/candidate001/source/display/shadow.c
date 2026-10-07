/* RAM-primary prototype. GPL-2.0-or-later, as the containing framebuf driver. */
#include "framebuf.h"
static BOOL XwnRopUsesSource(ROP4 rop)
{
 return ((rop ^ (rop >> 2)) & 0x3333) != 0;
}
static BOOL XwnRopUsesMask(ROP4 rop)
{
 return ((rop ^ (rop >> 8)) & 0xff) != 0;
}
static PPDEV XwnOwner(SURFOBJ *s)
{
 PPDEV p;
 if (!s || s->iType != STYPE_DEVICE || !s->dhpdev || s->dhsurf != (DHSURF)s->dhpdev) return NULL;
 p=(PPDEV)s->dhpdev;
 return p->hSurfEng==s->hsurf && p->ShadowObject ? p : NULL;
}
static SURFOBJ *XwnSub(PPDEV p, SURFOBJ *s)
{
 return s && s->hsurf==p->hSurfEng ? p->ShadowObject : s;
}
VOID XwnUpload(PPDEV p, const RECTL *rect, const CLIPOBJ *clip)
{
 RECTL r; LONG y; ULONG bytes;
 if (!p->ShadowActive || !p->ScreenPtr || !p->ShadowBits) return;
 r.left=0;r.top=0;r.right=p->ScreenWidth;r.bottom=p->ScreenHeight;
 if(rect) {r.left=max(r.left,rect->left);r.top=max(r.top,rect->top);r.right=min(r.right,rect->right);r.bottom=min(r.bottom,rect->bottom);}
 if(clip) {r.left=max(r.left,clip->rclBounds.left);r.top=max(r.top,clip->rclBounds.top);r.right=min(r.right,clip->rclBounds.right);r.bottom=min(r.bottom,clip->rclBounds.bottom);}
 if(r.left>=r.right || r.top>=r.bottom) return;
 bytes=(r.right-r.left)*4;
 for(y=r.top;y<r.bottom;y++) memcpy((BYTE*)p->ScreenPtr+y*p->ScreenDelta+r.left*4,(BYTE*)p->ShadowBits+y*p->ScreenDelta+r.left*4,bytes);
 if(p->ShadowUploads!=0xffffffff) ++p->ShadowUploads;
 p->ShadowBytes+=(ULONGLONG)bytes*(r.bottom-r.top);
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
 PPDEV p=NULL; BOOL ok;
 if (!p && TRUE) p=XwnOwner(psoTrg);
 if (!p && XwnRopUsesSource(rop4)) p=XwnOwner(psoSrc);
 if (!p && XwnRopUsesMask(rop4)) p=XwnOwner(psoMask);
 if (!p || !p->ShadowActive) return FALSE;
 if (p->ShadowCalls[0] != 0xffffffff) ++p->ShadowCalls[0];
 ok=EngBitBlt((TRUE ? XwnSub(p, psoTrg) : NULL), (XwnRopUsesSource(rop4) ? XwnSub(p, psoSrc) : NULL), (XwnRopUsesMask(rop4) ? XwnSub(p, psoMask) : NULL), pco, pxlo, prclTrg, pptlSrc, pptlMask, pbo, pptlBrush, rop4);
 if (XwnOwner(psoTrg)) XwnUpload(p, prclTrg, pco);
 return ok;
}

BOOL APIENTRY XwnCopyBits(SURFOBJ *psoDest, SURFOBJ *psoSrc, CLIPOBJ *pco, XLATEOBJ *pxlo, RECTL *prclDest, POINTL *pptlSrc)
{
 PPDEV p=NULL; BOOL ok;
 if (!p && TRUE) p=XwnOwner(psoDest);
 if (!p && TRUE) p=XwnOwner(psoSrc);
 if (!p || !p->ShadowActive) return FALSE;
 if (p->ShadowCalls[1] != 0xffffffff) ++p->ShadowCalls[1];
 ok=EngCopyBits((TRUE ? XwnSub(p, psoDest) : NULL), (TRUE ? XwnSub(p, psoSrc) : NULL), pco, pxlo, prclDest, pptlSrc);
 if (XwnOwner(psoDest)) XwnUpload(p, prclDest, pco);
 return ok;
}

BOOL APIENTRY XwnTextOut(SURFOBJ *pso, STROBJ *pstro, FONTOBJ *pfo, CLIPOBJ *pco, RECTL *prclExtra, RECTL *prclOpaque, BRUSHOBJ *pboFore, BRUSHOBJ *pboOpaque, POINTL *pptlOrg, MIX mix)
{
 PPDEV p=NULL; BOOL ok;
 if (!p && TRUE) p=XwnOwner(pso);
 if (!p || !p->ShadowActive) return FALSE;
 if (p->ShadowCalls[2] != 0xffffffff) ++p->ShadowCalls[2];
 ok=EngTextOut((TRUE ? XwnSub(p, pso) : NULL), pstro, pfo, pco, prclExtra, prclOpaque, pboFore, pboOpaque, pptlOrg, mix);
 if (XwnOwner(pso)) XwnUpload(p, NULL, pco);
 return ok;
}

BOOL APIENTRY XwnStrokePath(SURFOBJ *pso, PATHOBJ *ppo, CLIPOBJ *pco, XFORMOBJ *pxo, BRUSHOBJ *pbo, POINTL *pptlBrushOrg, LINEATTRS *plineattrs, MIX mix)
{
 PPDEV p=NULL; BOOL ok;
 if (!p && TRUE) p=XwnOwner(pso);
 if (!p || !p->ShadowActive) return FALSE;
 if (p->ShadowCalls[3] != 0xffffffff) ++p->ShadowCalls[3];
 ok=EngStrokePath((TRUE ? XwnSub(p, pso) : NULL), ppo, pco, pxo, pbo, pptlBrushOrg, plineattrs, mix);
 if (XwnOwner(pso)) XwnUpload(p, NULL, pco);
 return ok;
}

BOOL APIENTRY XwnFillPath(SURFOBJ *pso, PATHOBJ *ppo, CLIPOBJ *pco, BRUSHOBJ *pbo, POINTL *pptlBrushOrg, MIX mix, FLONG flOptions)
{
 PPDEV p=NULL; BOOL ok;
 if (!p && TRUE) p=XwnOwner(pso);
 if (!p || !p->ShadowActive) return FALSE;
 if (p->ShadowCalls[4] != 0xffffffff) ++p->ShadowCalls[4];
 ok=EngFillPath((TRUE ? XwnSub(p, pso) : NULL), ppo, pco, pbo, pptlBrushOrg, mix, flOptions);
 if (XwnOwner(pso)) XwnUpload(p, NULL, pco);
 return ok;
}

BOOL APIENTRY XwnStrokeAndFillPath(SURFOBJ *pso, PATHOBJ *ppo, CLIPOBJ *pco, XFORMOBJ *pxo, BRUSHOBJ *pboStroke, LINEATTRS *plineattrs, BRUSHOBJ *pboFill, POINTL *pptlBrushOrg, MIX mixFill, FLONG flOptions)
{
 PPDEV p=NULL; BOOL ok;
 if (!p && TRUE) p=XwnOwner(pso);
 if (!p || !p->ShadowActive) return FALSE;
 if (p->ShadowCalls[5] != 0xffffffff) ++p->ShadowCalls[5];
 ok=EngStrokeAndFillPath((TRUE ? XwnSub(p, pso) : NULL), ppo, pco, pxo, pboStroke, plineattrs, pboFill, pptlBrushOrg, mixFill, flOptions);
 if (XwnOwner(pso)) XwnUpload(p, NULL, pco);
 return ok;
}

BOOL APIENTRY XwnLineTo(SURFOBJ *pso, CLIPOBJ *pco, BRUSHOBJ *pbo, LONG x1, LONG y1, LONG x2, LONG y2, RECTL *prclBounds, MIX mix)
{
 PPDEV p=NULL; BOOL ok;
 if (!p && TRUE) p=XwnOwner(pso);
 if (!p || !p->ShadowActive) return FALSE;
 if (p->ShadowCalls[6] != 0xffffffff) ++p->ShadowCalls[6];
 ok=EngLineTo((TRUE ? XwnSub(p, pso) : NULL), pco, pbo, x1, y1, x2, y2, prclBounds, mix);
 if (XwnOwner(pso)) XwnUpload(p, NULL, pco);
 return ok;
}

BOOL APIENTRY XwnPaint(SURFOBJ *pso, CLIPOBJ *pco, BRUSHOBJ *pbo, POINTL *pptlBrushOrg, MIX mix)
{
 PPDEV p=NULL; BOOL ok;
 if (!p && TRUE) p=XwnOwner(pso);
 if (!p || !p->ShadowActive) return FALSE;
 if (p->ShadowCalls[7] != 0xffffffff) ++p->ShadowCalls[7];
 ok=EngPaint((TRUE ? XwnSub(p, pso) : NULL), pco, pbo, pptlBrushOrg, mix);
 if (XwnOwner(pso)) XwnUpload(p, NULL, pco);
 return ok;
}

BOOL APIENTRY XwnStretchBlt(SURFOBJ *psoDest, SURFOBJ *psoSrc, SURFOBJ *psoMask, CLIPOBJ *pco, XLATEOBJ *pxlo, COLORADJUSTMENT *pca, POINTL *pptlHTOrg, RECTL *prclDest, RECTL *prclSrc, POINTL *pptlMask, ULONG iMode)
{
 PPDEV p=NULL; BOOL ok;
 if (!p && TRUE) p=XwnOwner(psoDest);
 if (!p && TRUE) p=XwnOwner(psoSrc);
 if (!p && TRUE) p=XwnOwner(psoMask);
 if (!p || !p->ShadowActive) return FALSE;
 if (p->ShadowCalls[8] != 0xffffffff) ++p->ShadowCalls[8];
 ok=EngStretchBlt((TRUE ? XwnSub(p, psoDest) : NULL), (TRUE ? XwnSub(p, psoSrc) : NULL), (TRUE ? XwnSub(p, psoMask) : NULL), pco, pxlo, pca, pptlHTOrg, prclDest, prclSrc, pptlMask, iMode);
 if (XwnOwner(psoDest)) XwnUpload(p, NULL, pco);
 return ok;
}

BOOL APIENTRY XwnStretchBltROP(SURFOBJ *psoDest, SURFOBJ *psoSrc, SURFOBJ *psoMask, CLIPOBJ *pco, XLATEOBJ *pxlo, COLORADJUSTMENT *pca, POINTL *pptlHTOrg, RECTL *prclDest, RECTL *prclSrc, POINTL *pptlMask, ULONG iMode, BRUSHOBJ *pbo, DWORD rop4)
{
 PPDEV p=NULL; BOOL ok;
 if (!p && TRUE) p=XwnOwner(psoDest);
 if (!p && XwnRopUsesSource(rop4)) p=XwnOwner(psoSrc);
 if (!p && XwnRopUsesMask(rop4)) p=XwnOwner(psoMask);
 if (!p || !p->ShadowActive) return FALSE;
 if (p->ShadowCalls[9] != 0xffffffff) ++p->ShadowCalls[9];
 ok=EngStretchBltROP((TRUE ? XwnSub(p, psoDest) : NULL), (XwnRopUsesSource(rop4) ? XwnSub(p, psoSrc) : NULL), (XwnRopUsesMask(rop4) ? XwnSub(p, psoMask) : NULL), pco, pxlo, pca, pptlHTOrg, prclDest, prclSrc, pptlMask, iMode, pbo, rop4);
 if (XwnOwner(psoDest)) XwnUpload(p, NULL, pco);
 return ok;
}

BOOL APIENTRY XwnPlgBlt(SURFOBJ *psoTrg, SURFOBJ *psoSrc, SURFOBJ *psoMsk, CLIPOBJ *pco, XLATEOBJ *pxlo, COLORADJUSTMENT *pca, POINTL *pptlBrushOrg, POINTFIX *pptfx, RECTL *prcl, POINTL *pptl, ULONG iMode)
{
 PPDEV p=NULL; BOOL ok;
 if (!p && TRUE) p=XwnOwner(psoTrg);
 if (!p && TRUE) p=XwnOwner(psoSrc);
 if (!p && TRUE) p=XwnOwner(psoMsk);
 if (!p || !p->ShadowActive) return FALSE;
 if (p->ShadowCalls[10] != 0xffffffff) ++p->ShadowCalls[10];
 ok=EngPlgBlt((TRUE ? XwnSub(p, psoTrg) : NULL), (TRUE ? XwnSub(p, psoSrc) : NULL), (TRUE ? XwnSub(p, psoMsk) : NULL), pco, pxlo, pca, pptlBrushOrg, pptfx, prcl, pptl, iMode);
 if (XwnOwner(psoTrg)) XwnUpload(p, NULL, pco);
 return ok;
}

BOOL APIENTRY XwnAlphaBlend(SURFOBJ *psoDest, SURFOBJ *psoSrc, CLIPOBJ *pco, XLATEOBJ *pxlo, RECTL *prclDest, RECTL *prclSrc, BLENDOBJ *pBlendObj)
{
 PPDEV p=NULL; BOOL ok;
 if (!p && TRUE) p=XwnOwner(psoDest);
 if (!p && TRUE) p=XwnOwner(psoSrc);
 if (!p || !p->ShadowActive) return FALSE;
 if (p->ShadowCalls[11] != 0xffffffff) ++p->ShadowCalls[11];
 ok=EngAlphaBlend((TRUE ? XwnSub(p, psoDest) : NULL), (TRUE ? XwnSub(p, psoSrc) : NULL), pco, pxlo, prclDest, prclSrc, pBlendObj);
 if (XwnOwner(psoDest)) XwnUpload(p, prclDest, pco);
 return ok;
}

BOOL APIENTRY XwnGradientFill(SURFOBJ *psoDest, CLIPOBJ *pco, XLATEOBJ *pxlo, TRIVERTEX *pVertex, ULONG nVertex, PVOID pMesh, ULONG nMesh, RECTL *prclExtents, POINTL *pptlDitherOrg, ULONG ulMode)
{
 PPDEV p=NULL; BOOL ok;
 if (!p && TRUE) p=XwnOwner(psoDest);
 if (!p || !p->ShadowActive) return FALSE;
 if (p->ShadowCalls[12] != 0xffffffff) ++p->ShadowCalls[12];
 ok=EngGradientFill((TRUE ? XwnSub(p, psoDest) : NULL), pco, pxlo, pVertex, nVertex, pMesh, nMesh, prclExtents, pptlDitherOrg, ulMode);
 if (XwnOwner(psoDest)) XwnUpload(p, NULL, pco);
 return ok;
}

BOOL APIENTRY XwnTransparentBlt(SURFOBJ *psoDst, SURFOBJ *psoSrc, CLIPOBJ *pco, XLATEOBJ *pxlo, RECTL *prclDst, RECTL *prclSrc, ULONG iTransColor, ULONG ulReserved)
{
 PPDEV p=NULL; BOOL ok;
 if (!p && TRUE) p=XwnOwner(psoDst);
 if (!p && TRUE) p=XwnOwner(psoSrc);
 if (!p || !p->ShadowActive) return FALSE;
 if (p->ShadowCalls[13] != 0xffffffff) ++p->ShadowCalls[13];
 ok=EngTransparentBlt((TRUE ? XwnSub(p, psoDst) : NULL), (TRUE ? XwnSub(p, psoSrc) : NULL), pco, pxlo, prclDst, prclSrc, iTransColor, ulReserved);
 if (XwnOwner(psoDst)) XwnUpload(p, prclDst, pco);
 return ok;
}
