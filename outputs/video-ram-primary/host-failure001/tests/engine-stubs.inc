BOOL APIENTRY EngBitBlt(SURFOBJ *psoTrg, SURFOBJ *psoSrc, SURFOBJ *psoMask, CLIPOBJ *pco, XLATEOBJ *pxlo, RECTL *prclTrg, POINTL *pptlSrc, POINTL *pptlMask, BRUSHOBJ *pbo, POINTL *pptlBrush, ROP4 rop4)
{
 (void)psoTrg;
 (void)psoSrc;
 (void)psoMask;
 (void)pco;
 (void)pxlo;
 (void)prclTrg;
 (void)pptlSrc;
 (void)pptlMask;
 (void)pbo;
 (void)pptlBrush;
 (void)rop4;
 assert(psoTrg==ExpectedDest);
 assert(psoSrc==ExpectedOther);
 assert(psoMask==NULL);
 if(WritePixel && ExpectedDest==&Shadow) ((ULONG*)Active->ShadowBits)[0]=0x345678;
 return EngineResult;
}
BOOL APIENTRY EngCopyBits(SURFOBJ *psoDest, SURFOBJ *psoSrc, CLIPOBJ *pco, XLATEOBJ *pxlo, RECTL *prclDest, POINTL *pptlSrc)
{
 (void)psoDest;
 (void)psoSrc;
 (void)pco;
 (void)pxlo;
 (void)prclDest;
 (void)pptlSrc;
 assert(psoDest==ExpectedDest);
 assert(psoSrc==ExpectedOther);
 if(WritePixel && ExpectedDest==&Shadow) ((ULONG*)Active->ShadowBits)[0]=0x345678;
 return EngineResult;
}
BOOL APIENTRY EngTextOut(SURFOBJ *pso, STROBJ *pstro, FONTOBJ *pfo, CLIPOBJ *pco, RECTL *prclExtra, RECTL *prclOpaque, BRUSHOBJ *pboFore, BRUSHOBJ *pboOpaque, POINTL *pptlOrg, MIX mix)
{
 (void)pso;
 (void)pstro;
 (void)pfo;
 (void)pco;
 (void)prclExtra;
 (void)prclOpaque;
 (void)pboFore;
 (void)pboOpaque;
 (void)pptlOrg;
 (void)mix;
 assert(pso==ExpectedDest);
 if(WritePixel && ExpectedDest==&Shadow) ((ULONG*)Active->ShadowBits)[0]=0x345678;
 return EngineResult;
}
BOOL APIENTRY EngStrokePath(SURFOBJ *pso, PATHOBJ *ppo, CLIPOBJ *pco, XFORMOBJ *pxo, BRUSHOBJ *pbo, POINTL *pptlBrushOrg, LINEATTRS *plineattrs, MIX mix)
{
 (void)pso;
 (void)ppo;
 (void)pco;
 (void)pxo;
 (void)pbo;
 (void)pptlBrushOrg;
 (void)plineattrs;
 (void)mix;
 assert(pso==ExpectedDest);
 if(WritePixel && ExpectedDest==&Shadow) ((ULONG*)Active->ShadowBits)[0]=0x345678;
 return EngineResult;
}
BOOL APIENTRY EngFillPath(SURFOBJ *pso, PATHOBJ *ppo, CLIPOBJ *pco, BRUSHOBJ *pbo, POINTL *pptlBrushOrg, MIX mix, FLONG flOptions)
{
 (void)pso;
 (void)ppo;
 (void)pco;
 (void)pbo;
 (void)pptlBrushOrg;
 (void)mix;
 (void)flOptions;
 assert(pso==ExpectedDest);
 if(WritePixel && ExpectedDest==&Shadow) ((ULONG*)Active->ShadowBits)[0]=0x345678;
 return EngineResult;
}
BOOL APIENTRY EngStrokeAndFillPath(SURFOBJ *pso, PATHOBJ *ppo, CLIPOBJ *pco, XFORMOBJ *pxo, BRUSHOBJ *pboStroke, LINEATTRS *plineattrs, BRUSHOBJ *pboFill, POINTL *pptlBrushOrg, MIX mixFill, FLONG flOptions)
{
 (void)pso;
 (void)ppo;
 (void)pco;
 (void)pxo;
 (void)pboStroke;
 (void)plineattrs;
 (void)pboFill;
 (void)pptlBrushOrg;
 (void)mixFill;
 (void)flOptions;
 assert(pso==ExpectedDest);
 if(WritePixel && ExpectedDest==&Shadow) ((ULONG*)Active->ShadowBits)[0]=0x345678;
 return EngineResult;
}
BOOL APIENTRY EngLineTo(SURFOBJ *pso, CLIPOBJ *pco, BRUSHOBJ *pbo, LONG x1, LONG y1, LONG x2, LONG y2, RECTL *prclBounds, MIX mix)
{
 (void)pso;
 (void)pco;
 (void)pbo;
 (void)x1;
 (void)y1;
 (void)x2;
 (void)y2;
 (void)prclBounds;
 (void)mix;
 assert(pso==ExpectedDest);
 if(WritePixel && ExpectedDest==&Shadow) ((ULONG*)Active->ShadowBits)[0]=0x345678;
 return EngineResult;
}
BOOL APIENTRY EngPaint(SURFOBJ *pso, CLIPOBJ *pco, BRUSHOBJ *pbo, POINTL *pptlBrushOrg, MIX mix)
{
 (void)pso;
 (void)pco;
 (void)pbo;
 (void)pptlBrushOrg;
 (void)mix;
 assert(pso==ExpectedDest);
 if(WritePixel && ExpectedDest==&Shadow) ((ULONG*)Active->ShadowBits)[0]=0x345678;
 return EngineResult;
}
BOOL APIENTRY EngStretchBlt(SURFOBJ *psoDest, SURFOBJ *psoSrc, SURFOBJ *psoMask, CLIPOBJ *pco, XLATEOBJ *pxlo, COLORADJUSTMENT *pca, POINTL *pptlHTOrg, RECTL *prclDest, RECTL *prclSrc, POINTL *pptlMask, ULONG iMode)
{
 (void)psoDest;
 (void)psoSrc;
 (void)psoMask;
 (void)pco;
 (void)pxlo;
 (void)pca;
 (void)pptlHTOrg;
 (void)prclDest;
 (void)prclSrc;
 (void)pptlMask;
 (void)iMode;
 assert(psoDest==ExpectedDest);
 assert(psoSrc==ExpectedOther);
 assert(psoMask==NULL);
 if(WritePixel && ExpectedDest==&Shadow) ((ULONG*)Active->ShadowBits)[0]=0x345678;
 return EngineResult;
}
BOOL APIENTRY EngStretchBltROP(SURFOBJ *psoDest, SURFOBJ *psoSrc, SURFOBJ *psoMask, CLIPOBJ *pco, XLATEOBJ *pxlo, COLORADJUSTMENT *pca, POINTL *pptlHTOrg, RECTL *prclDest, RECTL *prclSrc, POINTL *pptlMask, ULONG iMode, BRUSHOBJ *pbo, DWORD rop4)
{
 (void)psoDest;
 (void)psoSrc;
 (void)psoMask;
 (void)pco;
 (void)pxlo;
 (void)pca;
 (void)pptlHTOrg;
 (void)prclDest;
 (void)prclSrc;
 (void)pptlMask;
 (void)iMode;
 (void)pbo;
 (void)rop4;
 assert(psoDest==ExpectedDest);
 assert(psoSrc==ExpectedOther);
 assert(psoMask==NULL);
 if(WritePixel && ExpectedDest==&Shadow) ((ULONG*)Active->ShadowBits)[0]=0x345678;
 return EngineResult;
}
BOOL APIENTRY EngPlgBlt(SURFOBJ *psoTrg, SURFOBJ *psoSrc, SURFOBJ *psoMsk, CLIPOBJ *pco, XLATEOBJ *pxlo, COLORADJUSTMENT *pca, POINTL *pptlBrushOrg, POINTFIX *pptfx, RECTL *prcl, POINTL *pptl, ULONG iMode)
{
 (void)psoTrg;
 (void)psoSrc;
 (void)psoMsk;
 (void)pco;
 (void)pxlo;
 (void)pca;
 (void)pptlBrushOrg;
 (void)pptfx;
 (void)prcl;
 (void)pptl;
 (void)iMode;
 assert(psoTrg==ExpectedDest);
 assert(psoSrc==ExpectedOther);
 assert(psoMsk==ExpectedOther);
 if(WritePixel && ExpectedDest==&Shadow) ((ULONG*)Active->ShadowBits)[0]=0x345678;
 return EngineResult;
}
BOOL APIENTRY EngAlphaBlend(SURFOBJ *psoDest, SURFOBJ *psoSrc, CLIPOBJ *pco, XLATEOBJ *pxlo, RECTL *prclDest, RECTL *prclSrc, BLENDOBJ *pBlendObj)
{
 (void)psoDest;
 (void)psoSrc;
 (void)pco;
 (void)pxlo;
 (void)prclDest;
 (void)prclSrc;
 (void)pBlendObj;
 assert(psoDest==ExpectedDest);
 assert(psoSrc==ExpectedOther);
 if(WritePixel && ExpectedDest==&Shadow) ((ULONG*)Active->ShadowBits)[0]=0x345678;
 return EngineResult;
}
BOOL APIENTRY EngGradientFill(SURFOBJ *psoDest, CLIPOBJ *pco, XLATEOBJ *pxlo, TRIVERTEX *pVertex, ULONG nVertex, PVOID pMesh, ULONG nMesh, RECTL *prclExtents, POINTL *pptlDitherOrg, ULONG ulMode)
{
 (void)psoDest;
 (void)pco;
 (void)pxlo;
 (void)pVertex;
 (void)nVertex;
 (void)pMesh;
 (void)nMesh;
 (void)prclExtents;
 (void)pptlDitherOrg;
 (void)ulMode;
 assert(psoDest==ExpectedDest);
 if(WritePixel && ExpectedDest==&Shadow) ((ULONG*)Active->ShadowBits)[0]=0x345678;
 return EngineResult;
}
BOOL APIENTRY EngTransparentBlt(SURFOBJ *psoDst, SURFOBJ *psoSrc, CLIPOBJ *pco, XLATEOBJ *pxlo, RECTL *prclDst, RECTL *prclSrc, ULONG iTransColor, ULONG ulReserved)
{
 (void)psoDst;
 (void)psoSrc;
 (void)pco;
 (void)pxlo;
 (void)prclDst;
 (void)prclSrc;
 (void)iTransColor;
 (void)ulReserved;
 assert(psoDst==ExpectedDest);
 assert(psoSrc==ExpectedOther);
 if(WritePixel && ExpectedDest==&Shadow) ((ULONG*)Active->ShadowBits)[0]=0x345678;
 return EngineResult;
}
