/* SPDX-License-Identifier: MIT
 * Emulator-only color/Z24S8 coherence oracle. No Windows or physical deployment.
 * The private pbkit copy adds two read-only accessors; rendering is unchanged.
 */
#include <hal/video.h>
#include <hal/xbox.h>
#include <hal/debug.h>
#include <nxdk/mount.h>
#include <pbkit/pbkit.h>
#include <pbkit/nv_regs.h>
#include <windows.h>
#include <xboxkrnl/xboxkrnl.h>
#include <stdint.h>
#include <stdio.h>
#include <stdarg.h>
#include <stdlib.h>

extern DWORD *xwn_depth_buffer(void);
extern DWORD xwn_depth_pitch(void);
#define W 640u
#define H 480u
#define ROOT "E:\\xwngpu143\\"
static HANDLE logf = INVALID_HANDLE_VALUE;
static DWORD *snapshot;
static unsigned captures, stores, failed;

static int flush(HANDLE h) {
    IO_STATUS_BLOCK io;
    return NT_SUCCESS(NtFlushBuffersFile(h, &io));
}
static void report(const char *fmt, ...) {
    char b[512]; DWORD n; va_list ap;
    va_start(ap, fmt); int len = vsnprintf(b, sizeof(b), fmt, ap); va_end(ap);
    if (len < 0 || len >= (int)sizeof(b) ||
        !WriteFile(logf, b, len, &n, NULL) || n != (DWORD)len || !flush(logf)) failed = 1;
}
static int idle(void) {
    DWORD start = GetTickCount();
    while (pb_busy()) {
        if (GetTickCount() - start > 10000) {
            report("FAIL gpu_timeout\r\n"); failed = 1; return 0;
        }
        Sleep(0);
    }
    return 1;
}
static int capture(unsigned epoch, unsigned depth, unsigned stage, volatile DWORD *p, DWORD pitch) {
    char path[100]; DWORD n;
    /* Volatile accesses preserve the actual CPU read path under test. */
    for (unsigned y = 0; y < H; ++y)
        for (unsigned x = 0; x < W; ++x) snapshot[y * W + x] = p[y * (pitch / 4) + x];
    snprintf(path, sizeof(path), ROOT "e%u-%c-s%u.raw", epoch, depth ? 'z' : 'c', stage);
    HANDLE f = CreateFileA(path, GENERIC_WRITE, 0, NULL, CREATE_NEW, FILE_ATTRIBUTE_NORMAL, NULL);
    if (f == INVALID_HANDLE_VALUE) { report("FAIL create %s\r\n", path); failed = 1; return 0; }
    int ok = WriteFile(f, snapshot, W * H * 4, &n, NULL) && n == W * H * 4 && flush(f);
    CloseHandle(f);
    if (!ok) { report("FAIL write %s\r\n", path); failed = 1; return 0; }
    ++captures;
    report("CAPTURE %u %u %u %08lx %lu %lu\r\n", epoch, depth, stage,
           (DWORD)p & 0x03ffffff, pitch, W * H * 4);
    return !failed;
}
static void clear(unsigned depth, unsigned x, unsigned y, unsigned w, unsigned h, DWORD v) {
    if (depth) pb_set_depth_stencil_buffer_region(NV097_SET_SURFACE_FORMAT_ZETA_Z24S8,
                                                  v >> 8, v & 255, x, y, w, h);
    else pb_fill(x, y, w, h, v);
}
static int exercise(unsigned epoch, unsigned depth) {
    volatile DWORD *p = depth ? xwn_depth_buffer() : pb_extra_buffer(0);
    DWORD pitch = depth ? xwn_depth_pitch() : pb_back_buffer_pitch();
    if (!p || pitch < W * 4 || pitch % 4 || pitch > 8192) { failed = 1; return 0; }
    report("SURFACE %u %u %08lx %lu\r\n", epoch, depth, (DWORD)p & 0x03ffffff, pitch);
    DWORD base = depth ? 0x345678a5u : 0xa5317ca4u;
    DWORD partial = depth ? 0x789abc3cu : 0xc48259edu;
    DWORD last = depth ? 0xabcdef5au : 0x9274c13bu;
    base ^= epoch * 0x01010100u; partial ^= epoch * 0x01010100u; last ^= epoch * 0x01010100u;
    clear(depth, 0, 0, W, H, base);
    if (!idle() || !capture(epoch, depth, 0, p, pitch)) return 0;
    for (unsigned round = 0; round < 17; ++round) {
        for (unsigned y = 5; y < 34; ++y) for (unsigned x = 3; x < 64; ++x) {
            p[y * (pitch / 4) + x] = 0x52100000u ^ (epoch << 20) ^ (depth << 19) ^
                                      (round << 12) ^ (y << 6) ^ x;
            ++stores;
        }
    }
    __asm__ __volatile__("sfence" ::: "memory");
    if (!capture(epoch, depth, 1, p, pitch)) return 0;
    /* GPU consumes CPU data; partial clear must retain CPU and GPU pixels outside it. */
    clear(depth, 19, 13, 97, 53, partial);
    if (!idle() || !capture(epoch, depth, 2, p, pitch)) return 0;
    clear(depth, 0, 0, W, H, last);
    return idle() && capture(epoch, depth, 3, p, pitch);
}
int main(void) {
    XVideoSetMode(640, 480, 32, REFRESH_DEFAULT);
    logf = CreateFileA("D:\\bootstrap.log", GENERIC_WRITE, 0, NULL, CREATE_NEW, FILE_ATTRIBUTE_NORMAL, NULL);
    if (logf == INVALID_HANDLE_VALUE) { XReboot(); return 1; }
    int was_mounted = nxIsDriveMounted('E');
    int mounted = was_mounted || nxMountDrive('E', "\\Device\\Harddisk0\\Partition1\\");
    report("MOUNT_E %d %d %lu\r\n", was_mounted, mounted, mounted ? 0ul : GetLastError());
    int created = mounted && CreateDirectoryA("E:\\xwngpu143", NULL);
    report("CREATE_OUTPUT %d %lu\r\n", created, created ? 0ul : GetLastError());
    CloseHandle(logf); logf = INVALID_HANDLE_VALUE;
    if (!created) {
        debugPrint("Existing/unwritable coherence output; refusing rerun.\n");
        Sleep(2000); XReboot(); return 1;
    }
    logf = CreateFileA(ROOT "result.log", GENERIC_WRITE, 0, NULL, CREATE_NEW, FILE_ATTRIBUTE_NORMAL, NULL);
    if (logf == INVALID_HANDLE_VALUE) { XReboot(); return 1; }
    snapshot = malloc(W * H * 4);
    report("BEGIN 143 2 2 4 640 480 17\r\n");
    if (!snapshot) failed = 1;
    for (unsigned epoch = 0; epoch < 2 && !failed; ++epoch) {
        report("INIT_BEGIN %u\r\n", epoch);
        pb_extra_buffers(1);
        int status = pb_init();
        report("INIT_RETURN %u %d\r\n", epoch, status);
        if (status) { failed = 1; break; }
        pb_target_extra_buffer(0);
        if (pb_back_buffer_width() != W || pb_back_buffer_height() != H) failed = 1;
        if (!failed && idle()) for (unsigned depth = 0; depth < 2 && !failed; ++depth)
            if (!exercise(epoch, depth)) failed = 1;
        report("KILL_BEGIN %u\r\n", epoch);
        pb_kill();
        report("KILL_RETURN %u\r\n", epoch);
    }
    report("COMPLETE %u %u %u\r\n", captures, stores, failed);
    report("NORMAL_REBOOT_REQUEST\r\n");
    flush(logf); CloseHandle(logf); free(snapshot);
    XReboot(); return failed ? 1 : 0;
}
