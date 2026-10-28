/* SPDX-License-Identifier: MIT */
#include <stdint.h>
struct result775 {
 uint32_t code,count,mismatch_mask,invalid_mask,flags_entry,flags_exit,cr0,cr3,cr4;
 uint32_t first[7],second[7],third[7];
};
void probe775(struct result775 *o);
