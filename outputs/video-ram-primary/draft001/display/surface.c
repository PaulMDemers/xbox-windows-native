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

/*
 * DrvEnableSurface
 *
 * Create engine bitmap around frame buffer and set the video mode requested
 * when PDEV was initialized.
 *
 * Status
 *    @implemented
 */

HSURF APIENTRY
DrvEnableSurface(
   IN DHPDEV dhpdev)
{
   PPDEV ppdev = (PPDEV)dhpdev;
   HSURF hSurface;
   ULONG BitmapType;
   SIZEL ScreenSize;
   VIDEO_MEMORY VideoMemory;
   VIDEO_MEMORY_INFORMATION VideoMemoryInfo;
   ULONG ulTemp;

   if (ppdev->ScreenPtr || ppdev->hSurfEng) return NULL;
   RtlZeroMemory(&VideoMemoryInfo, sizeof(VideoMemoryInfo));

   /*
    * Set video mode of our adapter.
    */

   if (EngDeviceIoControl(ppdev->hDriver, IOCTL_VIDEO_SET_CURRENT_MODE,
                          &(ppdev->ModeIndex), sizeof(ULONG), NULL, 0,
                          &ulTemp))
   {
      return NULL;
   }

   /*
    * Map the framebuffer into our memory.
    */

   VideoMemory.RequestedVirtualAddress = NULL;
   if (EngDeviceIoControl(ppdev->hDriver, IOCTL_VIDEO_MAP_VIDEO_MEMORY,
                          &VideoMemory, sizeof(VIDEO_MEMORY),
                          &VideoMemoryInfo, sizeof(VIDEO_MEMORY_INFORMATION),
                          &ulTemp))
   {
      return NULL;
   }

   /* Bound this prototype to the qualified positive-stride 32-bit contract. */
   ppdev->ScreenPtr = VideoMemoryInfo.VideoRamBase;
   if (ulTemp < sizeof(VideoMemoryInfo) || !ppdev->ScreenPtr ||
       VideoMemoryInfo.FrameBufferBase != ppdev->ScreenPtr ||
       ppdev->BitsPerPixel != 32 || !ppdev->ScreenWidth ||
       ppdev->ScreenWidth > 1920 || !ppdev->ScreenHeight ||
       ppdev->ScreenHeight > 1080 || ppdev->ScreenDelta != ppdev->ScreenWidth * 4 ||
       ppdev->ScreenHeight > 0x400000 / ppdev->ScreenDelta ||
       VideoMemoryInfo.FrameBufferLength < ppdev->ScreenHeight * ppdev->ScreenDelta)
      goto FailMapping;

   switch (ppdev->BitsPerPixel)
   {
      case 8:
         IntSetPalette(dhpdev, ppdev->PaletteEntries, 0, 256);
         BitmapType = BMF_8BPP;
         break;

      case 16:
         BitmapType = BMF_16BPP;
         break;

      case 24:
         BitmapType = BMF_24BPP;
         break;

      case 32:
         BitmapType = BMF_32BPP;
         break;

      default:
         goto FailMapping;
   }

   ppdev->iDitherFormat = BitmapType;

   ScreenSize.cx = ppdev->ScreenWidth;
   ScreenSize.cy = ppdev->ScreenHeight;

   ppdev->ShadowBits=EngAllocMem(FL_ZERO_MEMORY, ppdev->ScreenDelta*ppdev->ScreenHeight, ALLOC_TAG);
   if(!ppdev->ShadowBits) goto FailMapping;
   ppdev->ShadowSurface=(HSURF)EngCreateBitmap(ScreenSize, ppdev->ScreenDelta, BitmapType, BMF_TOPDOWN, ppdev->ShadowBits);
   if(!ppdev->ShadowSurface) goto FailMapping;
   if(!EngAssociateSurface(ppdev->ShadowSurface, ppdev->hDevEng, 0)) goto FailMapping;
   ppdev->ShadowObject=EngLockSurface(ppdev->ShadowSurface);
   if(!ppdev->ShadowObject) goto FailMapping;
   hSurface=EngCreateDeviceSurface((DHSURF)ppdev, ScreenSize, BitmapType);
   if (hSurface == NULL)
   {
      goto FailMapping;
   }

   /*
    * Associate the surface with our device.
    */

   if (!EngAssociateSurface(hSurface, ppdev->hDevEng, HOOK_BITBLT | HOOK_COPYBITS | HOOK_TEXTOUT | HOOK_STROKEPATH | HOOK_FILLPATH | HOOK_STROKEANDFILLPATH | HOOK_LINETO | HOOK_PAINT | HOOK_STRETCHBLT | HOOK_STRETCHBLTROP | HOOK_PLGBLT | HOOK_ALPHABLEND | HOOK_GRADIENTFILL | HOOK_TRANSPARENTBLT))
   {
      EngDeleteSurface(hSurface);
      goto FailMapping;
   }

   ppdev->hSurfEng = hSurface;
   ppdev->ShadowActive=TRUE;
   XwnUpload(ppdev,NULL,NULL);

   return hSurface;

FailMapping:
   ppdev->ShadowActive=FALSE;
   if(ppdev->ShadowObject) EngUnlockSurface(ppdev->ShadowObject);
   ppdev->ShadowObject=NULL;
   if(ppdev->ShadowSurface) EngDeleteSurface(ppdev->ShadowSurface);
   ppdev->ShadowSurface=NULL;
   if(ppdev->ShadowBits) EngFreeMem(ppdev->ShadowBits);
   ppdev->ShadowBits=NULL;
   if (ppdev->ScreenPtr)
   {
      VideoMemory.RequestedVirtualAddress = ppdev->ScreenPtr;
      EngDeviceIoControl(ppdev->hDriver, IOCTL_VIDEO_UNMAP_VIDEO_MEMORY,
                         &VideoMemory, sizeof(VideoMemory), NULL, 0, &ulTemp);
      ppdev->ScreenPtr = NULL;
   }
   return NULL;
}

