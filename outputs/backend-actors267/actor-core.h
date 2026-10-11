/* SPDX-License-Identifier: GPL-2.0-or-later
 * Retained diagnostic records. State3 acknowledges original work-function return,
 * not OS-thread exit or join. No owner dereference follows that publication.
 */
#ifndef X267_ACTOR_CORE_H
#define X267_ACTOR_CORE_H
#include <stdint.h>
#define X267_ACTORS 65536u
typedef struct X267Actor {
    unsigned state, kind;
    uint64_t epoch, thread;
    uintptr_t owner;
    void *(*function)(void *);
    void *argument;
} X267Actor;
static inline unsigned x267_reserve(unsigned *next, unsigned *overflow,
                                    unsigned capacity)
{
    unsigned n=__atomic_load_n(next,__ATOMIC_RELAXED);
    for (;;) {
        if (n>=capacity) {
            __atomic_store_n(overflow,1,__ATOMIC_RELEASE);
            return capacity;
        }
        if (__atomic_compare_exchange_n(next,&n,n+1,0,__ATOMIC_RELAXED,
                                        __ATOMIC_RELAXED)) return n;
    }
}
static inline void x267_start(X267Actor *a,uint64_t thread)
{
    a->thread=thread;
    __atomic_store_n(&a->state,2,__ATOMIC_RELEASE);
}
static inline void x267_finish(X267Actor *a)
{
    __atomic_store_n(&a->state,3,__ATOMIC_RELEASE);
}
static inline unsigned x267_state(const X267Actor *a)
{
    return a?__atomic_load_n(&a->state,__ATOMIC_ACQUIRE):0;
}
#endif
