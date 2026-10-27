/* SPDX-License-Identifier: MIT */
#include <stdint.h>
struct result727 {
 uint32_t code,attempts,flags_entry,flags_critical,flags_restored,cr0,cr3,cr4;
 uint32_t saved_index,saved_seq_index,seq_before,seq_after;
 uint32_t before[3],after[3],cleanup_ok,selectors_restored;
 uint32_t mmio630[6],cr1b[6],packed[6];
 uint32_t late_count,late_changes,late_min,late_max,summary;
 uint32_t cr1b_attempt,unlock_attempt,unlock_read,unlock_cr11;
 uint32_t prewrite630,prewrite1b,prewrite_packed,direct,indexed,write_reads_packed,attempts_packed;
};
void probe727(struct result727 *);
