/* SPDX-License-Identifier: MIT */
#ifndef XWN_PROBE721_H
#define XWN_PROBE721_H
#include <stdint.h>
struct result721 {
 uint32_t code, attempted, before, seq_before, unlock_read, prewrite;
 uint32_t requested, direct_after, selected_after, restored_after;
 uint32_t saved_index, saved_seq_index, flags_entry, flags_critical;
 uint32_t flags_restored, cr0, cr3, cr4, cr11_before, cr11_after;
 uint32_t index_before_write, index_after_write, selectors_restored, seq_restored;
};
void probe721(struct result721 *);
#endif
