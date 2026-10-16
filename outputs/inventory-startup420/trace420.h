/* SPDX-License-Identifier: MIT
 * Diagnostic only: native E create-only trace, flushed around original calls.
 * No kernel call is claimed cancellable. A missing after-record bounds a call
 * or the following trace write; it does not alone identify the hang producer.
 */
static HANDLE trace420;
static ULONG sequence420;
static int error420;

static void mark420(ULONG stage, ULONG phase, ULONG arg, ULONG result)
{
    if (!trace420 || error420) return;
    if (sequence420 >= 2048) { error420 = 1; return; }
    ULONG record[8] = {0x58573420, sequence420++, stage, phase, arg, result, 0, 0};
    for (unsigned i = 0; i < 7; ++i) record[7] ^= record[i];
    IO_STATUS_BLOCK io = {0};
    NTSTATUS status = NtWriteFile(trace420, NULL, NULL, NULL, &io, record, sizeof(record), NULL);
    if (!NT_SUCCESS(status) || io.Information != sizeof(record)) { error420 = 1; return; }
    if (!NT_SUCCESS(NtFlushBuffersFile(trace420, &io))) error420 = 1;
}

static int begin420(void)
{
    ANSI_STRING name; OBJECT_ATTRIBUTES attrs; IO_STATUS_BLOCK io = {0};
    RtlInitAnsiString(&name, "\\Device\\Harddisk0\\Partition1\\xwn-trace420.bin");
    InitializeObjectAttributes(&attrs, &name, OBJ_CASE_INSENSITIVE, NULL, NULL);
    NTSTATUS status = NtCreateFile(&trace420, GENERIC_WRITE | SYNCHRONIZE, &attrs, &io,
        NULL, FILE_ATTRIBUTE_NORMAL, 0, FILE_CREATE,
        FILE_NON_DIRECTORY_FILE | FILE_SYNCHRONOUS_IO_NONALERT);
    if (!NT_SUCCESS(status)) { trace420 = NULL; return 0; }
    mark420(0, 1, 0, 0);
    return !error420;
}

static BOOLEAN modes420(VIDEO_MODE *mode, int bits, int refresh, void **context)
{
    mark420(7, 0, 0, 0);
    BOOLEAN result = XVideoListModes(mode, bits, refresh, context);
    mark420(7, 1, result ? (ULONG)mode->height : 0, result);
    return result;
}

static BOOL video420(int width, int height, int bits, int refresh)
{
    mark420(31, 0, (ULONG)height, 0);
    BOOL result = XVideoSetMode(width, height, bits, refresh);
    mark420(31, 1, (ULONG)height, (ULONG)result);
    return result;
}

#define XVideoListModes modes420
#define XVideoSetMode video420
