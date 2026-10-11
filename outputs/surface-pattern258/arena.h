/* SPDX-License-Identifier: GPL-2.0-or-later */
#ifndef X258_ARENA_H
#define X258_ARENA_H
#include <stdint.h>
#define X258_BYTES 16384u
#define X258_VERSION 258u
enum { X258_ALLOCATE=1,X258_READ,X258_WRITE,X258_INFO,X258_CLOSE };
enum { X258_OK=0,X258_BAD,X258_BUSY,X258_OWNER,X258_STALE,X258_OOM,
       X258_TRANSLATION,X258_WAIT,X258_IRQL,X258_QUARANTINED,X258_LIMIT };
typedef struct { uint32_t op,generation,pattern,reserved; } X258Request;
typedef struct {
    uint32_t version,status,generation,physical,bytes,closed,reads,writes;
    unsigned char data[X258_BYTES];
} X258Reply;
typedef struct {
    void *owner; volatile unsigned char *memory;
    uint32_t generation,physical,closed,reads,writes,attempted;
} X258Arena;
typedef struct {
    void *opaque;
    int (*passive)(void *);
    int (*enter)(void *);
    void (*leave)(void *);
    unsigned char *(*allocate)(void *);
    uint64_t (*translate)(void *,unsigned char *);
    void (*discard_unpublished)(void *,unsigned char *);
    void (*retain_owner)(void *,void *);
} X258Ops;
/* No published-buffer free or owner-release operation: one16KiB hold until reboot.
 * Host renderer references MUST be retired before guest reuse is ever designed.
 * This diagnostic never grants the native guest GPU ownership. */
void x258_action(X258Arena *,const X258Ops *,void *,const X258Request *,X258Reply *);
unsigned char x258_pattern(uint32_t index,uint32_t seed);
#endif
