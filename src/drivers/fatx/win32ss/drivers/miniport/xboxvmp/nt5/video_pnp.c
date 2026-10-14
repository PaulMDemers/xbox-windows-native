/* Experimental NT5 video PnP checkpoint. GPL-2.0-or-later.
 * Default-off, RAM-only instrumentation of this driver's own callbacks.
 * Stops BEFORE forwarding START_DEVICE. Never changes PCI configuration. */
#include <ntddk.h>
#ifdef XBOX_NT5_VIDEO_DIRECT_MAP
VOID NTAPI XwnDirectInitialize(VOID);
VOID NTAPI XwnDirectClose(VOID);
#endif

static PDRIVER_ADD_DEVICE OriginalAddDevice;
static PDRIVER_DISPATCH OriginalPnp;
#ifdef XBOX_NT5_VIDEO_TRACE
VOID NTAPI XwnVideoTraceInit(VOID);
VOID NTAPI XwnVideoTrace(ULONG, ULONG, ULONG, ULONG);
VOID NTAPI XwnVideoTraceClose(VOID);
VOID NTAPI XwnVideoTracePci(VOID);
static PDRIVER_UNLOAD OriginalUnload;
static VOID NTAPI XwnVideoUnload(PDRIVER_OBJECT Driver)
{
    XwnVideoTrace(6, 0, 0, 0);
    XwnVideoTraceClose();
    if (OriginalUnload) OriginalUnload(Driver);
#ifdef XBOX_NT5_VIDEO_DIRECT_MAP
    XwnDirectClose();
#endif
}
#define TRACE(e,a,b,c) XwnVideoTrace(e,(ULONG)(a),(ULONG)(b),(ULONG)(c))
#else
#define TRACE(e,a,b,c) ((void)0)
#endif

static NTSTATUS NTAPI
XwnVideoPnp(PDEVICE_OBJECT Device, PIRP Irp)
{
    PIO_STACK_LOCATION Stack = IoGetCurrentIrpStackLocation(Irp);
    UCHAR Minor = Stack->MinorFunction;
    NTSTATUS Status;
    TRACE(4, Minor, Device, 0);
    if (Minor == IRP_MN_START_DEVICE)
    {
        PCM_RESOURCE_LIST Raw = Stack->Parameters.StartDevice.AllocatedResources;
        PCM_RESOURCE_LIST Translated = Stack->Parameters.StartDevice.AllocatedResourcesTranslated;
#ifdef XBOX_NT5_VIDEO_TRACE
        TRACE(7, Raw ? Raw->Count : 0, Translated ? Translated->Count : 0, 0);
#else
        KeBugCheckEx(0xE0580001, 9, Raw ? Raw->Count : 0,
                     Translated ? Translated->Count : 0, 0x53545254);
#endif
    }
    /* Optional PnP queries may legitimately fail. Preserve their responses.
     * Do not access Irp after the original dispatch may have completed it. */
    Status = OriginalPnp(Device, Irp);
    TRACE(5, Minor, Status, 0);
    return Status;
}

static NTSTATUS NTAPI
XwnVideoAddDevice(PDRIVER_OBJECT Driver, PDEVICE_OBJECT PhysicalDevice)
{
    NTSTATUS Status;
    TRACE(2, PhysicalDevice, 0, 0);
    Status = OriginalAddDevice(Driver, PhysicalDevice);
    TRACE(3, Status, PhysicalDevice, 0);
    if (!NT_SUCCESS(Status))
        KeBugCheckEx(0xE0580001, 10, (ULONG_PTR)Status,
                     (ULONG_PTR)PhysicalDevice, 0);
    /* VideoPort may install its dispatch while creating the device. */
    if (Driver->MajorFunction[IRP_MJ_PNP] != XwnVideoPnp)
    {
        OriginalPnp = Driver->MajorFunction[IRP_MJ_PNP];
        if (!OriginalPnp)
            KeBugCheckEx(0xE0580001, 11, 0, 0, 1);
        Driver->MajorFunction[IRP_MJ_PNP] = XwnVideoPnp;
    }
    return Status;
}

VOID NTAPI XwnVideoArmPnp(PDRIVER_OBJECT Driver)
{
#ifdef XBOX_NT5_VIDEO_TRACE
#ifdef XBOX_NT5_VIDEO_DIRECT_MAP
    XwnDirectInitialize();
#endif
    XwnVideoTraceInit();
    OriginalUnload = Driver->DriverUnload;
    Driver->DriverUnload = XwnVideoUnload;
#endif
    OriginalAddDevice = Driver->DriverExtension ? Driver->DriverExtension->AddDevice : NULL;
    OriginalPnp = Driver->MajorFunction[IRP_MJ_PNP];
    TRACE(1, OriginalAddDevice, OriginalPnp, 0);
#ifdef XBOX_NT5_VIDEO_TRACE
    XwnVideoTracePci();
#endif
    if (!OriginalAddDevice || !OriginalPnp)
        KeBugCheckEx(0xE0580001, 11, (ULONG_PTR)OriginalAddDevice,
                     (ULONG_PTR)OriginalPnp, 0);
    Driver->DriverExtension->AddDevice = XwnVideoAddDevice;
    Driver->MajorFunction[IRP_MJ_PNP] = XwnVideoPnp;
}
