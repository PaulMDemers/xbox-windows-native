/* SPDX-License-Identifier: MIT */
#include <stdint.h>
struct result760 {
 uint32_t code,forward_status,attempted_mmio,attempted_crtc,first_mismatch;
 uint32_t expected,observed,checked;
 uint32_t flags_entry,flags_critical,flags_restored,cr0,cr3,cr4;
 uint32_t saved_index,saved_seq_index,saved_gr_index;
 uint32_t seq_before,seq_after,cr11_before,cr11_after,gr_before,gr_after;
 uint32_t cr22_before,cr22_after,cr33_before,cr33_after,unlock_read;
 uint32_t selectors_restored,cleanup_ok,cleanup_mask;
 uint32_t mmio_before[11],mmio_checked[11],mmio_restored[11];
 uint32_t crtc_before[4],crtc_checked[4],crtc_restored[4];
 uint32_t h_before[7],h_checked[7],h_restored[7];
 uint32_t h_attempted,h_count,h_first,h_cleanup_mask,output_restored,h_expected,h_observed;
 uint32_t c4_before,c4_checked,c4_restored,c4_attempted,c4_cleanup_mask,c5_before,c5_checked,c5_restored;
 uint32_t c5_target,c5_attempted,c5_after,c4_after;
 uint32_t c0_before,c0_target,c0_attempted,c0_after,c0_restored,c0_cleanup_mask,c4_after_c0,c5_after_c0;
 uint32_t c2_before,c2_target,c2_attempted,c2_after,c2_restored,c2_cleanup_mask,c0_after_c2,c4_after_c2,c5_after_c2;
 uint32_t c3_before,c3_target,c3_attempted,c3_after,c3_restored,c3_cleanup_mask,c0_after_c3,c2_after_c3,c4_after_c3,c5_after_c3;
 uint32_t c5b_before,c5b_target,c5b_attempted,c5b_after,c5b_restored,c5b_cleanup_mask,c0_after_c5b,c2_after_c5b,c3_after_c5b,c4_after_c5b;
 uint32_t c17_before,c17_target,c17_attempted,c17_after,c17_restored,c17_cleanup_mask,c0_after_c17,c2_after_c17,c3_after_c17,c4_after_c17,c5_after_c17;
 uint32_t c1_before,c1_target,c1_attempted,c1_after,c1_restored,c1_cleanup_mask,c0_after_c1,c2_after_c1,c3_after_c1,c4_after_c1,c5_after_c1,c17_after_c1;
};
void probe760(struct result760 *o);
