"""Use legacy whole-disk partition information if NT5 lacks GET_LENGTH_INFO."""
from pathlib import Path
p=Path('/home/paul/xbox-windows-native/sources/reactos-extended/hal/halx86/xbox/part_xbox.c');s=p.read_text()
needle='    XwnExtendedPartitionTrace[2] = 40;'
assert s.count(needle)==1
s=s.replace(needle,'''    /* Windows 2000 may return STATUS_NOT_IMPLEMENTED for GET_LENGTH_INFO.
     * Query Partition0's native length, never a CHS estimate or table end. */
    if (Status == STATUS_NOT_IMPLEMENTED || Status == STATUS_INVALID_DEVICE_REQUEST ||
        Status == STATUS_NOT_SUPPORTED)
    {
        PARTITION_INFORMATION WholeDisk;
        XwnExtendedPartitionTrace[11] = 1;
        RtlZeroMemory(&WholeDisk, sizeof(WholeDisk));
        RtlZeroMemory(&Io, sizeof(Io));
        KeInitializeEvent(&Event, NotificationEvent, FALSE);
        Irp = IoBuildDeviceIoControlRequest(IOCTL_DISK_GET_PARTITION_INFO, Device,
                NULL, 0, &WholeDisk, sizeof(WholeDisk), FALSE, &Event, &Io);
        if (!Irp) { Status = STATUS_INSUFFICIENT_RESOURCES; goto Done; }
        Status = IoCallDriver(Device, Irp);
        if (Status == STATUS_PENDING)
        {
            KeWaitForSingleObject(&Event, Executive, KernelMode, FALSE, NULL);
            Status = Io.Status;
        }
        XwnExtendedPartitionTrace[12] = Status;
        XwnExtendedPartitionTrace[13] = WholeDisk.StartingOffset.LowPart;
        XwnExtendedPartitionTrace[14] = WholeDisk.PartitionLength.LowPart;
        XwnExtendedPartitionTrace[15] = WholeDisk.PartitionLength.HighPart;
        if (!NT_SUCCESS(Status)) goto Done;
        if (Io.Information < sizeof(WholeDisk) || WholeDisk.PartitionNumber != 0 ||
            WholeDisk.StartingOffset.QuadPart != 0)
        { Status = STATUS_DISK_CORRUPT_ERROR; goto Done; }
        Length.Length = WholeDisk.PartitionLength;
        Io.Information = sizeof(Length);
    }
'''+needle,1);p.write_text(s)
