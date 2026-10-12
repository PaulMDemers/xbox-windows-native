/* SPDX-License-Identifier: MIT
 * Read-only video inventory. No mode setter, GPU commands, EEPROM writes,
 * Windows startup changes or PCI writes. Only an exclusive app-local log.
 */
#include <hal/video.h>
#include <windows.h>
#include <xboxkrnl/xboxkrnl.h>
#include <stdint.h>
#include <stdio.h>
#include <stdarg.h>

typedef struct {
    uint32_t magic, version, bytes, phase, error, log_ok;
    uint32_t kernel[4], flags, gpu, mcpx, memory_status, total_pages;
    uint32_t settings, scanout, hvalid, vvalid, conexant_status, conexant_value;
    uint32_t focus_status, focus_value, mode_count;
    uint32_t modes[16][4];
} Record;
volatile Record record288;
static HANDLE log_file = INVALID_HANDLE_VALUE;
static unsigned log_ok;
__attribute__((noinline)) void checkpoint288(unsigned phase, volatile Record *r)
{
    __asm__ __volatile__("" ::: "memory");
    r->phase = phase;
    __asm__ __volatile__("" ::: "memory");
}
static void report(const char *format, ...)
{
    char text[256]; DWORD written = 0; va_list ap;
    va_start(ap, format); int n = vsnprintf(text, sizeof(text), format, ap); va_end(ap);
    if (n < 0 || n >= (int)sizeof(text)) { log_ok = 0; return; }
    if (log_file != INVALID_HANDLE_VALUE &&
        (!WriteFile(log_file, text, (DWORD)n, &written, NULL) || written != (DWORD)n))
        log_ok = 0;
}
int main(void)
{
    MM_STATISTICS memory = {0}; VIDEO_MODE mode; void *cursor = NULL;
    ULONG value = 0; NTSTATUS status;
    record288.magic = 0x288c0de; record288.version = 1; record288.bytes = sizeof(Record);
    log_file = CreateFileA("D:\\video288.txt", GENERIC_WRITE, FILE_SHARE_READ,
                           NULL, CREATE_NEW, FILE_ATTRIBUTE_NORMAL, NULL);
    log_ok = log_file != INVALID_HANDLE_VALUE;
    report("XWN_VIDEO288 version=1 mode_changes=0\r\n");
    record288.kernel[0] = XboxKrnlVersion.Major; record288.kernel[1] = XboxKrnlVersion.Minor;
    record288.kernel[2] = XboxKrnlVersion.Build; record288.kernel[3] = XboxKrnlVersion.Qfe;
    record288.flags = XboxHardwareInfo.Flags; record288.gpu = XboxHardwareInfo.GpuRevision;
    record288.mcpx = XboxHardwareInfo.McpRevision;
    memory.Length = sizeof(memory); status = MmQueryStatistics(&memory);
    record288.memory_status = (uint32_t)status; record288.total_pages = memory.TotalPhysicalPages;
    record288.settings = XVideoGetEncoderSettings();
    record288.scanout = VIDEOREG(0x600800);
    record288.hvalid = VIDEOREG(0x680838); record288.vvalid = VIDEOREG(0x680818);
    report("KERNEL %lu %lu %lu %lu\r\n", (unsigned long)record288.kernel[0],
           (unsigned long)record288.kernel[1], (unsigned long)record288.kernel[2], (unsigned long)record288.kernel[3]);
    report("HARDWARE flags=%08lx gpu=%lu mcpx=%lu memory_status=%08lx pages=%lu\r\n",
           (unsigned long)record288.flags, (unsigned long)record288.gpu, (unsigned long)record288.mcpx,
           (unsigned long)record288.memory_status, (unsigned long)record288.total_pages);
    report("VIDEO settings=%08lx scanout=%08lx hvalid=%08lx vvalid=%08lx\r\n",
           (unsigned long)record288.settings, (unsigned long)record288.scanout,
           (unsigned long)record288.hvalid, (unsigned long)record288.vvalid);
    /* Same register-zero probes as pinned Cromwell: 7-bit 0x45/0x6a.
     * Kernel API takes an 8-bit bus address. Read bit set explicitly.
     * If neither responds, retain UNKNOWN; do not infer Xcalibur by absence. */
    status = HalReadSMBusValue(0x8b, 0, FALSE, &value);
    record288.conexant_status = (uint32_t)status; record288.conexant_value = value;
    value = 0; status = HalReadSMBusValue(0xd5, 0, FALSE, &value);
    record288.focus_status = (uint32_t)status; record288.focus_value = value;
    report("ENCODER conexant_status=%08lx conexant_value=%08lx focus_status=%08lx focus_value=%08lx\r\n",
           (unsigned long)record288.conexant_status, (unsigned long)record288.conexant_value,
           (unsigned long)record288.focus_status, (unsigned long)record288.focus_value);
    while (XVideoListModes(&mode, 32, REFRESH_DEFAULT, &cursor)) {
        unsigned n = record288.mode_count;
        if (n == 16) { record288.error = 1; break; }
        record288.modes[n][0] = mode.width; record288.modes[n][1] = mode.height;
        record288.modes[n][2] = mode.bpp; record288.modes[n][3] = mode.refresh;
        record288.mode_count = n + 1;
        report("MODE %d %d %d %d\r\n", mode.width, mode.height, mode.bpp, mode.refresh);
    }
    if (record288.memory_status || !record288.mode_count) record288.error = 2;
    report("COMPLETE error=%lu log_ok=%u modes=%lu mode_changes=0\r\n",
           (unsigned long)record288.error, log_ok, (unsigned long)record288.mode_count);
    if (log_file != INVALID_HANDLE_VALUE) {
        IO_STATUS_BLOCK io;
        if ((LONG)NtFlushBuffersFile(log_file, &io) < 0) log_ok = 0;
        if (!CloseHandle(log_file)) log_ok = 0;
    }
    record288.log_ok = log_ok;
    checkpoint288(33, &record288);
    Sleep(10000);
    HalReturnToFirmware(HalRebootRoutine);
    return 0;
}
