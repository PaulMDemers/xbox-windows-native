/*
 * PROJECT: Experimental native Windows 2000 Xbox framebuffer miniport
 * LICENSE: GPL-2.0-or-later
 * Derived from ReactOS xboxvmp (Ge van Geldorp, Filip Navara,
 * Stanislav Motylkov). See ../xboxvmp.c and ReactOS COPYING.
 * Retains firmware's mode; no acceleration, palette or mode switching.
 */
#include "../xboxvmp.h"
#include <drivers/xbox/xgpu.h>
#ifdef XBOX_NT5_SHARED_FRAMEBUFFER
ULONG NTAPI XwnSharedMap(PVOID, ULONG, ULONG, ULONG, ULONG, PVOID *);
ULONG NTAPI XwnSharedUnmap(PVOID, PVOID);
#endif

#ifdef XBOX_NT5_VIDEO_DIAGNOSTIC
/* Deliberate diagnostic stop: preserve the first failing native video stage.
 * Stage 1: VideoPortInitialize; 2: PCI ranges; 3: range sizes; 4: register map;
 * 5: firmware geometry; 6: aperture bounds; 7: framebuffer map.
 * No GPU mode changes or disk writes are introduced by this diagnostic. */
NTSYSAPI VOID NTAPI KeBugCheckEx(ULONG, ULONG_PTR, ULONG_PTR, ULONG_PTR, ULONG_PTR);
#define VIDEO_FAIL(stage, a, b, c) KeBugCheckEx(0xE0580001, stage, a, b, c)
#else
#define VIDEO_FAIL(stage, a, b, c) ((void)0)
#endif

typedef struct {
    PVOID Control;
    PHYSICAL_ADDRESS ControlPhysical, FramebufferAperture, Framebuffer;
    ULONG ApertureLength, Offset;
    VIDEO_MODE_INFORMATION Mode;
    BOOLEAN Ready;
} NT5_VIDEO, *PNT5_VIDEO;

C_ASSERT(SIZE_OF_W2K_VIDEO_HW_INITIALIZATION_DATA == 80);
C_ASSERT(sizeof(VIDEO_MODE_INFORMATION) == 80);
C_ASSERT(sizeof(VIDEO_MEMORY_INFORMATION) == 16);

static UCHAR Crtc(PNT5_VIDEO V, UCHAR Index)
{
    WRITE_REGISTER_UCHAR((PUCHAR)V->Control + NV2A_CRTC_REGISTER_INDEX, Index);
    return READ_REGISTER_UCHAR((PUCHAR)V->Control + NV2A_CRTC_REGISTER_VALUE);
}

VP_STATUS NTAPI
Nt5VideoFindAdapter(PVOID Extension, PVOID Context, PWSTR Arguments,
                   PVIDEO_PORT_CONFIG_INFO Config, PUCHAR Again)
{
    PNT5_VIDEO V = Extension;
    VIDEO_ACCESS_RANGE Ranges[3];
    USHORT Vendor = 0x10de, Device = 0x02a0;
    ULONG Slot = 0;
    VP_STATUS Status;
    *Again = FALSE;
    VideoPortZeroMemory(Ranges, sizeof(Ranges));
    Status = VideoPortGetAccessRanges(Extension, 0, NULL, 3, Ranges, &Vendor, &Device, &Slot);
    if (Status != NO_ERROR) { VIDEO_FAIL(2, Status, Config->SystemIoBusNumber, Slot); return Status; }
    if (Ranges[0].RangeInIoSpace || Ranges[1].RangeInIoSpace ||
        Ranges[0].RangeLength < NV2A_RAMDAC_FP_HVALID_END + sizeof(ULONG) ||
        Ranges[1].RangeLength < NV2A_VIDEO_MEMORY_SIZE)
    { VIDEO_FAIL(3, Ranges[0].RangeLength, Ranges[1].RangeLength,
                 Ranges[0].RangeInIoSpace | (Ranges[1].RangeInIoSpace << 8));
      return ERROR_DEV_NOT_EXIST; }
    V->ControlPhysical = Ranges[0].RangeStart;
    V->FramebufferAperture = Ranges[1].RangeStart;
    V->ApertureLength = Ranges[1].RangeLength;
#ifdef XBOX_NT5_VIDEO_ADAPTER_DIAGNOSTIC
    /* Preserve Windows-assigned resources before hardware initialization. */
    VIDEO_FAIL(8, V->ControlPhysical.LowPart,
               V->FramebufferAperture.LowPart, V->ApertureLength);
#endif
    return NO_ERROR;
}

