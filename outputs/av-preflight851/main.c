/* SPDX-License-Identifier: MIT
 * Kernel-owned framebuffer and read-only configuration reference. No native handoff.
 * Kernel display calls are not bounded by this application. Watched test only.
 */
#include <hal/debug.h>
#include <hal/video.h>
#include <windows.h>
#include <xboxkrnl/xboxkrnl.h>
#include <nxdk/mount.h>
#include <stdarg.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>


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
        snprintf(path, size, "E:\\xwn-av851-%02u.json", i);
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



int main(void)
{
    if (!prepare_e()) { HalReturnToFirmware(HalRebootRoutine); return 1; }
    DWORD settings = XVideoGetEncoderSettings();
    MM_STATISTICS memory = {0}; memory.Length = sizeof(memory);
    LONG ms = MmQueryStatistics(&memory);
    ULONG cable=0xdeadbeef, flags=0xdeadbeef, encoder=0xdeadbeef;
    LONG cs=HalReadSMBusValue(0x20,4,FALSE,&cable);
    LONG fs=HalReadSMBusValue(0xa8,0x96,FALSE,&flags);
    LONG es=HalReadSMBusValue(0x8a,0,FALSE,&encoder);
    int memory_ok=ms==0 && memory.TotalPhysicalPages==16384;
    int pack_ok=(settings&VIDEO_ADAPTER_MASK)==AV_PACK_HDTV;
    int sdk_480=(settings&VIDEO_MODE_480P)!=0;
    int raw_480=fs==0 && (flags&8)!=0;
    append("{\n  \"schema\":1,\"tool\":\"xwn-av851\",\"phase\":\"kernel_preflight\",\n");
    append("  \"kernel\":[%u,%u,%u,%u],\"gpu_revision\":%u,\"mcp_revision\":%u,\n", XboxKrnlVersion.Major,XboxKrnlVersion.Minor,XboxKrnlVersion.Build,XboxKrnlVersion.Qfe,XboxHardwareInfo.GpuRevision,XboxHardwareInfo.McpRevision);
    append("  \"settings\":%lu,\"memory_status\":%ld,\"physical_pages\":%lu,\n",(unsigned long)settings,(long)ms,(unsigned long)memory.TotalPhysicalPages);
    append("  \"smc_cable_status\":%ld,\"smc_cable_value\":%lu,\"eeprom_video_status\":%ld,\"eeprom_video_byte96\":%lu,\"encoder_response_status\":%ld,\"encoder_response_byte\":%lu,\n",(long)cs,(unsigned long)cable,(long)fs,(unsigned long)flags,(long)es,(unsigned long)encoder);
    append("  \"memory_64m\":%s,\"kernel_hdtv_pack\":%s,\"kernel_480p_enabled\":%s,\"raw_480p_bit\":%s,\"encoder_responded\":%s,\n",memory_ok?"true":"false",pack_ok?"true":"false",sdk_480?"true":"false",raw_480?"true":"false",es==0?"true":"false");
    append("  \"limits\":\"Kernel reference only; encoder response does not identify chip; no native dispatch or guard observed.\",\"complete\":true\n}\n");
    char path[64]; int result=overflow?6:save_report(path,sizeof(path));
    HalReturnToFirmware(HalRebootRoutine); return result;
}
