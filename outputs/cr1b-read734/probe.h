/* SPDX-License-Identifier: MIT */
#include <stdint.h>
struct result734 {
 uint32_t code,forward_status,attempted_mmio,attempted_crtc,first_mismatch;
 uint32_t expected,observed,checked;
 uint32_t flags_entry,flags_critical,flags_restored,cr0,cr3,cr4;
 uint32_t saved_index,saved_seq_index,saved_gr_index;
 uint32_t seq_before,seq_after,cr11_before,cr11_after,gr_before,gr_after;
 uint32_t cr22_before,cr22_after,cr33_before,cr33_after,unlock_read;
 uint32_t selectors_restored,cleanup_ok,cleanup_mask;
 uint32_t mmio_before[11],mmio_checked[11],mmio_restored[11];
 uint32_t crtc_before[4],crtc_checked[4],crtc_restored[4];
 uint32_t direct_count,indexed_count,after_direct630,after_indexed630;
 uint32_t direct[16],indexed[16];
};
void probe734(struct result734 *o);
