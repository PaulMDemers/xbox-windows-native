/* SPDX-License-Identifier: GPL-2.0-or-later
 * Serialized, portable transition reducer. No MMIO and no runtime proof adapter.
 * Passing synthetic receipts tests ordering; it never qualifies GPU ownership.
 */
#ifndef X226_OWNER_H
#define X226_OWNER_H
#include <stdint.h>
#define X226_MAX_RANGES 16u
enum X226State { X226_EMPTY, X226_PREPARED, X226_REVOKING, X226_RETIRING,
 X226_INSTALLING, X226_CONTEXT, X226_READY, X226_SUBMITTED, X226_COMPLETED,
 X226_DRAINING, X226_RESTORING, X226_RELEASED, X226_QUARANTINED };
enum X226Action { X226_REVOKE=1, X226_RETIRE_OLD, X226_INSTALL,
 X226_SERVICE_CONTEXT, X226_SUBMIT, X226_RETIRE_NEW, X226_RESTORE };
enum X226Result { X226_REFUSED, X226_ACCEPTED, X226_WAITING };
typedef struct { uint32_t start, bytes; } X226Range;
typedef struct {
 uint32_t generation, channel, old_count, new_count;
 uint32_t census_complete, backing_verified, backend_supported, context_supported;
 uint64_t budget;
 X226Range old_range[X226_MAX_RANGES], new_range[X226_MAX_RANGES];
} X226Plan;
typedef struct {
 uint32_t generation, action, sequence, status;
 /* Adapter must derive these from serialized actual operations, never registers
  * alone. These are typed obligations, not a bitmask/host authorization grant. */
 uint32_t producers_revoked, queue_consumed, backend_finished, references_ended;
 uint32_t exact_private_install, trapped_channel, context_valid, context_channel;
 uint32_t irq_serviced, owner_restored;
} X226Receipt;
typedef struct {
 uint32_t state, generation, channel, pending_action, sequence, exposed;
 uint64_t last_time, deadline;
 X226Plan plan; /* Owned immutable copy; later adapter uses these exact ranges. */
} X226Owner;
int x226_prepare(X226Owner *, const X226Plan *, uint64_t now);
int x226_begin(X226Owner *, uint32_t action, uint64_t now);
int x226_receipt(X226Owner *, const X226Receipt *, uint64_t now);
int x226_completion(X226Owner *, uint32_t generation, uint32_t token,
                    uint64_t now, int fault);
int x226_tick(X226Owner *, uint64_t now);
int x226_cancel(X226Owner *);
#endif
