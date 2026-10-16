/* SPDX-License-Identifier: MIT
 * Original XWN tester inventory. No EEPROM, keys, serials, disk identification,
 * firmware dump, network traffic, registry or partition-table writes.
 * Kernel/PCI/encoder observations are reported, not motherboard revision guesses.
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

#include "trace420.h"

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
        snprintf(path, size, "E:\\xwn-report-%02u.json", i);
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
    if (!begin420()) return 2;
    mark420(1, 0, 0, 0);
    int e_ready = prepare_e();
    mark420(1, 1, 0, e_ready);
    MM_STATISTICS memory = {0};
    memory.Length = sizeof(memory);
    mark420(2, 0, 0, 0);
    LONG memory_status = MmQueryStatistics(&memory);
    mark420(2, 1, 0, (ULONG)memory_status);
    mark420(3, 0, 0, 0);
    DWORD settings = XVideoGetEncoderSettings();
    mark420(3, 1, 0, (ULONG)settings);
    /* Two read-only probes corresponding to Cromwell's 7-bit 0x45/0x6a
     * presence checks. Kernel API uses the shifted 8-bit SMBus address.
     * No fallback identification of Xcalibur from two failed reads. */
    ULONG conexant = 0, focus = 0;
    mark420(4, 0, 0, 0);
    LONG cx_status = HalReadSMBusValue(0x8a, 0, FALSE, &conexant);
    mark420(4, 1, 0, (ULONG)cx_status);
    mark420(5, 0, 0, 0);
    LONG fs_status = HalReadSMBusValue(0xd4, 0, FALSE, &focus);
    mark420(5, 1, 0, (ULONG)fs_status);
    const char *encoder = cx_status == 0 && fs_status != 0 ? "conexant-response" :
                          fs_status == 0 && cx_status != 0 ? "focus-response" : "unidentified";
    append("{\n  \"schema\":1,\n  \"tool\":\"xwn-hardware-report-1\",\n");
    append("  \"kernel\":[%u,%u,%u,%u],\n", XboxKrnlVersion.Major, XboxKrnlVersion.Minor,
           XboxKrnlVersion.Build, XboxKrnlVersion.Qfe);
    append("  \"hardware_flags\":%lu,\n  \"gpu_revision\":%u,\n  \"mcp_revision\":%u,\n",
           (unsigned long)XboxHardwareInfo.Flags, XboxHardwareInfo.GpuRevision, XboxHardwareInfo.McpRevision);
    append("  \"memory_status\":%lu,\n  \"kernel_total_pages\":%lu,\n  \"page_bytes\":4096,\n",
           (unsigned long)memory_status, (unsigned long)memory.TotalPhysicalPages);
    append("  \"video_settings\":%lu,\n  \"av_pack\":%lu,\n  \"video_standard\":%lu,\n",
           (unsigned long)settings, (unsigned long)(settings & VIDEO_ADAPTER_MASK),
           (unsigned long)(settings & VIDEO_STANDARD_MASK));
    append("  \"encoder_probe\":{\"label\":\"%s\",\"conexant_status\":%lu,\"conexant_value\":%lu,"
           "\"focus_status\":%lu,\"focus_value\":%lu},\n", encoder,
           (unsigned long)cx_status, (unsigned long)conexant, (unsigned long)fs_status, (unsigned long)focus);
    ULARGE_INTEGER free_bytes = {0}, total_bytes = {0};
    mark420(6, 0, 0, 0);
    BOOL space_ok = e_ready && GetDiskFreeSpaceExA("E:\\", &free_bytes, &total_bytes, NULL);
    mark420(6, 1, 0, (ULONG)space_ok);
    append("  \"e_space\":{\"ok\":%s,\"free_bytes\":%llu,\"total_bytes\":%llu},\n",
           space_ok ? "true" : "false", (unsigned long long)free_bytes.QuadPart,
           (unsigned long long)total_bytes.QuadPart);
    append("  \"available_32bit_modes\":[");
    VIDEO_MODE mode; void *context = NULL; unsigned modes = 0;
    while (modes < 128 && XVideoListModes(&mode, 32, 0, &context)) {
        append("%s[%d,%d,%d,%d]", modes ? "," : "", mode.width, mode.height, mode.bpp, mode.refresh);
        ++modes;
    }
    if (modes == 128) overflow = 1;
    append("],\n  \"pci\":[");
    unsigned devices = 0;
    for (unsigned bus = 0; bus < 2; ++bus) {
        for (unsigned device = 0; device < 32; ++device) {
            for (unsigned function = 0; function < 8; ++function) {
                ULONG id = 0xffffffff, klass = 0;
                ULONG slot = device | (function << 5);
                mark420(20, 0, (bus << 8) | slot, 0);
                HalReadWritePCISpace(bus, slot, 0, &id, sizeof(id), FALSE);
                mark420(20, 1, (bus << 8) | slot, id);
                if ((id & 0xffff) == 0xffff || (id & 0xffff) == 0) continue;
                mark420(21, 0, (bus << 8) | slot, 0);
                HalReadWritePCISpace(bus, slot, 8, &klass, sizeof(klass), FALSE);
                mark420(21, 1, (bus << 8) | slot, klass);
                append("%s{\"bus\":%u,\"device\":%u,\"function\":%u,\"id\":%lu,\"class_revision\":%lu}",
                       devices ? "," : "", bus, device, function, (unsigned long)id, (unsigned long)klass);
                ++devices;
            }
        }
    }
    append("],\n  \"complete\":true\n}\n");
    char path[64] = {0};
    mark420(30, 0, 0, 0);
    int saved = !e_ready ? 7 : overflow ? 6 : save_report(path, sizeof(path));
    mark420(30, 1, 0, (ULONG)saved);
    /* SD display for the inventory UI; never asks a new encoder to enter HD. */
    if (XVideoSetMode(640, 480, 32, REFRESH_DEFAULT)) {
        debugPrint("XWN hardware report 1\n\n");
        debugPrint("Kernel %u.%u.%u.%u   RAM pages %lu\n", XboxKrnlVersion.Major,
                   XboxKrnlVersion.Minor, XboxKrnlVersion.Build, XboxKrnlVersion.Qfe,
                   (unsigned long)memory.TotalPhysicalPages);
        debugPrint("Encoder probe: %s\n", encoder);
        debugPrint("PCI devices: %u; available modes: %u\n\n", devices, modes);
        if (!saved) debugPrint("Saved and read back:\n%s\n\n", path);
        else debugPrint("Report save FAILED (%d). Do not submit as a pass.\n\n", saved);
        debugPrint("FTP the JSON file after returning to the dashboard.\n");
        debugPrint("No console keys, serials or EEPROM are collected.\n");
        debugPrint("Returns to dashboard in 20 seconds.\n");
    }
    mark420(32, 0, 0, 0);
    Sleep(20000);
    mark420(32, 1, 0, 0);
    mark420(33, 0, 0, error420);
    if (trace420) NtClose(trace420);
    HalReturnToFirmware(HalRebootRoutine);
    return 0;
}
