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

#include "framebuf.h"

/* Read-only identity/geometry escape; no pointers or memory writes exposed. */
static ULONG APIENTRY
XwnDirectEscape(SURFOBJ *Surface, ULONG Escape, ULONG InBytes, PVOID In,
                ULONG OutBytes, PVOID Out)
{
   PPDEV p;
   ULONG Data[32]; ULONG i;
   if (InBytes || In || !Surface || !Out || !Surface->dhpdev) return 0;
   p = XwnOwner(Surface);
   if (!p) return 0;
   if (!p->ScreenPtr || !p->hSurfEng || !p->ShadowObject || !p->ShadowActive) return 0;
   if (Escape == 0x58574433 && OutBytes == sizeof(Data))
   {
      XwnProfileSnapshot(p,Data);memcpy(Out,Data,sizeof(Data));return 1;
   }
   if (Escape == 0x58574431 && OutBytes == 32)
   {
      Data[0]=0x44525758;Data[1]=112;Data[2]=p->ScreenWidth;Data[3]=p->ScreenHeight;
      Data[4]=p->ScreenDelta;Data[5]=p->BitsPerPixel;Data[6]=p->ScreenDelta*p->ScreenHeight;Data[7]=1;
      memcpy(Out,Data,32);return 1;
   }
   if (Escape != 0x58574432 || OutBytes != sizeof(Data)) return 0;
   RtlZeroMemory(Data,sizeof(Data));Data[0]=0x53525758;Data[1]=112;
   for(i=0;i<14;i++) Data[2+i]=p->ShadowCalls[i];
   Data[16]=p->ShadowUploads;Data[17]=(ULONG)p->ShadowBytes;Data[18]=(ULONG)(p->ShadowBytes>>32);
   Data[19]=XwnCheckScanout(p);Data[20]=p->ShadowActive;
   memcpy(Out,Data,sizeof(Data));return 1;
}

static DRVFN DrvFunctionTable[] =
{
   {INDEX_DrvDisableDriver, (PFN)XwnOwnershipDisable},
   {INDEX_DrvEscape, (PFN)XwnDirectEscape},
   {INDEX_DrvBitBlt, (PFN)XwnBitBlt},
   {INDEX_DrvCopyBits, (PFN)XwnCopyBits},
   {INDEX_DrvTextOut, (PFN)XwnTextOut},
   {INDEX_DrvStrokePath, (PFN)XwnStrokePath},
   {INDEX_DrvFillPath, (PFN)XwnFillPath},
   {INDEX_DrvStrokeAndFillPath, (PFN)XwnStrokeAndFillPath},
   {INDEX_DrvLineTo, (PFN)XwnLineTo},
   {INDEX_DrvPaint, (PFN)XwnPaint},
   {INDEX_DrvStretchBlt, (PFN)XwnStretchBlt},
   {INDEX_DrvStretchBltROP, (PFN)XwnStretchBltROP},
   {INDEX_DrvPlgBlt, (PFN)XwnPlgBlt},
   {INDEX_DrvAlphaBlend, (PFN)XwnAlphaBlend},
   {INDEX_DrvGradientFill, (PFN)XwnGradientFill},
   {INDEX_DrvTransparentBlt, (PFN)XwnTransparentBlt},

   {INDEX_DrvEnablePDEV, (PFN)DrvEnablePDEV},
   {INDEX_DrvCompletePDEV, (PFN)DrvCompletePDEV},
   {INDEX_DrvDisablePDEV, (PFN)DrvDisablePDEV},
   {INDEX_DrvEnableSurface, (PFN)DrvEnableSurface},
   {INDEX_DrvDisableSurface, (PFN)DrvDisableSurface},
   {INDEX_DrvAssertMode, (PFN)DrvAssertMode},
   {INDEX_DrvGetModes, (PFN)DrvGetModes},
   {INDEX_DrvSetPalette, (PFN)DrvSetPalette},
   {INDEX_DrvSetPointerShape, (PFN)DrvSetPointerShape},
   {INDEX_DrvMovePointer, (PFN)DrvMovePointer},
   {INDEX_DrvEnableDirectDraw, (PFN)DrvEnableDirectDraw},
   {INDEX_DrvDisableDirectDraw, (PFN)DrvDisableDirectDraw},

};

/*
 * DrvEnableDirectDraw
 */

