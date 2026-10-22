/* SPDX-License-Identifier: GPL-2.0-or-later
 * RAM-only observations of existing reads. No new hardware I/O.
 */
#ifndef XWN_TRACE648_H
#define XWN_TRACE648_H
struct xwn_edge648 {
 unsigned wanted,first,last,samples,byte_changes,bit_changes,completed;
};
struct xwn_trace648 {
 unsigned waits_started,waits_completed,failed_wait;
 struct xwn_edge648 edge[6];
};
extern volatile struct xwn_trace648 XwnTrace648;
#endif
