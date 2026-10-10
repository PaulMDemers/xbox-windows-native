/* SPDX-License-Identifier: GPL-2.0-or-later */
#ifndef X224_RETIREMENT_H
#define X224_RETIREMENT_H
#include <stdint.h>
#define X224_ROUNDS 8u
#define X224_WORDS 16u
enum { X224_OFF=20, X224_OBSERVED, X224_READ_FAILED };
enum { X224_DMA_DATA=1, X224_METHOD=2, X224_SUBROUTINE=4,
       X224_CACHE=8, X224_RUNOUT=16, X224_GRAPH_IRQ=32,
       X224_DMA_ERROR=64, X224_FIFO_IRQ=128, X224_CHANGED=256,
       X224_DMA_SUSPENDED=512 };
#define X224_NO_OWNERSHIP 0x80000000u
#define X224_UNMODELED_BUSY 0x40000000u
typedef struct { uint32_t generation,reserved; } X224Request;
typedef struct {
    uint32_t status,rounds,reads,reasons;
    uint32_t values[X224_ROUNDS][X224_WORDS];
} X224Reply;
typedef int (*X224Read)(void *,uint32_t,uint32_t *);
/* Read-only offsets checked against the pinned model/header. Neither busy bit
 * nor a sequential snapshot is a retirement/ownership capability. */
extern const uint32_t X224Offsets[X224_WORDS];
void x224_sample(X224Read,void *,X224Reply *);
#endif
