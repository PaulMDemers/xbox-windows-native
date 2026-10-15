/* GPL-2.0-or-later. Opt-in trace to an existing, explicitly seeded 4096-byte file.
 * No creation, resizing, path selection, PCI writes, or disk-sector access. */
#include <ntddk.h>


static HANDLE TraceHandle;
static ULONG TraceData[1024];
static volatile LONG TraceBusy;
static const CHAR Magic[16] = "XWN-VID-TRACE01\n";

static VOID TraceFail(ULONG Phase, NTSTATUS Status, ULONG_PTR Bytes)
{
    KeBugCheckEx(0xE0580001, 13, Phase, (ULONG_PTR)Status, Bytes);
}

VOID NTAPI XwnVideoTraceInit(VOID)
{
    UNICODE_STRING Name;
    OBJECT_ATTRIBUTES Attributes;
    IO_STATUS_BLOCK Io;
    FILE_STANDARD_INFORMATION Info;
    LARGE_INTEGER Offset;
    NTSTATUS Status;
    ULONG I;
    if (KeGetCurrentIrql() != PASSIVE_LEVEL)
        TraceFail(0, STATUS_INVALID_DEVICE_STATE, KeGetCurrentIrql());
    RtlInitUnicodeString(&Name, L"\\SystemRoot\\System32\\xwn-video-trace.bin");
    InitializeObjectAttributes(&Attributes, &Name,
                               OBJ_CASE_INSENSITIVE | OBJ_KERNEL_HANDLE, NULL, NULL);
    Status = ZwCreateFile(&TraceHandle, FILE_READ_DATA | FILE_WRITE_DATA | SYNCHRONIZE,
                          &Attributes, &Io, NULL, 0, FILE_SHARE_READ, FILE_OPEN,
                          FILE_NON_DIRECTORY_FILE | FILE_SYNCHRONOUS_IO_NONALERT |
                          FILE_WRITE_THROUGH, NULL, 0);
    if (!NT_SUCCESS(Status)) TraceFail(1, Status, 0);
    Status = ZwQueryInformationFile(TraceHandle, &Io, &Info, sizeof(Info), FileStandardInformation);
    if (!NT_SUCCESS(Status) || Info.EndOfFile.QuadPart != sizeof(TraceData))
        TraceFail(2, Status, NT_SUCCESS(Status) ? Info.EndOfFile.LowPart : 0);
    Offset.QuadPart = 0;
    Io.Information = 0;
    Status = ZwReadFile(TraceHandle, NULL, NULL, NULL, &Io,
                        TraceData, sizeof(TraceData), &Offset, NULL);
    if (!NT_SUCCESS(Status) || Io.Information != sizeof(TraceData))
        TraceFail(3, Status, Io.Information);
    for (I = 0; I < sizeof(Magic); ++I)
        if (((PUCHAR)TraceData)[I] != (UCHAR)Magic[I]) TraceFail(4, STATUS_DATA_ERROR, I);
    for (I = sizeof(Magic); I < sizeof(TraceData); ++I)
        if (((PUCHAR)TraceData)[I]) TraceFail(4, STATUS_DATA_ERROR, I);
}

VOID NTAPI XwnVideoTrace(ULONG Event, ULONG A, ULONG B, ULONG C)
{
    LARGE_INTEGER Offset;
    IO_STATUS_BLOCK Io;
    NTSTATUS Status;
    ULONG Index;
    if (!TraceHandle) return;
    if (KeGetCurrentIrql() != PASSIVE_LEVEL ||
        InterlockedCompareExchange(&TraceBusy, 1, 0) != 0)
    {
        InterlockedIncrement((PLONG)&TraceData[5]);
        return;
    }
    if (TraceData[4] >= 254) { InterlockedExchange(&TraceBusy, 0); return; }
    Index = 8 + TraceData[4] * 4;
    TraceData[Index] = Event; TraceData[Index + 1] = A;
    TraceData[Index + 2] = B; TraceData[Index + 3] = C;
    ++TraceData[4];
    Offset.QuadPart = 0;
    Io.Information = 0;
    Status = ZwWriteFile(TraceHandle, NULL, NULL, NULL, &Io,
                         TraceData, sizeof(TraceData), &Offset, NULL);
    if (!NT_SUCCESS(Status) || Io.Information != sizeof(TraceData))
        TraceFail(5, Status, Io.Information);
    InterlockedExchange(&TraceBusy, 0);
}

VOID NTAPI XwnVideoTraceClose(VOID)
{
    if (TraceHandle) { ZwClose(TraceHandle); TraceHandle = NULL; }
}


VOID NTAPI XwnVideoTracePci(VOID)
{
    ULONG Bridge[16], Gpu[16], I, BridgeBytes, GpuBytes;
    RtlFillMemory(Bridge, sizeof(Bridge), 0xff);
    RtlFillMemory(Gpu, sizeof(Gpu), 0xff);
    /* Xbox AGP bridge 00:1e.0 and GPU 01:00.0; config reads only. */
    BridgeBytes = HalGetBusDataByOffset(PCIConfiguration, 0, 30, Bridge, 0, sizeof(Bridge));
    GpuBytes = HalGetBusDataByOffset(PCIConfiguration, 1, 0, Gpu, 0, sizeof(Gpu));
    XwnVideoTrace(8, BridgeBytes, GpuBytes, 0);
    for (I = 0; I < 16; ++I)
        XwnVideoTrace(9, I * 4, Bridge[I], Gpu[I]);
}
