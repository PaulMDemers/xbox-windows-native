/*
 * ReactOS Generic Framebuffer display driver
 *
 * Copyright (C) 2004 Filip Navara
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License
 * as published by the Free Software Foundation; either version 2
 * of the License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License along
 * with this program; if not, write to the Free Software Foundation, Inc.,
 * 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
 */

#ifndef _FRAMEBUF_PCH_
#define _FRAMEBUF_PCH_

#include <stdarg.h>
#include <windef.h>
#include <wingdi.h>
#include <winddi.h>
#include <winioctl.h>
#include <ntddvdeo.h>

//#define EXPERIMENTAL_MOUSE_CURSOR_SUPPORT

#include "profile_math.h"
typedef struct _PDEV
{
   HANDLE hDriver;
   HDEV hDevEng;
   HSURF hSurfEng;
   HSURF ShadowSurface;
   SURFOBJ *ShadowObject;
   PVOID ShadowBits;
   BOOL ShadowActive;
   ULONG ShadowCalls[14];
   ULONG RowBoxes, RowFast, RowSlow;
   ULONGLONG RowBytes, RowFastBytes;
   XWN_PROFILE Profile;
   ULONG ShadowUploads;
   ULONGLONG ShadowBytes;
   ULONG ModeIndex;
   ULONG ScreenWidth;
   ULONG ScreenHeight;
   ULONG ScreenDelta;
   BYTE BitsPerPixel;
   ULONG RedMask;
   ULONG GreenMask;
   ULONG BlueMask;
   BYTE PaletteShift;
   PVOID ScreenPtr;
   HPALETTE DefaultPalette;
   PALETTEENTRY *PaletteEntries;

#ifdef EXPERIMENTAL_MOUSE_CURSOR_SUPPORT
   VIDEO_POINTER_ATTRIBUTES PointerAttributes;
   XLATEOBJ *PointerXlateObject;
   HSURF PointerColorSurface;
   HSURF PointerMaskSurface;
   HSURF PointerSaveSurface;
   POINTL PointerHotSpot;
#endif

   /* DirectX Support */
   DWORD iDitherFormat;
   ULONG MemHeight;
   ULONG MemWidth;
   DWORD dwHeap;
   VIDEOMEMORY* pvmList;
   BOOL bDDInitialized;
   DDPIXELFORMAT ddpfDisplay;
} PDEV, *PPDEV;

#define DEVICE_NAME	L"xwnram"
#define ALLOC_TAG	'FUBF'


BOOL APIENTRY
DrvEnableDirectDraw(
    DHPDEV dhpdev,
    DD_CALLBACKS *pCallbacks,
    DD_SURFACECALLBACKS *pSurfaceCallbacks,
    DD_PALETTECALLBACKS *pPaletteCallbacks);

VOID APIENTRY
DrvDisableDirectDraw(
    DHPDEV dhpdev);

DHPDEV APIENTRY
DrvEnablePDEV(
   IN DEVMODEW *pdm,
   IN LPWSTR pwszLogAddress,
   IN ULONG cPat,
   OUT HSURF *phsurfPatterns,
   IN ULONG cjCaps,
   OUT ULONG *pdevcaps,
   IN ULONG cjDevInfo,
   OUT DEVINFO *pdi,
   IN HDEV hdev,
   IN LPWSTR pwszDeviceName,
   IN HANDLE hDriver);

VOID APIENTRY
DrvCompletePDEV(
   IN DHPDEV dhpdev,
   IN HDEV hdev);

VOID APIENTRY
DrvDisablePDEV(
   IN DHPDEV dhpdev);

HSURF APIENTRY
DrvEnableSurface(
   IN DHPDEV dhpdev);

VOID APIENTRY
DrvDisableSurface(
   IN DHPDEV dhpdev);

BOOL APIENTRY
DrvAssertMode(
   IN DHPDEV dhpdev,
   IN BOOL bEnable);

ULONG APIENTRY
DrvGetModes(
   IN HANDLE hDriver,
   IN ULONG cjSize,
   OUT DEVMODEW *pdm);

BOOL APIENTRY
DrvSetPalette(
   IN DHPDEV dhpdev,
   IN PALOBJ *ppalo,
   IN FLONG fl,
   IN ULONG iStart,
   IN ULONG cColors);

ULONG APIENTRY
DrvSetPointerShape(
   IN SURFOBJ *pso,
   IN SURFOBJ *psoMask,
   IN SURFOBJ *psoColor,
   IN XLATEOBJ *pxlo,
   IN LONG xHot,
   IN LONG yHot,
   IN LONG x,
   IN LONG y,
   IN RECTL *prcl,
   IN FLONG fl);

VOID APIENTRY
DrvMovePointer(
   IN SURFOBJ *pso,
   IN LONG x,
   IN LONG y,
   IN RECTL *prcl);

BOOL
IntInitScreenInfo(
   PPDEV ppdev,
   LPDEVMODEW pDevMode,
   PGDIINFO pGdiInfo,
   PDEVINFO pDevInfo);

BOOL
IntInitDefaultPalette(
   PPDEV ppdev,
   PDEVINFO pDevInfo);

BOOL APIENTRY
IntSetPalette(
   IN DHPDEV dhpdev,
   IN PPALETTEENTRY ppalent,
   IN ULONG iStart,
   IN ULONG cColors);


