/* SPDX-License-Identifier: MIT */
#include <stdint.h>
struct result723 {
 uint32_t code,attempted_mmio,attempted_crtc,first_mismatch;
 uint32_t flags_entry,flags_critical,flags_restored,cr0,cr3,cr4;
 uint32_t saved_index,saved_seq_index,seq_before,seq_after;
 uint32_t cr11_before,cr11_after,cr22_before,cr22_after,unlock_read;
 uint32_t selectors_restored,cleanup_ok;
 uint32_t mmio_before[11],mmio_after[11],mmio_restored[11];
 uint32_t crtc_before[4],crtc_after[4],crtc_restored[4];
};
void probe723(struct result723 *o);
