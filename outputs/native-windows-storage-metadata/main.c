/* SPDX-License-Identifier: MIT
 * Xbox-kernel storage metadata. Read-only device handles read three sectors;
 * the sole file write is this application's report. No ATA passthrough.
 */
#include <hal/debug.h>
#include <hal/video.h>
#include <hal/xbox.h>
#include <windows.h>
#include <xboxkrnl/xboxkrnl.h>
#include <stdio.h>
#include <stdarg.h>
#include <string.h>
#include "xboxpart.h"

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

static int read_sector(HANDLE disk, unsigned long long offset,
                       unsigned long long disk_bytes, void *buffer)
{
    IO_STATUS_BLOCK io={0}; LARGE_INTEGER position; NTSTATUS s;
    if (offset % 512 || disk_bytes < 512 || offset > disk_bytes - 512) return 0;
    report("BEGIN read offset=%llu bytes=512\r\n", offset);
    if (!checkpoint()) return 0;
    position.QuadPart = offset;
    s=NtReadFile(disk,NULL,NULL,NULL,&io,buffer,512,&position);
    if (s==STATUS_PENDING) {
        s=NtWaitForSingleObject(disk,FALSE,NULL);
        if (NT_SUCCESS(s)) s=io.Status;
    }
    report("END read status=%08lx returned=%lu\r\n",(unsigned long)s,io.Information);
    checkpoint();
    return NT_SUCCESS(s) && io.Information==512;
}

static int inventory(void)
{
    HANDLE disk=NULL, volume=NULL; PARTITION_INFORMATION d={0}, f={0};
    unsigned char *buffer=NULL; ULONG returned=0; NTSTATUS s; int ok=0,table;
    XWN_XBOX_PARTITION parts[14]; unsigned int count=0,i;
    s=open_query("\\Device\\Harddisk0\\Partition0",&disk,0);
    report("disk_open=%08lx\r\n",(unsigned long)s);
    if (!NT_SUCCESS(s)) goto done;
    s=query_device(disk,IOCTL_DISK_GET_PARTITION_INFO,&d,sizeof(d),&returned);
    if (!NT_SUCCESS(s) || returned<sizeof(d) || d.StartingOffset.QuadPart!=0 ||
        d.PartitionLength.QuadPart<512 || (d.PartitionLength.QuadPart&511)) goto done;
    s=open_query("\\Device\\Harddisk0\\Partition6",&volume,0);
    report("f_open=%08lx\r\n",(unsigned long)s);
    if (!NT_SUCCESS(s)) goto done;
    s=query_device(volume,IOCTL_DISK_GET_PARTITION_INFO,&f,sizeof(f),&returned);
    if (!NT_SUCCESS(s) || returned<sizeof(f) || f.StartingOffset.QuadPart<512 ||
        f.PartitionLength.QuadPart<512 || (f.StartingOffset.QuadPart&511) ||
        f.StartingOffset.QuadPart>d.PartitionLength.QuadPart ||
        f.PartitionLength.QuadPart>d.PartitionLength.QuadPart-f.StartingOffset.QuadPart) goto done;
    report("disk_bytes=%llu f_start=%llu f_bytes=%llu\r\n",
        (unsigned long long)d.PartitionLength.QuadPart,
        (unsigned long long)f.StartingOffset.QuadPart,
        (unsigned long long)f.PartitionLength.QuadPart);
    buffer=MmAllocateContiguousMemory(4096);
    if (!buffer) goto done;
    debugPrint("Reading partition metadata (3 sectors)...\n");
    if (!read_sector(disk,0,d.PartitionLength.QuadPart,buffer)) goto done;
    report("mbr_signature_present=%u\r\n",buffer[510]==0x55 && buffer[511]==0xaa);
    table=XwnXboxParsePartitionTable(buffer,512,d.PartitionLength.QuadPart/512,parts,&count);
    report("partinfo_status=%d count=%u\r\n",table,count);
    /* Print bounded raw entry numbers, never sector contents or partition names. */
    if (memcmp(buffer,"****PARTINFO****",16)==0)
        for(i=0;i<14;i++) {
            const unsigned char *entry=buffer+48+i*32;
            report("table_slot=%u flags=%08x start_lba=%u sectors=%u reserved=%08x\r\n",
                i+1,XwnXboxReadU32(entry+16),XwnXboxReadU32(entry+20),
                XwnXboxReadU32(entry+24),XwnXboxReadU32(entry+28));
        }
    if (!read_sector(disk,1536,d.PartitionLength.QuadPart,buffer)) goto done;
    report("brfr_signature_present=%u\r\n",memcmp(buffer,"BRFR",4)==0);
    if (!read_sector(disk,f.StartingOffset.QuadPart,d.PartitionLength.QuadPart,buffer)) goto done;
    report("f_fatx_signature_present=%u sectors_per_cluster=%u root_cluster=%u\r\n",
        memcmp(buffer,"FATX",4)==0,XwnXboxReadU32(buffer+8),XwnXboxReadU32(buffer+12));
    ok=1;
done:
    if(buffer) MmFreeContiguousMemory(buffer);
    if(volume) NtClose(volume);
    if(disk) NtClose(disk);
    return ok;
}

int main(void)
{
    XVideoSetMode(640, 480, 32, REFRESH_DEFAULT);
    debugPrint("XWN storage metadata\nRead-only partition metadata probe\n\n");
    logfile = CreateFileA("D:\\xwn-storage-metadata.txt", GENERIC_WRITE, FILE_SHARE_READ,
                         NULL, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
    if (logfile == INVALID_HANDLE_VALUE) {
        debugPrint("Report cannot be opened; no inventory performed.\n");
    } else {
        report("XWN storage metadata v1\r\nKernel=%u.%u.%u.%u\r\n",
            XboxKrnlVersion.Major, XboxKrnlVersion.Minor,
            XboxKrnlVersion.Build, XboxKrnlVersion.Qfe);
        report("Reads only sector 0, sector 3 and the queried F header. No disk writes, ATA or EEPROM requests.\r\n");
        int complete = checkpoint() && inventory();
        report("METADATA_COMPLETE success=%d log_ok=%d\r\n", complete, log_ok);
        checkpoint(); CloseHandle(logfile); logfile = INVALID_HANDLE_VALUE;
        debugPrint(log_ok && complete ? "\nReport saved beside this app: xwn-storage-metadata.txt\n" : "\nReport write failed.\n");
    }
    debugPrint("\nRebooting in 15 seconds.\nWindows was not started; no partition changes.\n");
    Sleep(15000); XReboot();
    for (;;) Sleep(1000);
}
