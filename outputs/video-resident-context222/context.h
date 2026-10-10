/* SPDX-License-Identifier: GPL-2.0-or-later */
#ifndef X222_CONTEXT_H
#define X222_CONTEXT_H
#include <stdint.h>
#define X222_BYTES 16384u
enum { X222_ALLOCATE=1, X222_QUERY, X222_EXPOSE, X222_RELEASE, X222_INFO, X222_CLEANUP };
enum { X222_OK=0, X222_BUSY, X222_OWNER, X222_STALE, X222_HOLD,
       X222_BAD, X222_OOM, X222_TRANSLATION, X222_EXHAUSTED, X222_WAIT,
       X222_IRQL, X222_CORRUPT, X222_EMPTY };
typedef struct { uint32_t op,generation; } X222Request;
typedef struct {
    uint32_t status,generation,owned,pages[4],allocations,releases,
             verified_bytes,exposure_refusals,cleanup_releases;
} X222Reply;
typedef struct {
    void *owner; unsigned char *memory; uint32_t generation,next_generation;
    uint32_t pages[4],allocations,releases,verified_bytes,exposure_refusals,cleanup_releases;
} X222Manager;
typedef struct {
    void *opaque;
    int (*passive)(void *);
    int (*enter)(void *); /* Native bridge: bounded, non-alertable mutex wait. */
    void (*leave)(void *);
    unsigned char *(*allocate)(void *);
    uint64_t (*translate)(void *,unsigned char *);
    void (*free)(void *,unsigned char *);
    void (*retain_owner)(void *,void *);
    void (*release_owner)(void *,void *);
} X222Ops;
void x222_initialize(X222Manager *);
void x222_action(X222Manager *,const X222Ops *,void *,const X222Request *,X222Reply *);
#endif