/*
 * DrvDisableSurface
 *
 * Used by GDI to notify a driver that the surface created by DrvEnableSurface
 * for the current device is no longer needed.
 *
 * Status
 *    @implemented
 */

VOID APIENTRY
DrvDisableSurface(
   IN DHPDEV dhpdev)
{
   DWORD ulTemp;
   VIDEO_MEMORY VideoMemory;
   PPDEV ppdev = (PPDEV)dhpdev;

   ppdev->ShadowActive=FALSE;
   if (ppdev->hSurfEng) EngDeleteSurface(ppdev->hSurfEng);
   ppdev->hSurfEng = NULL;
   ppdev->ShadowActive=FALSE;
   if(ppdev->ShadowObject) EngUnlockSurface(ppdev->ShadowObject);
   ppdev->ShadowObject=NULL;
   if(ppdev->ShadowSurface) EngDeleteSurface(ppdev->ShadowSurface);
   ppdev->ShadowSurface=NULL;
   if(ppdev->ShadowBits) EngFreeMem(ppdev->ShadowBits);
   ppdev->ShadowBits=NULL;


#ifdef EXPERIMENTAL_MOUSE_CURSOR_SUPPORT
   /* Clear all mouse pointer surfaces. */
   DrvSetPointerShape(NULL, NULL, NULL, NULL, 0, 0, 0, 0, NULL, 0);
#endif

   /*
    * Unmap the framebuffer.
    */

   VideoMemory.RequestedVirtualAddress = ((PPDEV)dhpdev)->ScreenPtr;
   if (ppdev->ScreenPtr)
      EngDeviceIoControl(ppdev->hDriver, IOCTL_VIDEO_UNMAP_VIDEO_MEMORY,
                         &VideoMemory, sizeof(VideoMemory), NULL, 0, &ulTemp);
   ppdev->ScreenPtr = NULL;
}

/*
 * DrvAssertMode
 *
 * Sets the mode of the specified physical device to either the mode specified
 * when the PDEV was initialized or to the default mode of the hardware.
 *
 * Status
 *    @implemented
 */

BOOL APIENTRY
DrvAssertMode(
   IN DHPDEV dhpdev,
   IN BOOL bEnable)
{
   PPDEV ppdev = (PPDEV)dhpdev;
   ULONG ulTemp;

   if (bEnable)
   {
      /*
       * Reinitialize the device to a clean state.
       */
      if (EngDeviceIoControl(ppdev->hDriver, IOCTL_VIDEO_SET_CURRENT_MODE,
                             &(ppdev->ModeIndex), sizeof(ULONG), NULL, 0,
                             &ulTemp))
      {
          /* We failed, bail out */
          return FALSE;
      }
      if (ppdev->BitsPerPixel == 8)
      {
	     IntSetPalette(dhpdev, ppdev->PaletteEntries, 0, 256);
      }

      ppdev->ShadowActive=TRUE;
      XwnUpload(ppdev,NULL,NULL);
      return TRUE;
   }
   else
   {
      /*
       * Call the miniport driver to reset the device to a known state.
       */
      ppdev->ShadowActive=FALSE;
      return !EngDeviceIoControl(ppdev->hDriver, IOCTL_VIDEO_RESET_DEVICE,
                                 NULL, 0, NULL, 0, &ulTemp);
   }
}
