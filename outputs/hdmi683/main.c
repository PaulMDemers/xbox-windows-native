/* SPDX-License-Identifier: MIT
 * Kernel-assisted 720p baseline. No encoder writes, EEPROM or network code.
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
#include "pattern.h"

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
        snprintf(path, size, "E:\\xwn-video683-%02u.json", i);
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


static int geometry(const char *stage)
{
    static const unsigned offsets[] = {
        0x600800, 0x680800, 0x680804, 0x68080c, 0x680810, 0x680818,
        0x680820, 0x680824, 0x68082c, 0x680830, 0x680838,
        0x680630, 0x68084c, 0x680880, 0x6808c4
    };
    static const unsigned char indices[] = {0x13, 0x19, 0x28};
    unsigned char original = VIDEOREG8(0x6013d4), crtc[3];
    for (unsigned i = 0; i < 3; ++i) {
        VIDEOREG8(0x6013d4) = indices[i];
        crtc[i] = VIDEOREG8(0x6013d5);
    }
    VIDEOREG8(0x6013d4) = original;
    append("  \"%s\":{\"crtc13_19_28\":[%u,%u,%u],\"pitch_bytes\":%u,\"registers\":[",
           stage, crtc[0], crtc[1], crtc[2], 8 * (((crtc[1] & 0xe0) << 3) | crtc[0]));
    for (unsigned i = 0; i < sizeof(offsets)/sizeof(offsets[0]); ++i)
        append("%s[%u,%lu]", i ? "," : "", offsets[i], (unsigned long)VIDEOREG(offsets[i]));
    append("]},\n");
    return VIDEOREG(0x680838) == 1279 && VIDEOREG(0x680818) == 719 &&
           8 * (((crtc[1] & 0xe0) << 3) | crtc[0]) == 5120 && (crtc[2] & 15) == 3;
}

static int checkpoint(const char *phase, int complete)
{
    char path[64];
    size_t saved_used = used;
    append("  \"phase\":\"%s\",\"complete\":%s\n}\n", phase, complete ? "true" : "false");
    int rc = overflow ? 6 : save_report(path, sizeof(path));
    used = saved_used;
    if (!rc && !strcmp(phase, "before_kernel_mode"))
        append("  \"start_record\":\"%s\",\n", path + 3); /* E-root basename, no JSON escapes. */
    return rc;
}

int main(void)
{
    if (!prepare_e()) { HalReturnToFirmware(HalRebootRoutine); return 1; }
    DWORD settings = XVideoGetEncoderSettings();
    MM_STATISTICS memory = {0};
    memory.Length = sizeof(memory);
    LONG memory_status = MmQueryStatistics(&memory);
    append("{\n  \"schema\":1,\"tool\":\"xwn-video-hdmi683\",\n");
    append("  \"kernel\":[%u,%u,%u,%u],\"gpu_revision\":%u,\"mcp_revision\":%u,\n",
           XboxKrnlVersion.Major, XboxKrnlVersion.Minor, XboxKrnlVersion.Build,
           XboxKrnlVersion.Qfe, XboxHardwareInfo.GpuRevision, XboxHardwareInfo.McpRevision);
    append("  \"settings\":%lu,\"memory_status\":%lu,\"pages\":%lu,\n",
           (unsigned long)settings, (unsigned long)memory_status, (unsigned long)memory.TotalPhysicalPages);
    geometry("entry_geometry");
    /* Explicit 720p request, NTSC HDTV and enabled mode required. */
    unsigned standard = settings & VIDEO_STANDARD_MASK;
    int eligible = (settings & VIDEO_ADAPTER_MASK) == AV_PACK_HDTV &&
                   (settings & VIDEO_MODE_720P) && (standard == 0x100 || standard == 0x200) &&
                   memory_status == 0 && memory.TotalPhysicalPages == 16384;
    append("  \"eligible_720p\":%s,\"requested_mode\":[1280,720,32,60],\n", eligible ? "true" : "false");
    if (checkpoint(eligible ? "before_kernel_mode" : "refused_configuration", 0) || !eligible) {
        HalReturnToFirmware(HalRebootRoutine); return 2;
    }
    BOOL applied = XVideoSetMode(1280, 720, 32, 60);
    append("  \"kernel_mode_return\":%s,\n", applied ? "true" : "false");
    int geometry_ok = geometry("after_geometry");
    if (!applied) { checkpoint("mode_failed", 0); HalReturnToFirmware(HalRebootRoutine); return 3; }
    VIDEO_MODE mode = XVideoGetMode();
    append("  \"sdk_mode\":[%d,%d,%d,%d],\n", mode.width, mode.height, mode.bpp, mode.refresh);
    /* Draw only through SDK-owned linear framebuffer at its confirmed size.
     * Register observations are diagnostic data, never imported as a recipe. */
    if (!geometry_ok || mode.width != 1280 || mode.height != 720 || mode.bpp != 32 ||
        mode.refresh != 60 || !XVideoGetFB()) {
        checkpoint("unexpected_sdk_mode", 0); HalReturnToFirmware(HalRebootRoutine); return 4;
    }
    uint32_t *fb = (uint32_t *)XVideoGetFB();
    for (unsigned y = 0; y < 720; ++y)
        for (unsigned x = 0; x < 1280; ++x) fb[y * 1280 + x] = baseline_pixel(x,y,1280,720);
    XVideoFlushFB();
    if (checkpoint("pattern_submitted", 0)) { HalReturnToFirmware(HalRebootRoutine); return 5; }
    Sleep(20000);
    checkpoint("restart_requested", 1);
    HalReturnToFirmware(HalRebootRoutine);
    return 0;
}