BOOLEAN NTAPI
Nt5VideoInitialize(PVOID Extension)
{
    PNT5_VIDEO V = Extension;
    ULONG Width, Height, Pitch, Bytes, Format;
    V->Ready = FALSE;
    V->Control = VideoPortGetDeviceBase(Extension, V->ControlPhysical, 0x681000, 0);
    if (!V->Control) { VIDEO_FAIL(4, V->ControlPhysical.LowPart, V->ControlPhysical.HighPart, 0); return FALSE; }
    Width = READ_REGISTER_ULONG((PULONG)((PUCHAR)V->Control + NV2A_RAMDAC_FP_HVALID_END)) + 1;
    Height = READ_REGISTER_ULONG((PULONG)((PUCHAR)V->Control + NV2A_RAMDAC_FP_VVALID_END)) + 1;
    Pitch = 8 * (((Crtc(V, 0x19) & 0xe0) << 3) | Crtc(V, 0x13));
    Format = Crtc(V, 0x28) & 15;
    Bytes = (Format == 3) ? 4 : Format;
    V->Offset = READ_REGISTER_ULONG((PULONG)((PUCHAR)V->Control + NV2A_CRTC_FRAMEBUFFER_START)) & 0x0fffffff;
    /* This experiment supports the firmware's direct RGB mode only. The
       framebuffer must stay inside Cromwell's reserved top-four-MiB area. */
    if (Width < 320 || Width > 1920 || Height < 200 || Height > 1080 || Bytes != 4 ||
        Pitch < Width * Bytes || Pitch > 8192 || Height > NV2A_VIDEO_MEMORY_SIZE / Pitch ||
#ifdef XBOX_NT5_HD_RESERVATION
        !XwnHdLayoutValid(V->Offset, NV2A_VIDEO_MEMORY_SIZE, Width, Height, Pitch, XWN_HD_HIDDEN_OFFSET) ||
#else
        (V->Offset != 0x03c00000 && V->Offset != 0x07c00000) ||
#endif
        V->Offset > V->ApertureLength - NV2A_VIDEO_MEMORY_SIZE)
    {
        if (Width < 320 || Width > 1920 || Height < 200 || Height > 1080 || Bytes != 4 ||
            Pitch < Width * Bytes || Pitch > 8192 || Height > NV2A_VIDEO_MEMORY_SIZE / Pitch)
            VIDEO_FAIL(5, Width, Height, (Pitch << 8) | Format);
        else
            VIDEO_FAIL(6, V->Offset, V->ApertureLength, V->FramebufferAperture.LowPart);
        VideoPortFreeDeviceBase(Extension, V->Control);V->Control = NULL;return FALSE;
    }
    V->Framebuffer.QuadPart = V->FramebufferAperture.QuadPart + V->Offset;
    VideoPortZeroMemory(&V->Mode, sizeof(V->Mode));
    V->Mode.Length = sizeof(V->Mode);
    V->Mode.VisScreenWidth = Width; V->Mode.VisScreenHeight = Height;
    V->Mode.ScreenStride = Pitch; V->Mode.NumberOfPlanes = 1; V->Mode.BitsPerPlane = 32;
    V->Mode.Frequency = 60;
    /* No EDID is available for the retained firmware mode. Supply a 96-DPI
     * logical size: NT5 framebuf passes these fields to GDI, and Paint divides
     * by HORZSIZE/VERTSIZE when converting between pixels and physical units.
     * These are fallback dimensions, not measurements of the connected TV. */
    V->Mode.XMillimeter = (Width * 254 + 480) / 960;
    V->Mode.YMillimeter = (Height * 254 + 480) / 960;
    V->Mode.NumberRedBits = V->Mode.NumberGreenBits = V->Mode.NumberBlueBits = 8;
    V->Mode.RedMask = 0xff0000; V->Mode.GreenMask = 0xff00; V->Mode.BlueMask = 0xff;
    V->Mode.AttributeFlags = VIDEO_MODE_GRAPHICS | VIDEO_MODE_COLOR | VIDEO_MODE_NO_OFF_SCREEN;
    V->Mode.VideoMemoryBitmapWidth = Pitch / 4; V->Mode.VideoMemoryBitmapHeight = Height;
    V->Ready = TRUE;
    return TRUE;
}