BOOL APIENTRY
DrvEnableDirectDraw(
    DHPDEV dhpdev,
    DD_CALLBACKS *pCallbacks,
    DD_SURFACECALLBACKS *pSurfaceCallbacks,
    DD_PALETTECALLBACKS *pPaletteCallbacks)
{
    RtlZeroMemory(pCallbacks, sizeof(*pCallbacks));
    RtlZeroMemory(pSurfaceCallbacks, sizeof(*pSurfaceCallbacks));
    RtlZeroMemory(pPaletteCallbacks, sizeof(*pPaletteCallbacks));

    pCallbacks->dwSize = sizeof(*pCallbacks);
    pSurfaceCallbacks->dwSize = sizeof(*pSurfaceCallbacks);
    pPaletteCallbacks->dwSize = sizeof(*pPaletteCallbacks);

    /* No direct access may bypass the private RAM primary. */
    return FALSE;
}

/*
 * DrvDisableDirectDraw
 */

VOID APIENTRY
DrvDisableDirectDraw(
    DHPDEV dhpdev)
{
}

/*
 * DrvEnableDriver
 *
 * Initial driver entry point exported by the driver DLL. It fills in a
 * DRVENABLEDATA structure with the driver's DDI version number and the
 * calling addresses of all DDI functions supported by the driver.
 *
 * Status
 *    @implemented
 */

BOOL APIENTRY
DrvEnableDriver(
   ULONG iEngineVersion,
   ULONG cj,
   PDRVENABLEDATA pded)
{
   if (cj >= sizeof(DRVENABLEDATA))
   {
      if (!XwnOwnershipInit()) return FALSE;
      pded->c = sizeof(DrvFunctionTable) / sizeof(DRVFN);
      pded->pdrvfn = DrvFunctionTable;
      pded->iDriverVersion = DDI_DRIVER_VERSION_NT5;
      return TRUE;
   }
   else
   {
      return FALSE;
   }
}

/*
 * DrvEnablePDEV
 *
 * Returns a description of the physical device's characteristics to GDI.
 *
 * Status
 *    @implemented
 */

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
   IN HANDLE hDriver)
{
   PPDEV ppdev;
   GDIINFO GdiInfo;
   DEVINFO DevInfo;

   ppdev = EngAllocMem(FL_ZERO_MEMORY, sizeof(PDEV), ALLOC_TAG);
   if (ppdev == NULL)
   {
      return NULL;
   }

   RtlZeroMemory(&GdiInfo, sizeof(GdiInfo));
   RtlZeroMemory(&DevInfo, sizeof(DevInfo));
   ppdev->hDriver = hDriver;

   if (!IntInitScreenInfo(ppdev, pdm, &GdiInfo, &DevInfo))
   {
      EngFreeMem(ppdev);
      return NULL;
   }

   if (!IntInitDefaultPalette(ppdev, &DevInfo))
   {
      EngFreeMem(ppdev);
      return NULL;
   }

   XwnProfileInit(ppdev);
   memcpy(pdi, &DevInfo, min(sizeof(DEVINFO), cjDevInfo));
   memcpy(pdevcaps, &GdiInfo, min(sizeof(GDIINFO), cjCaps));

   return (DHPDEV)ppdev;
}

/*
 * DrvCompletePDEV
 *
 * Stores the GDI handle (hdev) of the physical device in dhpdev. The driver
 * should retain this handle for use when calling GDI services.
 *
 * Status
 *    @implemented
 */

VOID APIENTRY
DrvCompletePDEV(
   IN DHPDEV dhpdev,
   IN HDEV hdev)
{
   ((PPDEV)dhpdev)->hDevEng = hdev;
}

/*
 * DrvDisablePDEV
 *
 * Release the resources allocated in DrvEnablePDEV.  If a surface has been
 * enabled DrvDisableSurface will have already been called.
 *
 * Status
 *    @implemented
 */

VOID APIENTRY
DrvDisablePDEV(
   IN DHPDEV dhpdev)
{
   if (((PPDEV)dhpdev)->DefaultPalette)
   {
      EngDeletePalette(((PPDEV)dhpdev)->DefaultPalette);
   }

   if (((PPDEV)dhpdev)->PaletteEntries != NULL)
   {
      EngFreeMem(((PPDEV)dhpdev)->PaletteEntries);
   }

   EngFreeMem(dhpdev);
}
