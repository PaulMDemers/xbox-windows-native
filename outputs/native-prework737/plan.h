/* SPDX-License-Identifier: MIT */
#ifndef PLAN705_H
#define PLAN705_H
#include <stdint.h>
struct plan705 {
 uint32_t source,source_size,source_allocation,source_contiguous;
 uint32_t stub,stub_size,stub_allocation,stub_contiguous;
 uint32_t status,requested,returned,region_size;
 uint32_t alias[8],alias_last[8];
 uint32_t framebuffer,framebuffer_size,framebuffer_allocation;
};
int reservation_contains705(uint32_t,uint32_t,uint32_t);
uint32_t admit705(const struct plan705 *);
#endif
