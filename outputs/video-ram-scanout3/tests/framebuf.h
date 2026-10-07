#ifndef TEST_FRAMEBUF_H
#define TEST_FRAMEBUF_H
#include <stdint.h>
#include <string.h>
#include <stddef.h>
typedef uint32_t ULONG,DWORD,ROP4,MIX,FLONG;
typedef uint64_t ULONGLONG;
typedef int32_t LONG;
typedef unsigned char BYTE;
typedef int BOOL;
typedef void VOID,*PVOID,*HANDLE,*HSURF,*DHPDEV,*DHSURF;
typedef struct {LONG cx,cy;} SIZEL;
typedef struct {LONG x,y;} POINTL,POINTFIX;
typedef struct {LONG left,top,right,bottom;} RECTL;
typedef struct {RECTL rclBounds;} CLIPOBJ;
typedef struct {int unused;} XLATEOBJ,STROBJ,FONTOBJ,BRUSHOBJ,PATHOBJ,XFORMOBJ,LINEATTRS,COLORADJUSTMENT,BLENDOBJ,TRIVERTEX;
typedef struct {ULONG iType; DHPDEV dhpdev; DHSURF dhsurf; HSURF hsurf;} SURFOBJ;
typedef struct {PVOID RequestedVirtualAddress;} VIDEO_MEMORY;
typedef struct {PVOID VideoRamBase;ULONG VideoRamLength;PVOID FrameBufferBase;ULONG FrameBufferLength;} VIDEO_MEMORY_INFORMATION;
typedef struct {HANDLE hDriver,hDevEng;HSURF hSurfEng;PVOID ScreenPtr;ULONG ModeIndex,ScreenWidth,ScreenHeight,ScreenDelta,BitsPerPixel,iDitherFormat;PVOID PaletteEntries;
HSURF ShadowSurface;SURFOBJ *ShadowObject;PVOID ShadowBits;BOOL ShadowActive;ULONG ShadowCalls[14],ShadowUploads;ULONGLONG ShadowBytes;} PDEV,*PPDEV;
#define IN
#define APIENTRY
#define TRUE 1
#define FALSE 0
#define BMF_8BPP 3
#define BMF_16BPP 4
#define BMF_24BPP 5
#define BMF_32BPP 6
#define BMF_TOPDOWN 1
#define FL_ZERO_MEMORY 1
#define ALLOC_TAG 42
#define STYPE_DEVICE 1
#define IOCTL_VIDEO_SET_CURRENT_MODE 1
#define IOCTL_VIDEO_MAP_VIDEO_MEMORY 2
#define IOCTL_VIDEO_UNMAP_VIDEO_MEMORY 3
#define IOCTL_VIDEO_RESET_DEVICE 4
#define RtlZeroMemory(p,n) memset(p,0,n)
#define min(a,b) ((a)<(b)?(a):(b))
#define max(a,b) ((a)>(b)?(a):(b))
ULONG EngDeviceIoControl(HANDLE,ULONG,PVOID,ULONG,PVOID,ULONG,ULONG*);
BOOL IntSetPalette(DHPDEV,PVOID,ULONG,ULONG);
HSURF EngCreateBitmap(SIZEL,LONG,ULONG,ULONG,PVOID);
HSURF EngCreateDeviceSurface(DHSURF,SIZEL,ULONG);
BOOL EngAssociateSurface(HSURF,HANDLE,ULONG);
BOOL EngDeleteSurface(HSURF);
PVOID EngAllocMem(ULONG,ULONG,ULONG);
VOID EngFreeMem(PVOID);
SURFOBJ *EngLockSurface(HSURF);
VOID EngUnlockSurface(SURFOBJ*);
HSURF DrvEnableSurface(DHPDEV);
VOID DrvDisableSurface(DHPDEV);
BOOL DrvAssertMode(DHPDEV,BOOL);
VOID XwnUpload(PPDEV,const RECTL*,const CLIPOBJ*);
ULONG XwnCheckScanout(PPDEV);
#define HOOK_BITBLT (1u<<0)
BOOL APIENTRY XwnBitBlt(SURFOBJ *psoTrg, SURFOBJ *psoSrc, SURFOBJ *psoMask, CLIPOBJ *pco, XLATEOBJ *pxlo, RECTL *prclTrg, POINTL *pptlSrc, POINTL *pptlMask, BRUSHOBJ *pbo, POINTL *pptlBrush, ROP4 rop4);
BOOL APIENTRY EngBitBlt(SURFOBJ *psoTrg, SURFOBJ *psoSrc, SURFOBJ *psoMask, CLIPOBJ *pco, XLATEOBJ *pxlo, RECTL *prclTrg, POINTL *pptlSrc, POINTL *pptlMask, BRUSHOBJ *pbo, POINTL *pptlBrush, ROP4 rop4);
#define HOOK_COPYBITS (1u<<1)
BOOL APIENTRY XwnCopyBits(SURFOBJ *psoDest, SURFOBJ *psoSrc, CLIPOBJ *pco, XLATEOBJ *pxlo, RECTL *prclDest, POINTL *pptlSrc);
BOOL APIENTRY EngCopyBits(SURFOBJ *psoDest, SURFOBJ *psoSrc, CLIPOBJ *pco, XLATEOBJ *pxlo, RECTL *prclDest, POINTL *pptlSrc);
#define HOOK_TEXTOUT (1u<<2)
BOOL APIENTRY XwnTextOut(SURFOBJ *pso, STROBJ *pstro, FONTOBJ *pfo, CLIPOBJ *pco, RECTL *prclExtra, RECTL *prclOpaque, BRUSHOBJ *pboFore, BRUSHOBJ *pboOpaque, POINTL *pptlOrg, MIX mix);
BOOL APIENTRY EngTextOut(SURFOBJ *pso, STROBJ *pstro, FONTOBJ *pfo, CLIPOBJ *pco, RECTL *prclExtra, RECTL *prclOpaque, BRUSHOBJ *pboFore, BRUSHOBJ *pboOpaque, POINTL *pptlOrg, MIX mix);
#define HOOK_STROKEPATH (1u<<3)
BOOL APIENTRY XwnStrokePath(SURFOBJ *pso, PATHOBJ *ppo, CLIPOBJ *pco, XFORMOBJ *pxo, BRUSHOBJ *pbo, POINTL *pptlBrushOrg, LINEATTRS *plineattrs, MIX mix);
BOOL APIENTRY EngStrokePath(SURFOBJ *pso, PATHOBJ *ppo, CLIPOBJ *pco, XFORMOBJ *pxo, BRUSHOBJ *pbo, POINTL *pptlBrushOrg, LINEATTRS *plineattrs, MIX mix);
#define HOOK_FILLPATH (1u<<4)
BOOL APIENTRY XwnFillPath(SURFOBJ *pso, PATHOBJ *ppo, CLIPOBJ *pco, BRUSHOBJ *pbo, POINTL *pptlBrushOrg, MIX mix, FLONG flOptions);
BOOL APIENTRY EngFillPath(SURFOBJ *pso, PATHOBJ *ppo, CLIPOBJ *pco, BRUSHOBJ *pbo, POINTL *pptlBrushOrg, MIX mix, FLONG flOptions);
#define HOOK_STROKEANDFILLPATH (1u<<5)
BOOL APIENTRY XwnStrokeAndFillPath(SURFOBJ *pso, PATHOBJ *ppo, CLIPOBJ *pco, XFORMOBJ *pxo, BRUSHOBJ *pboStroke, LINEATTRS *plineattrs, BRUSHOBJ *pboFill, POINTL *pptlBrushOrg, MIX mixFill, FLONG flOptions);
BOOL APIENTRY EngStrokeAndFillPath(SURFOBJ *pso, PATHOBJ *ppo, CLIPOBJ *pco, XFORMOBJ *pxo, BRUSHOBJ *pboStroke, LINEATTRS *plineattrs, BRUSHOBJ *pboFill, POINTL *pptlBrushOrg, MIX mixFill, FLONG flOptions);
#define HOOK_LINETO (1u<<6)
BOOL APIENTRY XwnLineTo(SURFOBJ *pso, CLIPOBJ *pco, BRUSHOBJ *pbo, LONG x1, LONG y1, LONG x2, LONG y2, RECTL *prclBounds, MIX mix);
BOOL APIENTRY EngLineTo(SURFOBJ *pso, CLIPOBJ *pco, BRUSHOBJ *pbo, LONG x1, LONG y1, LONG x2, LONG y2, RECTL *prclBounds, MIX mix);
#define HOOK_PAINT (1u<<7)
BOOL APIENTRY XwnPaint(SURFOBJ *pso, CLIPOBJ *pco, BRUSHOBJ *pbo, POINTL *pptlBrushOrg, MIX mix);
BOOL APIENTRY EngPaint(SURFOBJ *pso, CLIPOBJ *pco, BRUSHOBJ *pbo, POINTL *pptlBrushOrg, MIX mix);
#define HOOK_STRETCHBLT (1u<<8)
BOOL APIENTRY XwnStretchBlt(SURFOBJ *psoDest, SURFOBJ *psoSrc, SURFOBJ *psoMask, CLIPOBJ *pco, XLATEOBJ *pxlo, COLORADJUSTMENT *pca, POINTL *pptlHTOrg, RECTL *prclDest, RECTL *prclSrc, POINTL *pptlMask, ULONG iMode);
BOOL APIENTRY EngStretchBlt(SURFOBJ *psoDest, SURFOBJ *psoSrc, SURFOBJ *psoMask, CLIPOBJ *pco, XLATEOBJ *pxlo, COLORADJUSTMENT *pca, POINTL *pptlHTOrg, RECTL *prclDest, RECTL *prclSrc, POINTL *pptlMask, ULONG iMode);
#define HOOK_STRETCHBLTROP (1u<<9)
BOOL APIENTRY XwnStretchBltROP(SURFOBJ *psoDest, SURFOBJ *psoSrc, SURFOBJ *psoMask, CLIPOBJ *pco, XLATEOBJ *pxlo, COLORADJUSTMENT *pca, POINTL *pptlHTOrg, RECTL *prclDest, RECTL *prclSrc, POINTL *pptlMask, ULONG iMode, BRUSHOBJ *pbo, DWORD rop4);
BOOL APIENTRY EngStretchBltROP(SURFOBJ *psoDest, SURFOBJ *psoSrc, SURFOBJ *psoMask, CLIPOBJ *pco, XLATEOBJ *pxlo, COLORADJUSTMENT *pca, POINTL *pptlHTOrg, RECTL *prclDest, RECTL *prclSrc, POINTL *pptlMask, ULONG iMode, BRUSHOBJ *pbo, DWORD rop4);
#define HOOK_PLGBLT (1u<<10)
BOOL APIENTRY XwnPlgBlt(SURFOBJ *psoTrg, SURFOBJ *psoSrc, SURFOBJ *psoMsk, CLIPOBJ *pco, XLATEOBJ *pxlo, COLORADJUSTMENT *pca, POINTL *pptlBrushOrg, POINTFIX *pptfx, RECTL *prcl, POINTL *pptl, ULONG iMode);
BOOL APIENTRY EngPlgBlt(SURFOBJ *psoTrg, SURFOBJ *psoSrc, SURFOBJ *psoMsk, CLIPOBJ *pco, XLATEOBJ *pxlo, COLORADJUSTMENT *pca, POINTL *pptlBrushOrg, POINTFIX *pptfx, RECTL *prcl, POINTL *pptl, ULONG iMode);
#define HOOK_ALPHABLEND (1u<<11)
BOOL APIENTRY XwnAlphaBlend(SURFOBJ *psoDest, SURFOBJ *psoSrc, CLIPOBJ *pco, XLATEOBJ *pxlo, RECTL *prclDest, RECTL *prclSrc, BLENDOBJ *pBlendObj);
BOOL APIENTRY EngAlphaBlend(SURFOBJ *psoDest, SURFOBJ *psoSrc, CLIPOBJ *pco, XLATEOBJ *pxlo, RECTL *prclDest, RECTL *prclSrc, BLENDOBJ *pBlendObj);
#define HOOK_GRADIENTFILL (1u<<12)
BOOL APIENTRY XwnGradientFill(SURFOBJ *psoDest, CLIPOBJ *pco, XLATEOBJ *pxlo, TRIVERTEX *pVertex, ULONG nVertex, PVOID pMesh, ULONG nMesh, RECTL *prclExtents, POINTL *pptlDitherOrg, ULONG ulMode);
BOOL APIENTRY EngGradientFill(SURFOBJ *psoDest, CLIPOBJ *pco, XLATEOBJ *pxlo, TRIVERTEX *pVertex, ULONG nVertex, PVOID pMesh, ULONG nMesh, RECTL *prclExtents, POINTL *pptlDitherOrg, ULONG ulMode);
#define HOOK_TRANSPARENTBLT (1u<<13)
BOOL APIENTRY XwnTransparentBlt(SURFOBJ *psoDst, SURFOBJ *psoSrc, CLIPOBJ *pco, XLATEOBJ *pxlo, RECTL *prclDst, RECTL *prclSrc, ULONG iTransColor, ULONG ulReserved);
BOOL APIENTRY EngTransparentBlt(SURFOBJ *psoDst, SURFOBJ *psoSrc, CLIPOBJ *pco, XLATEOBJ *pxlo, RECTL *prclDst, RECTL *prclSrc, ULONG iTransColor, ULONG ulReserved);
#endif
