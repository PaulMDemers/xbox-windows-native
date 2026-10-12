/* Bounded observation accounting only. No renderer integration or ownership grant.
 * The single acknowledged owner calls these functions under the one-word gate.
 * Opaque identities are NEVER dereferenced here. Four registrations are immutable.
 */
#ifndef XWN_LIFETIME270_H
#define XWN_LIFETIME270_H
#include <stdbool.h>
#include <stdint.h>
#include <string.h>
#define L270_WATCHES 4u
#define L270_RUNS 128u
enum { L270_BIND=2, L270_DEC=3, L270_FREE=4 };
enum { L270_BAD=1u, L270_OVERFLOW=2u, L270_SEQUENCE=4u, L270_EXTERNAL=8u };
typedef struct {
    uint64_t seq, identity, generation;
    uint32_t kind, slot, code;
} L270Event;
typedef struct {
    L270Event first;
    uint64_t last_seq, count;
} L270Run;
typedef struct {
    uint64_t identity, generation, binds, decrements;
    bool live, has_bind, has_free;
    L270Event first_bind, final_free;
} L270Watch;
typedef struct {
    uint64_t sequence;
    uint32_t error, run_count;
    bool armed;
    L270Watch watch[L270_WATCHES];
    L270Run runs[L270_RUNS];
} L270;

static inline bool l270_arm(L270 *s, const uint64_t id[4], const uint64_t gen[4])
{
    if (s->armed || s->error || s->sequence || s->run_count) {s->error |= L270_BAD; return false;}
    for (unsigned i=0;i<4;i++) {
        if (!id[i] || !gen[i]) {s->error |= L270_BAD; return false;}
        for (unsigned j=0;j<i;j++) if (id[i]==id[j] || gen[i]==gen[j]) {s->error |= L270_BAD; return false;}
    }
    for (unsigned i=0;i<4;i++) s->watch[i]=(L270Watch){.identity=id[i],.generation=gen[i],.live=true};
    s->armed=true;
    return true;
}
static inline void l270_count(L270 *s, uint64_t *counter)
{
    if (*counter==UINT64_MAX) s->error |= L270_OVERFLOW;
    else ++*counter;
}
static inline void l270_run(L270 *s, L270Event e)
{
    L270Run *r=s->run_count?&s->runs[s->run_count-1]:NULL;
    if (r && r->first.kind==e.kind && r->first.slot==e.slot && r->first.code==e.code &&
        r->first.identity==e.identity && r->first.generation==e.generation &&
        r->last_seq!=UINT64_MAX && r->last_seq+1==e.seq) {
        if (r->count==UINT64_MAX) {s->error |= L270_OVERFLOW; return;}
        ++r->count; r->last_seq=e.seq; return;
    }
    if (s->run_count==L270_RUNS) {s->error |= L270_OVERFLOW; return;}
    s->runs[s->run_count++]=(L270Run){.first=e,.last_seq=e.seq,.count=1};
}
/* code is pre-decrement refcount for DEC, or (actual unit << 8)|path for BIND.
 * A final-free record is emitted BEFORE the actual final decrement/free.
 * Caller must never manufacture generation on address reuse or reset a tombstone.
 */
static inline bool l270_observe(L270 *s, unsigned slot, uint64_t id, uint64_t gen,
                                unsigned kind, unsigned code)
{
    if (!s->armed || slot>=4) {s->error |= L270_BAD; return false;}
    L270Watch *w=&s->watch[slot];
    if (!w->live || w->identity!=id || w->generation!=gen ||
        (kind!=L270_BIND && kind!=L270_DEC) ||
        (kind==L270_DEC && !code) ||
        (kind==L270_BIND && ((code>>8)>=4 || ((code&255)!=1 && (code&255)!=2)))) {
        s->error |= L270_BAD; return false;
    }
    uint64_t seq=0;
    if (s->sequence==UINT64_MAX) s->error |= L270_SEQUENCE;
    else seq=++s->sequence;
    L270Event e={seq,id,gen,kind,slot,code};
    if (kind==L270_BIND) {
        l270_count(s,&w->binds);
        if (!w->has_bind) {w->first_bind=e; w->has_bind=true;}
        else if (seq) l270_run(s,e);
    } else {
        l270_count(s,&w->decrements);
        if (code==1) {
            e.kind=L270_FREE; w->final_free=e; w->has_free=true; w->live=false;
        } else if (seq) l270_run(s,e);
    }
    /* Even after run overflow, reserved first-bind/final-free slots survive.
     * They aid diagnosis ONLY: error remains sticky and complete is false. */
    return !s->error;
}
static inline bool l270_complete(const L270 *s)
{
    return s->armed && !s->error;
}
#endif
