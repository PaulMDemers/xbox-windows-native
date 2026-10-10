/* SPDX-License-Identifier: GPL-2.0-or-later
 * Pure CPU planning/lifetime model. No MMIO, native allocator or runtime adapter.
 * Every caller serializes the context. Host witnesses are explicitly mock evidence.
 */
#ifndef X215_PROTOCOL_H
#define X215_PROTOCOL_H
#include <stdint.h>
#define X215_WORDS 27u
#define X215_RANGES 4u
#define X215_HANDLES 7u
#define X215_PROOF_ALL 63u
#define X215_DRAIN_ALL 7u
enum X215State { X215_EMPTY,X215_PREPARED,X215_EXPOSED,X215_SUBMITTED,
 X215_COMPLETE,X215_DRAINED,X215_QUARANTINED,X215_RELEASED };
enum X215Proof { X215_RESIDENT=1,X215_INSTANCE_OWNER=2,X215_CONTEXT_OWNER=4,
 X215_DMA_ADDRESS=8,X215_COMPLETION_ORDER=16,X215_TOKEN_CLEARED=32 };
enum X215Drain { X215_PRODUCER_STOPPED=1,X215_NO_REFERENCES=2,X215_OWNER_RESTORED=4 };
typedef struct { uint32_t base,bytes; } X215Range;
typedef struct {
 X215Range range[X215_RANGES]; /* source,destination,completion,command */
 uint32_t source_offset,dest_offset,source_pitch,dest_pitch,width,height;
 uint32_t ramht_base,objects_base,channel,token;
} X215Input;
typedef struct {
 uint32_t words[X215_WORDS],dma[4][4],graphics[3][4];
 struct { uint32_t address,handle,context; } entry[X215_HANDLES];
 uint32_t packet_bytes,source_end,dest_end;
} X215Plan;
typedef struct { uint32_t state,generation;uint64_t last_time,deadline; } X215Context;
int x215_plan(const X215Input *,X215Plan *);
int x215_prepare(X215Context *,uint32_t generation,uint64_t now,uint64_t budget);
int x215_expose(X215Context *,uint32_t proofs,uint64_t now);
int x215_submit(X215Context *);
int x215_observe(X215Context *,uint32_t generation,uint32_t token,uint64_t now,int fault);
int x215_drain(X215Context *,uint32_t generation,uint32_t proofs);
int x215_release(X215Context *);
int x215_abort(X215Context *);
#endif
