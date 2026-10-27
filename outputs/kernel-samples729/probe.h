/* SPDX-License-Identifier: MIT */
#include <stdint.h>
struct result729 {
 uint32_t code,attempts,flags_entry,flags_critical,flags_restored,cr0,cr3,cr4;
 uint32_t saved_index,saved_seq_index,seq_before,seq_after;
 uint32_t before[3],after[3],cleanup_ok,selectors_restored;
 uint32_t mmio630[6],cr1b[6],packed[6];
 uint32_t late_count,late_changes,late_min,late_max,summary;
 uint32_t cr1b_attempt,unlock_attempt,unlock_read,unlock_cr11;
 uint32_t prewrite630,prewrite1b,prewrite_packed,direct,indexed,write_reads_packed,attempts_packed;
 uint32_t blank630[32],blank1b[32],blank_count,blank_changes,blank_min,blank_max;
 uint32_t gate630,gate1b,gate_seq;
};
void probe729(struct result729 *);