BOOLEAN NTAPI
Nt5VideoStartIO(PVOID Extension, PVIDEO_REQUEST_PACKET Request)
{
    PNT5_VIDEO V = Extension;
    VP_STATUS Status = ERROR_INVALID_FUNCTION;
    Request->StatusBlock->Information = 0;
    if (!V->Ready) { Request->StatusBlock->Status = ERROR_DEV_NOT_EXIST; return TRUE; }
    switch (Request->IoControlCode)
    {
    case IOCTL_VIDEO_QUERY_NUM_AVAIL_MODES:
        if (!Request->OutputBuffer || Request->OutputBufferLength < sizeof(VIDEO_NUM_MODES))
            { Status = ERROR_INSUFFICIENT_BUFFER; break; }
        ((PVIDEO_NUM_MODES)Request->OutputBuffer)->NumModes = 1;
        ((PVIDEO_NUM_MODES)Request->OutputBuffer)->ModeInformationLength = sizeof(V->Mode);
        Request->StatusBlock->Information = sizeof(VIDEO_NUM_MODES);Status = NO_ERROR;break;
    case IOCTL_VIDEO_QUERY_AVAIL_MODES:
    case IOCTL_VIDEO_QUERY_CURRENT_MODE:
        if (!Request->OutputBuffer || Request->OutputBufferLength < sizeof(V->Mode))
            { Status = ERROR_INSUFFICIENT_BUFFER; break; }
        *(PVIDEO_MODE_INFORMATION)Request->OutputBuffer = V->Mode;
        Request->StatusBlock->Information = sizeof(V->Mode);Status = NO_ERROR;break;
    case IOCTL_VIDEO_SET_CURRENT_MODE:
        if (!Request->InputBuffer || Request->InputBufferLength < sizeof(VIDEO_MODE))
            { Status = ERROR_INSUFFICIENT_BUFFER; break; }
        Status = (((PVIDEO_MODE)Request->InputBuffer)->RequestedMode &
                  ~(VIDEO_MODE_MAP_MEM_LINEAR | VIDEO_MODE_NO_ZERO_MEMORY)) ? ERROR_INVALID_PARAMETER : NO_ERROR;
        break;
    case IOCTL_VIDEO_RESET_DEVICE:
        Status = NO_ERROR;break;
    case IOCTL_VIDEO_MAP_VIDEO_MEMORY:
        if (!Request->InputBuffer || !Request->OutputBuffer ||
            Request->InputBufferLength < sizeof(VIDEO_MEMORY) ||
            Request->OutputBufferLength < sizeof(VIDEO_MEMORY_INFORMATION))
            { Status = ERROR_INSUFFICIENT_BUFFER; break; }
        {
            VIDEO_MEMORY_INFORMATION Result;
#ifndef XBOX_NT5_SHARED_FRAMEBUFFER
            ULONG Space = VIDEO_MEMORY_SPACE_MEMORY;
#endif
            VideoPortZeroMemory(&Result, sizeof(Result));
            Result.VideoRamBase = ((PVIDEO_MEMORY)Request->InputBuffer)->RequestedVirtualAddress;
            Result.VideoRamLength = NV2A_VIDEO_MEMORY_SIZE;
#ifdef XBOX_NT5_SHARED_FRAMEBUFFER
            Status = XwnSharedMap(Extension, V->Offset, V->Mode.VisScreenWidth,
                                  V->Mode.VisScreenHeight, V->Mode.ScreenStride, &Result.VideoRamBase);
#else
            Status = VideoPortMapMemory(Extension, V->Framebuffer, &Result.VideoRamLength,
                                        &Space, &Result.VideoRamBase);
#endif
            if (Status != NO_ERROR) { VIDEO_FAIL(7, Status, V->Framebuffer.LowPart, Result.VideoRamLength); break; }
            Result.FrameBufferBase = Result.VideoRamBase;
            Result.FrameBufferLength = V->Mode.ScreenStride * V->Mode.VisScreenHeight;
            *(PVIDEO_MEMORY_INFORMATION)Request->OutputBuffer = Result;
            Request->StatusBlock->Information = sizeof(Result);
        }
        break;
    case IOCTL_VIDEO_UNMAP_VIDEO_MEMORY:
        if (!Request->InputBuffer || Request->InputBufferLength < sizeof(VIDEO_MEMORY))
            { Status = ERROR_INSUFFICIENT_BUFFER; break; }
#ifdef XBOX_NT5_SHARED_FRAMEBUFFER
        Status = XwnSharedUnmap(Extension, ((PVIDEO_MEMORY)Request->InputBuffer)->RequestedVirtualAddress);
#else
        Status = VideoPortUnmapMemory(Extension, ((PVIDEO_MEMORY)Request->InputBuffer)->RequestedVirtualAddress, NULL);
#endif
        break;
    }
    Request->StatusBlock->Status = Status;
    return TRUE;
}

