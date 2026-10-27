/* SPDX-License-Identifier: MIT */
#ifndef PLAN692_H
#define PLAN692_H
#include <stdint.h>
struct plan692 {uint32_t source,source_size,source_allocation,source_contiguous;
 uint32_t stub,stub_size,stub_allocation,stub_contiguous;
 uint32_t status,requested,returned,region_size,alias_physical,alias_last;
 uint32_t framebuffer,framebuffer_size;};
/* Independent refusal bits: source1, stub2, virtual4, overlap8, framebuffer16. */
uint32_t admit692(const struct plan692 *);
#endif
