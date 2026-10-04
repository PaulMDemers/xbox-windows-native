/* SPDX-License-Identifier: MIT
 * Xbox-kernel storage inventory. Query-only device handles; the sole file
 * write is this application's report. No ATA passthrough or raw-sector I/O.
 */
#include <hal/debug.h>
#include <hal/video.h>
#include <hal/xbox.h>
#include <windows.h>
#include <xboxkrnl/xboxkrnl.h>
#include <stdio.h>
#include <stdarg.h>

static HANDLE logfile = INVALID_HANDLE_VALUE;
static int log_ok = 1;

static void report(const char *fmt, ...)
{
    char text[512]; DWORD written = 0; va_list args;
    va_start(args, fmt);
    int n = vsnprintf(text, sizeof(text), fmt, args);
    va_end(args);
    if (n < 0 || n >= (int)sizeof(text)) { log_ok = 0; return; }
    if (!WriteFile(logfile, text, n, &written, NULL) || written != (DWORD)n)
        log_ok = 0;
    OutputDebugStringA(text);
}

static int checkpoint(void)
{
    IO_STATUS_BLOCK io;
    if (!NT_SUCCESS(NtFlushBuffersFile(logfile, &io))) log_ok = 0;
    return log_ok;
}

static NTSTATUS open_query(const char *path, HANDLE *handle, int directory)
{
    ANSI_STRING name; OBJECT_ATTRIBUTES attrs; IO_STATUS_BLOCK io;
    RtlInitAnsiString(&name, path);
    InitializeObjectAttributes(&attrs, &name, OBJ_CASE_INSENSITIVE, NULL, NULL);
    return NtOpenFile(handle, GENERIC_READ | SYNCHRONIZE, &attrs, &io,
        FILE_SHARE_READ | FILE_SHARE_WRITE,
        FILE_SYNCHRONOUS_IO_NONALERT | (directory ? FILE_DIRECTORY_FILE : 0));
}

static NTSTATUS query_device(HANDLE handle, ULONG code, void *out, ULONG length,
                             ULONG *returned)
{
    IO_STATUS_BLOCK io = {0};
    NTSTATUS s = NtDeviceIoControlFile(handle, NULL, NULL, NULL, &io,
                                     code, NULL, 0, out, length);
    if (s == STATUS_PENDING) {
        s = NtWaitForSingleObject(handle, FALSE, NULL);
        if (NT_SUCCESS(s)) s = io.Status;
    }
    *returned = io.Information;
    return s;
}

static void inventory(void)
{
    HANDLE handle; char path[80]; ULONG returned;
    for (unsigned p = 0; p <= 7; ++p) {
        snprintf(path, sizeof(path), "\\Device\\Harddisk0\\Partition%u", p);
        report("BEGIN partition=%u path=%s\r\n", p, path);
        if (!checkpoint()) return;
        debugPrint("Query partition %u\n", p);
        NTSTATUS s = open_query(path, &handle, 0);
        report("open_status=%08lx\r\n", (unsigned long)s);
        if (NT_SUCCESS(s)) {
            if (p == 0) {
                DISK_GEOMETRY g = {0};
                s = query_device(handle, IOCTL_DISK_GET_DRIVE_GEOMETRY,
                                 &g, sizeof(g), &returned);
                report("geometry_status=%08lx returned=%lu\r\n", (unsigned long)s, returned);
                if (NT_SUCCESS(s) && returned >= sizeof(g))
                    report("geometry cylinders=%llu heads=%lu sectors_per_track=%lu bytes_per_sector=%lu\r\n",
                        (unsigned long long)g.Cylinders.QuadPart, g.TracksPerCylinder,
                        g.SectorsPerTrack, g.BytesPerSector);
            }
            PARTITION_INFORMATION info = {0};
            s = query_device(handle, IOCTL_DISK_GET_PARTITION_INFO,
                             &info, sizeof(info), &returned);
            report("partition_status=%08lx returned=%lu\r\n", (unsigned long)s, returned);
            if (NT_SUCCESS(s) && returned >= sizeof(info))
                report("partition=%u start_bytes=%llu length_bytes=%llu number=%lu type=%02x\r\n",
                    p, (unsigned long long)info.StartingOffset.QuadPart,
                    (unsigned long long)info.PartitionLength.QuadPart,
                    info.PartitionNumber, info.PartitionType);
            NtClose(handle);
        }
        /* Mount/query only the existing volume root; never create or format. */
        if (p != 0) {
            snprintf(path, sizeof(path), "\\Device\\Harddisk0\\Partition%u\\", p);
            s = open_query(path, &handle, 1);
            report("root_open_status=%08lx\r\n", (unsigned long)s);
            if (NT_SUCCESS(s)) {
                FILE_FS_SIZE_INFORMATION size = {0}; IO_STATUS_BLOCK io = {0};
                s = NtQueryVolumeInformationFile(handle, &io, &size, sizeof(size), FileFsSizeInformation);
                report("size_status=%08lx returned=%lu\r\n", (unsigned long)s, io.Information);
                if (NT_SUCCESS(s) && io.Information >= sizeof(size))
                    report("volume=%u total_units=%llu free_units=%llu sectors_per_unit=%lu bytes_per_sector=%lu\r\n",
                        p, (unsigned long long)size.TotalAllocationUnits.QuadPart,
                        (unsigned long long)size.AvailableAllocationUnits.QuadPart,
                        size.SectorsPerAllocationUnit, size.BytesPerSector);
                NtClose(handle);
            }
        }
        report("END partition=%u\r\n", p);
        if (!checkpoint()) return;
    }
}

int main(void)
{
    XVideoSetMode(640, 480, 32, REFRESH_DEFAULT);
    debugPrint("XWN storage inventory\nQuery-only disk and volume handles\n\n");
    logfile = CreateFileA("D:\\xwn-storage.txt", GENERIC_WRITE, FILE_SHARE_READ,
                         NULL, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
    if (logfile == INVALID_HANDLE_VALUE) {
        debugPrint("Report cannot be opened; no inventory performed.\n");
    } else {
        report("XWN storage inventory v1\r\nKernel=%u.%u.%u.%u\r\n",
            XboxKrnlVersion.Major, XboxKrnlVersion.Minor,
            XboxKrnlVersion.Build, XboxKrnlVersion.Qfe);
        report("Only disk/partition geometry and volume space queries. No raw-sector read/write, ATA or EEPROM requests.\r\n");
        if (checkpoint()) inventory();
        report("INVENTORY_COMPLETE log_ok=%d\r\n", log_ok);
        checkpoint(); CloseHandle(logfile); logfile = INVALID_HANDLE_VALUE;
        debugPrint(log_ok ? "\nReport saved beside this app: xwn-storage.txt\n" : "\nReport write failed.\n");
    }
    debugPrint("\nRebooting in 15 seconds.\nWindows was not started; no partition changes.\n");
    Sleep(15000); XReboot();
    for (;;) Sleep(1000);
}
