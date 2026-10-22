/* SPDX-License-Identifier: GPL-2.0-or-later
 * Transport-independent experiment. No native disk backend or deployment.
 */
#ifndef XWN_RECEIPT652_H
#define XWN_RECEIPT652_H
#include <stdint.h>
#define XWN652_SECTOR 512u
#define XWN652_PAYLOAD 1024u
#define XWN652_SLOT 1536u
/* Order is documented in FORMAT.md; all observations retain raw 32-bit values. */
struct xwn652_data {
    int32_t result;
    uint32_t post_kind; /* 1: after return; 2: after original failure blanking */
    uint32_t request[8], state[9], trace[63], pre[47], post[47];
};
struct xwn652_identity { uint8_t attempt[16], candidate_sha256[32]; };
struct xwn652_io {
    void *opaque;
    /* Exactly 512 bytes, return zero only on definite complete success.
     * No internal retries. The future backend must impose its own finite bound.
     * Sector indices are 0..2 within a separately verified owned file extent.
     */
    int (*read)(void *, unsigned, uint8_t *);
    int (*write)(void *, unsigned, const uint8_t *);
    int (*flush)(void *);
};
enum xwn652_status {
    XWN652_OK=0, XWN652_ARGUMENT=1, XWN652_ALREADY_ATTEMPTED=2,
    XWN652_PREFLIGHT_READ=3, XWN652_SEED_MISMATCH=4,
    XWN652_PAYLOAD_WRITE=5, XWN652_PAYLOAD_FLUSH=6,
    XWN652_PAYLOAD_READ=7, XWN652_PAYLOAD_MISMATCH=8,
    XWN652_COMMIT_WRITE=9, XWN652_COMMIT_FLUSH=10,
    XWN652_FINAL_READ=11, XWN652_FINAL_MISMATCH=12
};
struct xwn652_guard { unsigned attempted; };
struct xwn652_scratch { uint8_t record[XWN652_SLOT], sector[XWN652_SECTOR]; };
uint32_t xwn652_crc(const uint8_t *, unsigned);
void xwn652_seed(const struct xwn652_identity *, unsigned, uint8_t *);
int xwn652_encode(const struct xwn652_identity *, const struct xwn652_data *, uint8_t *);
/* Pure format validation; a valid record alone is NOT a flush acknowledgment. */
int xwn652_validate(const struct xwn652_identity *, const uint8_t *);
/* Uses caller-owned scratch; calls no allocator, clock or hardware directly.
 * Guard is consumed before I/O, including failures. Never repeat an uncertain
 * write, reset a used slot, or use this engine as authorization for raw writes.
 */
int xwn652_store(struct xwn652_guard *, const struct xwn652_io *,
                 const struct xwn652_identity *, const struct xwn652_data *,
                 struct xwn652_scratch *);
#endif
