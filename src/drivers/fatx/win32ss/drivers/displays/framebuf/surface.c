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

/* Keep the mapping token until the miniport acknowledges release. */
static VOID
IntUnmapScreen(PPDEV ppdev)
{
   VIDEO_MEMORY Memory;
   ULONG Returned;
   if (!ppdev->VideoRamBase) return;
   Memory.RequestedVirtualAddress = ppdev->VideoRamBase;
   if (!EngDeviceIoControl(ppdev->hDriver, IOCTL_VIDEO_UNMAP_VIDEO_MEMORY,
                          &Memory, sizeof(Memory), NULL, 0, &Returned))
   {
      ppdev->VideoRamBase = NULL;
      ppdev->ScreenPtr = NULL;
   }
}

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

   /* A failed release must not be hidden by a second mapping. */
   if (ppdev->hSurfEng || ppdev->VideoRamBase) return NULL;

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

   ppdev->VideoRamBase = VideoMemoryInfo.VideoRamBase;
   ppdev->ScreenPtr = VideoMemoryInfo.FrameBufferBase;
   if (!ppdev->VideoRamBase || !ppdev->ScreenPtr) goto ReleaseMapping;

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
         goto ReleaseMapping;
   }

   ppdev->iDitherFormat = BitmapType;

   ScreenSize.cx = ppdev->ScreenWidth;
   ScreenSize.cy = ppdev->ScreenHeight;

   hSurface = (HSURF)EngCreateBitmap(ScreenSize, ppdev->ScreenDelta, BitmapType,
                                     (ppdev->ScreenDelta > 0) ? BMF_TOPDOWN : 0,
                                     ppdev->ScreenPtr);
   if (hSurface == NULL)
   {
      goto ReleaseMapping;
   }

   /*
    * Associate the surface with our device.
    */

   if (!EngAssociateSurface(hSurface, ppdev->hDevEng, 0))
   {
      /* Never unmap storage still owned by an engine surface. */
      if (!EngDeleteSurface(hSurface))
      {
         ppdev->hSurfEng = hSurface;
         return NULL;
      }
      goto ReleaseMapping;
   }

   ppdev->hSurfEng = hSurface;

   return hSurface;

ReleaseMapping:
   IntUnmapScreen(ppdev);
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
   PPDEV ppdev = (PPDEV)dhpdev;

   if (ppdev->hSurfEng)
   {
      if (!EngDeleteSurface(ppdev->hSurfEng)) return;
      ppdev->hSurfEng = NULL;
   }

#ifdef EXPERIMENTAL_MOUSE_CURSOR_SUPPORT
   /* Clear all mouse pointer surfaces. */
   DrvSetPointerShape(NULL, NULL, NULL, NULL, 0, 0, 0, 0, NULL, 0);
#endif

   /*
    * Unmap the framebuffer.
    */

   IntUnmapScreen(ppdev);
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

      return TRUE;
   }
   else
   {
      /*
       * Call the miniport driver to reset the device to a known state.
       */
      return !EngDeviceIoControl(ppdev->hDriver, IOCTL_VIDEO_RESET_DEVICE,
                                 NULL, 0, NULL, 0, &ulTemp);
   }
}
