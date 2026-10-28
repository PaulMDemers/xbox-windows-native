/* SPDX-License-Identifier: MIT */
#ifndef PAGE705_H
#define PAGE705_H
#include <stdint.h>
struct reloc705 {uint32_t offset,value;};
/* Template metadata: end, flat, fault, post, payload-entry. */
int page705(uint8_t *,const uint8_t *,const uint32_t *,const uint8_t *,uint32_t,
 const struct reloc705 *,uint32_t,uint32_t,uint32_t);
#endif
