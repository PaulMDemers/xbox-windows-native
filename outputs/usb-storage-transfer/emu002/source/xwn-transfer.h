/* Diagnostic byte capture only; no guest/device state changes. */
#include "qemu/iov.h"
static GMutex xwn_transfer_lock;
static FILE *xwn_transfer_file;
static bool xwn_transfer_init, xwn_transfer_full;
static uint64_t xwn_transfer_seq, xwn_transfer_ids, xwn_transfer_written;
static uint64_t xwn_transfer(uint64_t id, uint64_t phase, uint64_t offset,
                             uint64_t bytes, QEMUIOVector *iov, size_t iov_offset,
                             void *owner, int ret, uint64_t flags)
{
    uint64_t h[16] = { UINT64_C(0x315246534e5758), 1 };
    uint8_t *copy = NULL;
    size_t count = 0;
    const char *base;
    g_mutex_lock(&xwn_transfer_lock);
    if (!xwn_transfer_init) {
        xwn_transfer_init = true;
        base = getenv("XWN_TRANSFER_TRACE_BASE");
        if (base && *base) {
            char *path = g_strdup_printf("%s.%s.bin", base, XWN_TRANSFER_COMPONENT);
            xwn_transfer_file = fopen(path, "wb");
            g_free(path);
            if (!xwn_transfer_file) {
                fprintf(stderr, "XWN transfer trace open failed\n");
                abort();
            }
        }
    }
    if (!xwn_transfer_file || xwn_transfer_full ||
        (!id && (offset < UINT64_C(8004132864) || bytes == 0))) {
        g_mutex_unlock(&xwn_transfer_lock);
        return 0;
    }
    if (!id) { id = ++xwn_transfer_ids; }
    if (iov && bytes && bytes <= 1048576 && iov_offset <= iov->size &&
        bytes <= iov->size - iov_offset) {
        count = bytes;
        copy = g_malloc(count);
        if (qemu_iovec_to_buf(iov, iov_offset, copy, count) != count) { abort(); }
    } else if (bytes && (iov || phase == 4 || phase == 5)) {
        flags |= UINT64_C(1) << 63;
    }
    if (xwn_transfer_written + sizeof(h) + count > 268435456) {
        xwn_transfer_full = true;
        flags |= UINT64_C(1) << 62;
        count = 0;
    }
    h[2] = ++xwn_transfer_seq; h[3] = id; h[4] = phase;
    h[5] = offset; h[6] = bytes; h[7] = (uintptr_t)iov;
    h[8] = (uintptr_t)owner; h[9] = (int64_t)ret;
    h[10] = g_get_monotonic_time(); h[11] = iov_offset;
    h[12] = count; h[13] = flags;
    h[14] = iov ? iov->niov : 0; h[15] = 0;
    if (fwrite(h, sizeof(h), 1, xwn_transfer_file) != 1 ||
        (count && fwrite(copy, count, 1, xwn_transfer_file) != 1) ||
        fflush(xwn_transfer_file)) {
        fprintf(stderr, "XWN transfer trace write failed\n"); abort();
    }
    xwn_transfer_written += sizeof(h) + count;
    g_free(copy);
    g_mutex_unlock(&xwn_transfer_lock);
    return id;
}
