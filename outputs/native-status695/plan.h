/* SPDX-License-Identifier: MIT */
#ifndef PLAN695_H
#define PLAN695_H
#include <stdint.h>
struct plan695 {uint32_t source,source_size,source_allocation,source_contiguous;
 uint32_t stub,stub_size,stub_allocation,stub_contiguous;
 uint32_t status,requested,returned,region_size,alias_physical,alias_last;
 uint32_t framebuffer,framebuffer_size;};
/* Independent refusal bits: source1, stub2, virtual4, overlap8, framebuffer16. */
int reservation_contains695(uint32_t requested,uint32_t returned,uint32_t size);
uint32_t admit695(const struct plan695 *);
#endif
