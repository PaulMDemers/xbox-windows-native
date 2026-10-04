/* Experimental NT5 video PnP checkpoint. GPL-2.0-or-later.
 * Default-off, RAM-only instrumentation of this driver's own callbacks.
 * Stops BEFORE forwarding START_DEVICE. Never changes PCI configuration. */
#include <ntddk.h>

static PDRIVER_ADD_DEVICE OriginalAddDevice;
static PDRIVER_DISPATCH OriginalPnp;

static NTSTATUS NTAPI
XwnVideoPnp(PDEVICE_OBJECT Device, PIRP Irp)
{
    PIO_STACK_LOCATION Stack = IoGetCurrentIrpStackLocation(Irp);
    UCHAR Minor = Stack->MinorFunction;
    if (Minor == IRP_MN_START_DEVICE)
    {
        PCM_RESOURCE_LIST Raw = Stack->Parameters.StartDevice.AllocatedResources;
        PCM_RESOURCE_LIST Translated = Stack->Parameters.StartDevice.AllocatedResourcesTranslated;
        KeBugCheckEx(0xE0580001, 9, Raw ? Raw->Count : 0,
                     Translated ? Translated->Count : 0, 0x53545254);
    }
    /* Optional PnP queries may legitimately fail. Preserve their responses.
     * Do not access Irp after the original dispatch may have completed it. */
    return OriginalPnp(Device, Irp);
}

static NTSTATUS NTAPI
XwnVideoAddDevice(PDRIVER_OBJECT Driver, PDEVICE_OBJECT PhysicalDevice)
{
    NTSTATUS Status = OriginalAddDevice(Driver, PhysicalDevice);
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
    OriginalAddDevice = Driver->DriverExtension ? Driver->DriverExtension->AddDevice : NULL;
    OriginalPnp = Driver->MajorFunction[IRP_MJ_PNP];
    if (!OriginalAddDevice || !OriginalPnp)
        KeBugCheckEx(0xE0580001, 11, (ULONG_PTR)OriginalAddDevice,
                     (ULONG_PTR)OriginalPnp, 0);
    Driver->DriverExtension->AddDevice = XwnVideoAddDevice;
    Driver->MajorFunction[IRP_MJ_PNP] = XwnVideoPnp;
}
