/* SPDX-License-Identifier: MIT */
#ifndef PLAN691_H
#define PLAN691_H
#include <stdint.h>
struct plan691 {uint32_t source,source_size,source_allocation,source_contiguous;
 uint32_t stub,stub_size,stub_allocation,stub_contiguous;
 uint32_t status,requested,returned,region_size,alias_physical,alias_last;
 uint32_t framebuffer,framebuffer_size;};
/* Independent refusal bits: source1, stub2, virtual4, overlap8, framebuffer16. */
uint32_t admit691(const struct plan691 *);
#endif