VOID XwnUpload(PPDEV p, const RECTL *rect, const CLIPOBJ *clip);
ULONG XwnCheckScanout(PPDEV p);
BOOL APIENTRY XwnBitBlt(SURFOBJ *psoTrg, SURFOBJ *psoSrc, SURFOBJ *psoMask, CLIPOBJ *pco, XLATEOBJ *pxlo, RECTL *prclTrg, POINTL *pptlSrc, POINTL *pptlMask, BRUSHOBJ *pbo, POINTL *pptlBrush, ROP4 rop4);
BOOL APIENTRY XwnCopyBits(SURFOBJ *psoDest, SURFOBJ *psoSrc, CLIPOBJ *pco, XLATEOBJ *pxlo, RECTL *prclDest, POINTL *pptlSrc);
BOOL APIENTRY XwnTextOut(SURFOBJ *pso, STROBJ *pstro, FONTOBJ *pfo, CLIPOBJ *pco, RECTL *prclExtra, RECTL *prclOpaque, BRUSHOBJ *pboFore, BRUSHOBJ *pboOpaque, POINTL *pptlOrg, MIX mix);
BOOL APIENTRY XwnStrokePath(SURFOBJ *pso, PATHOBJ *ppo, CLIPOBJ *pco, XFORMOBJ *pxo, BRUSHOBJ *pbo, POINTL *pptlBrushOrg, LINEATTRS *plineattrs, MIX mix);
BOOL APIENTRY XwnFillPath(SURFOBJ *pso, PATHOBJ *ppo, CLIPOBJ *pco, BRUSHOBJ *pbo, POINTL *pptlBrushOrg, MIX mix, FLONG flOptions);
BOOL APIENTRY XwnStrokeAndFillPath(SURFOBJ *pso, PATHOBJ *ppo, CLIPOBJ *pco, XFORMOBJ *pxo, BRUSHOBJ *pboStroke, LINEATTRS *plineattrs, BRUSHOBJ *pboFill, POINTL *pptlBrushOrg, MIX mixFill, FLONG flOptions);
BOOL APIENTRY XwnLineTo(SURFOBJ *pso, CLIPOBJ *pco, BRUSHOBJ *pbo, LONG x1, LONG y1, LONG x2, LONG y2, RECTL *prclBounds, MIX mix);
BOOL APIENTRY XwnPaint(SURFOBJ *pso, CLIPOBJ *pco, BRUSHOBJ *pbo, POINTL *pptlBrushOrg, MIX mix);
BOOL APIENTRY XwnStretchBlt(SURFOBJ *psoDest, SURFOBJ *psoSrc, SURFOBJ *psoMask, CLIPOBJ *pco, XLATEOBJ *pxlo, COLORADJUSTMENT *pca, POINTL *pptlHTOrg, RECTL *prclDest, RECTL *prclSrc, POINTL *pptlMask, ULONG iMode);
BOOL APIENTRY XwnStretchBltROP(SURFOBJ *psoDest, SURFOBJ *psoSrc, SURFOBJ *psoMask, CLIPOBJ *pco, XLATEOBJ *pxlo, COLORADJUSTMENT *pca, POINTL *pptlHTOrg, RECTL *prclDest, RECTL *prclSrc, POINTL *pptlMask, ULONG iMode, BRUSHOBJ *pbo, DWORD rop4);
BOOL APIENTRY XwnPlgBlt(SURFOBJ *psoTrg, SURFOBJ *psoSrc, SURFOBJ *psoMsk, CLIPOBJ *pco, XLATEOBJ *pxlo, COLORADJUSTMENT *pca, POINTL *pptlBrushOrg, POINTFIX *pptfx, RECTL *prcl, POINTL *pptl, ULONG iMode);
BOOL APIENTRY XwnAlphaBlend(SURFOBJ *psoDest, SURFOBJ *psoSrc, CLIPOBJ *pco, XLATEOBJ *pxlo, RECTL *prclDest, RECTL *prclSrc, BLENDOBJ *pBlendObj);
BOOL APIENTRY XwnGradientFill(SURFOBJ *psoDest, CLIPOBJ *pco, XLATEOBJ *pxlo, TRIVERTEX *pVertex, ULONG nVertex, PVOID pMesh, ULONG nMesh, RECTL *prclExtents, POINTL *pptlDitherOrg, ULONG ulMode);
BOOL APIENTRY XwnTransparentBlt(SURFOBJ *psoDst, SURFOBJ *psoSrc, CLIPOBJ *pco, XLATEOBJ *pxlo, RECTL *prclDst, RECTL *prclSrc, ULONG iTransColor, ULONG ulReserved);

BOOL XwnOwnershipInit(VOID);
VOID APIENTRY XwnOwnershipDisable(VOID);
BOOL XwnRegisterPrimary(PPDEV p);
VOID XwnUnregisterPrimary(PPDEV p);
PPDEV XwnOwner(SURFOBJ *s);
BOOL XwnSelectOwner(PPDEV *selected, SURFOBJ *s);
VOID XwnRowRecord(PPDEV p, ULONG fast, ULONG slow, ULONG bytes);
VOID XwnRowSnapshot(PPDEV p, ULONG *out);
VOID XwnProfileInit(PPDEV);
LONGLONG XwnProfileStart(VOID);
VOID XwnProfileEnd(PPDEV,ULONG,LONGLONG);
VOID XwnProfileSnapshot(PPDEV,ULONG *);
#endif /* _FRAMEBUF_PCH_ */
