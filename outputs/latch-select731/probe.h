/* SPDX-License-Identifier: MIT */
#include <stdint.h>
struct result731 {
 uint32_t code,flags_entry,flags_critical,flags_restored,cr0,cr3,cr4;
 uint32_t saved_cr_index,saved_gr_index;
 uint32_t gr_before,gr_after,cr22_before,cr22_after,cr33_before,cr33_after;
 uint32_t mmio630_before,mmio630_after,cr1b_before,cr1b_after;
 uint32_t selectors_restored,cleanup_ok,attempts,completed;
 uint32_t requested[4],gr_read[4],cr22_first[4],cr22_direct[4],cr22_reselected[4];
};
void probe731(struct result731 *);
