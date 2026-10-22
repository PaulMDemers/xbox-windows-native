/* SPDX-License-Identifier: GPL-2.0-or-later */
#ifndef XWN_UDP655_H
#define XWN_UDP655_H
#include <stddef.h>
#include <stdint.h>
#include "../receipt652/receipt.h"
#define XWN655_BYTES 772u
struct xwn655_identity { uint8_t attempt[16], build_id[32]; };
/* Pure RAM serialization. Inputs and output must be disjoint, live memory.
 * The caller freezes the source before calling. No atomic snapshot is implied.
 * build_id is an externally assigned source-manifest token, NOT a self hash.
 * No socket, NIC, timer, disk, allocation or interrupt operation occurs here.
 * Returns 0 on success; invalid arguments leave the output untouched.
 */
int xwn655_encode(const struct xwn655_identity *, const struct xwn652_data *,
                  uint8_t *, size_t);
#endif
