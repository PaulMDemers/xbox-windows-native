/* SPDX-License-Identifier: MIT
 * Read-only timer and SMBus-status observation. No encoder or display changes.
 * Kernel file/sleep/restart services are not application time-bounded.
 */
#include <windows.h>
#include <xboxkrnl/xboxkrnl.h>
#include <nxdk/mount.h>
#include <stdarg.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "sample.h"

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
        snprintf(path, size, "E:\\xwn-clock684-%02u.json", i);
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


uint32_t raw_pm(void *unused);
uint16_t raw_smbus_status(void);
uint64_t raw_tsc(void *unused);
static uint64_t qpc(void *unused) { (void)unused; return KeQueryPerformanceCounter(); }
static uint64_t irq(void *unused) { (void)unused; return KeQueryInterruptTime(); }
static void sleep_ms(void *unused,unsigned ms) { (void)unused; Sleep(ms); }
static struct sample fast[SAMPLE_COUNT], slow[SAMPLE_COUNT];
static int checkpoint(const char *phase, int complete)
{
    char path[64]; size_t saved_used=used;
    append("  \"phase\":\"%s\",\"complete\":%s\n}\n",phase,complete?"true":"false");
    int rc=overflow?6:save_report(path,sizeof(path)); used=saved_used;
    return rc;
}
static void samples(const char *name, struct sample *s)
{
    append("  \"%s\":[",name);
    for(unsigned i=0;i<SAMPLE_COUNT;++i)
        append("%s[%lu,%llu,%llu,%llu,%lu]",i?",":"",
            (unsigned long)s[i].pm_before,(unsigned long long)s[i].qpc,
            (unsigned long long)s[i].irq,(unsigned long long)s[i].tsc,
            (unsigned long)s[i].pm_after);
    append("],\n");
}
int main(void)
{
    /* Status is an observation only. Kernel may own pending transactions;
     * never acknowledge, reset, or submit a command in this utility. */
    unsigned entry=raw_smbus_status();
    if(!prepare_e()) { HalReturnToFirmware(HalRebootRoutine); return 1; }
    append("{\n  \"schema\":1,\"tool\":\"xwn-video-clock684\",\n");
    append("  \"kernel\":[%u,%u,%u,%u],\"gpu_revision\":%u,\"mcp_revision\":%u,\n",
        XboxKrnlVersion.Major,XboxKrnlVersion.Minor,XboxKrnlVersion.Build,
        XboxKrnlVersion.Qfe,XboxHardwareInfo.GpuRevision,XboxHardwareInfo.McpRevision);
    append("  \"smbus_entry\":%u,\"qpc_frequency\":%llu,\n",entry,
        (unsigned long long)KeQueryPerformanceFrequency());
    append("  \"columns\":[\"pm_before\",\"qpc\",\"interrupt_100ns\",\"rdtsc\",\"pm_after\"],\n");
    if(checkpoint("before_samples",0)) { HalReturnToFirmware(HalRebootRoutine); return 2; }
    struct reader r={NULL,raw_pm,qpc,irq,raw_tsc,sleep_ms};
    int ok=acquire(&r,fast,0) && acquire(&r,slow,100);
    unsigned end=raw_smbus_status();
    samples("burst",fast); samples("spaced_100ms",slow);
    append("  \"acquisition_return\":%s,\"smbus_end\":%u,\n",ok?"true":"false",end);
    checkpoint("restart_requested",ok);
    HalReturnToFirmware(HalRebootRoutine); return 0;
}
