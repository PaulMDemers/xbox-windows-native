/* SPDX-License-Identifier: MIT */
#include <stdint.h>
struct result749 {
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
};
void probe749(struct result749 *o);
