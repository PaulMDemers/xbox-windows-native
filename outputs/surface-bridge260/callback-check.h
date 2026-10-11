/* SPDX-License-Identifier: GPL-2.0-or-later */
#ifndef X260_CALLBACK_CHECK_H
#define X260_CALLBACK_CHECK_H
#include <stdint.h>
#define X260_CALLBACKS 256u
unsigned x260_callbacks_check(const uint64_t before[][4], unsigned nb,
    const uint64_t after[][4], unsigned na, uint64_t identity,
    uint64_t begin, uint64_t opaque, unsigned stage);
#endif