BOOLEAN NTAPI Nt5VideoReset(PVOID Extension, ULONG Columns, ULONG Rows) { return TRUE; }
VP_STATUS NTAPI Nt5VideoPower(PVOID Extension, ULONG Id, PVIDEO_POWER_MANAGEMENT Power)
{ return Power->PowerState == VideoPowerOn ? NO_ERROR : ERROR_INVALID_FUNCTION; }
VP_STATUS NTAPI Nt5VideoChild(PVOID Extension, PVIDEO_CHILD_ENUM_INFO Info,
                             PVIDEO_CHILD_TYPE Type, PUCHAR Descriptor, PULONG Id, PULONG Unused)
{ return VIDEO_ENUM_NO_MORE_DEVICES; }

#ifdef XBOX_NT5_VIDEO_PNP_DIAGNOSTIC
VOID NTAPI XwnVideoArmPnp(PVOID Driver);
#endif
ULONG NTAPI DriverEntry(PVOID Context1, PVOID Context2)
{
    VIDEO_HW_INITIALIZATION_DATA Init;
    ULONG Status;
#ifdef XBOX_NT5_VIDEO_ENTRY_DIAGNOSTIC
    /* Prove invocation independently of PnP or VideoPort callbacks. */
    VIDEO_FAIL(0, (ULONG_PTR)Context1, (ULONG_PTR)Context2, 0x56454E54);
#endif
    VideoPortZeroMemory(&Init, sizeof(Init));
    Init.HwInitDataSize = SIZE_OF_W2K_VIDEO_HW_INITIALIZATION_DATA;
    Init.AdapterInterfaceType = PCIBus;
    Init.HwDeviceExtensionSize = sizeof(NT5_VIDEO);
    Init.HwFindAdapter = Nt5VideoFindAdapter; Init.HwInitialize = Nt5VideoInitialize;
    Init.HwStartIO = Nt5VideoStartIO; Init.HwResetHw = Nt5VideoReset;
    Init.HwGetPowerState = Nt5VideoPower; Init.HwSetPowerState = Nt5VideoPower;
    Init.HwGetVideoChildDescriptor = Nt5VideoChild;
    Status = VideoPortInitialize(Context1, Context2, &Init, NULL);
    if (Status != NO_ERROR) VIDEO_FAIL(1, Status, 0, 0);
#ifdef XBOX_NT5_VIDEO_PNP_DIAGNOSTIC
    if (Status == NO_ERROR) XwnVideoArmPnp(Context1);
#endif
    return Status;
}
