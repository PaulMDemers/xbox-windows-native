/* SPDX-License-Identifier: MIT */
#include <stdint.h>
struct result726 {
 uint32_t code,attempts,flags_entry,flags_critical,flags_restored,cr0,cr3,cr4;
 uint32_t saved_index,saved_seq_index,seq_before,seq_after;
 uint32_t before[3],after[3],cleanup_ok,selectors_restored;
 uint32_t mmio630[6],cr1b[6],packed[6];
 uint32_t late_count,late_changes,late_min,late_max,summary;
};
void probe726(struct result726 *);
