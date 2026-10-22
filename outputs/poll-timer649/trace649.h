/* SPDX-License-Identifier: GPL-2.0-or-later
 * RAM-only observations of existing reads. No new hardware I/O.
 */
#ifndef XWN_TRACE649_H
#define XWN_TRACE649_H
struct xwn_edge649 {
 unsigned wanted,first,last,samples,byte_changes,bit_changes,completed,begin,end,elapsed;
};
struct xwn_trace649 {
 unsigned waits_started,waits_completed,failed_wait;
 struct xwn_edge649 edge[6];
};
unsigned xwn_timer649(void);
extern volatile struct xwn_trace649 XwnTrace649;
#endif
