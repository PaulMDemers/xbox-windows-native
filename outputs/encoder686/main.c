/* SPDX-License-Identifier: MIT
 * Read-only kernel encoder-address observations. No encoder configuration writes.
 * Kernel file/sleep/restart services are not application time-bounded.
 */
#include <windows.h>
#include <xboxkrnl/xboxkrnl.h>
#include <nxdk/mount.h>
#include <stdarg.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <hal/video.h>
#include "probe.h"

static char report[32768], verify[32768];
static size_t used;
static int overflow;

/* DVD launches mount D only. Never replace an existing drive mapping: verify
 * the native target, and refuse any mapping other than standard dashboard E. */
static int prepare_e(void)
{
    const char *target = "\\Device\\Harddisk0\\Partition1";
    if (!nxIsDriveMounted('E') && !nxMountDrive('E', target)) return 0;
    ANSI_STRING name, value;
    OBJECT_ATTRIBUTES attributes;
    HANDLE handle;
    char buffer[128];
    RtlInitAnsiString(&name, "\\??\\E:");
    InitializeObjectAttributes(&attributes, &name, OBJ_CASE_INSENSITIVE, NULL, NULL);
    if (!NT_SUCCESS(NtOpenSymbolicLinkObject(&handle, &attributes))) return 0;
    value.Buffer = buffer; value.Length = 0; value.MaximumLength = sizeof(buffer);
    ULONG returned = 0;
    NTSTATUS status = NtQuerySymbolicLinkObject(handle, &value, &returned);
    NtClose(handle);
    return NT_SUCCESS(status) && value.Length == strlen(target) &&
           !memcmp(value.Buffer, target, value.Length);
}

static void append(const char *fmt, ...)
{
    if (overflow) return;
    va_list args;
    va_start(args, fmt);
    int n = vsnprintf(report + used, sizeof(report) - used, fmt, args);
    va_end(args);
    if (n < 0 || (size_t)n >= sizeof(report) - used) { overflow = 1; return; }
    used += (size_t)n;
}

static int save_report(char *path, size_t size)
{
    HANDLE file = INVALID_HANDLE_VALUE;
    for (unsigned i = 0; i < 100; ++i) {
        snprintf(path, size, "E:\\xwn-encoder686-%02u.json", i);
        file = CreateFileA(path, GENERIC_WRITE, 0, NULL, CREATE_NEW, FILE_ATTRIBUTE_NORMAL, NULL);
        if (file != INVALID_HANDLE_VALUE) break;
        if (GetLastError() != ERROR_FILE_EXISTS && GetLastError() != ERROR_ALREADY_EXISTS) return 1;
    }
    if (file == INVALID_HANDLE_VALUE) return 2;
    DWORD written = 0;
    IO_STATUS_BLOCK io;
    int ok = WriteFile(file, report, (DWORD)used, &written, NULL) && written == used;
    if ((LONG)NtFlushBuffersFile(file, &io) < 0) ok = 0;
    if (!CloseHandle(file)) ok = 0;
    if (!ok) return 3;
    file = CreateFileA(path, GENERIC_READ, FILE_SHARE_READ, NULL, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);
    if (file == INVALID_HANDLE_VALUE) return 4;
    DWORD got = 0;
    ok = ReadFile(file, verify, sizeof(verify), &got, NULL) && got == used && !memcmp(report, verify, used);
    if (!CloseHandle(file)) ok = 0;
    return ok ? 0 : 5;
}


uint16_t raw_smbus_status(void);
static int checkpoint(const char *phase,int complete)
{
    char path[64];size_t saved=used;
    append("  \"phase\":\"%s\",\"complete\":%s\n}\n",phase,complete?"true":"false");
    int rc=overflow?6:save_report(path,sizeof(path));used=saved;return rc;
}
int main(void)
{
    if(!prepare_e()) { HalReturnToFirmware(HalRebootRoutine);return 1; }
    DWORD settings=XVideoGetEncoderSettings();
    MM_STATISTICS memory={0};memory.Length=sizeof(memory);
    LONG memstatus=MmQueryStatistics(&memory);
    append("{\n  \"schema\":1,\"tool\":\"xwn-encoder686\",\n");
    append("  \"kernel\":[%u,%u,%u,%u],\"gpu_revision\":%u,\"mcp_revision\":%u,\n",
       XboxKrnlVersion.Major,XboxKrnlVersion.Minor,XboxKrnlVersion.Build,
       XboxKrnlVersion.Qfe,XboxHardwareInfo.GpuRevision,XboxHardwareInfo.McpRevision);
    append("  \"settings\":%lu,\"memory_status\":%lu,\"pages\":%lu,\n",
       (unsigned long)settings,(unsigned long)memstatus,(unsigned long)memory.TotalPhysicalPages);
    append("  \"qpc_frequency\":%llu,\"smbus_entry\":%u,\n",
       (unsigned long long)KeQueryPerformanceFrequency(),raw_smbus_status());
    if(checkpoint("before_reads",0)) { HalReturnToFirmware(HalRebootRoutine);return 2; }
    struct encoder_response results[3];
    const char *phases[]={"after_xcalibur","after_conexant","after_focus"};
    for(unsigned i=0;i<3;++i) {
        ULONG value=0xdeadbeef;
        ULONGLONG before=KeQueryPerformanceCounter();
        /* Kernel owns serialization. One API call per address, no application
         * retry, native port command, writes to encoder registers or fallback. */
        LONG status=HalReadSMBusValue(encoder_addresses[i],0,FALSE,&value);
        ULONGLONG after=KeQueryPerformanceCounter();
        results[i].status=status;results[i].value=value;
        append("  \"probe%u\":{\"address8\":%u,\"register\":0,\"read_word\":false,\"status\":%lu,\"value\":%lu,\"qpc_before\":%llu,\"qpc_after\":%llu,\"smbus_after\":%u},\n",
           i,encoder_addresses[i],(unsigned long)status,(unsigned long)value,
           (unsigned long long)before,(unsigned long long)after,raw_smbus_status());
        if(checkpoint(phases[i],0)) { HalReturnToFirmware(HalRebootRoutine);return 3; }
    }
    append("  \"label\":\"%s\",\"unique_chip_id_proved\":false,\n",response_label(results));
    checkpoint("restart_requested",1);
    HalReturnToFirmware(HalRebootRoutine);return 0;
}
