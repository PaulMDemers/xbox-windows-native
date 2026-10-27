/* SPDX-License-Identifier: MIT */
#ifndef PLAN694_H
#define PLAN694_H
#include <stdint.h>
struct plan694 {uint32_t source,source_size,source_allocation,source_contiguous;
 uint32_t stub,stub_size,stub_allocation,stub_contiguous;
 uint32_t status,requested,returned,region_size,alias_physical,alias_last;
 uint32_t framebuffer,framebuffer_size;};
/* Independent refusal bits: source1, stub2, virtual4, overlap8, framebuffer16. */
int reservation_contains694(uint32_t requested,uint32_t returned,uint32_t size);
uint32_t admit694(const struct plan694 *);
#endif
