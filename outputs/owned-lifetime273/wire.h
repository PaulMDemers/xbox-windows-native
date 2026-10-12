/* Explicit little-endian terminal format; no C padding or pointer dereference. */
#ifndef XWN_WIRE273_H
#define XWN_WIRE273_H
#include "lifetime.h"
#define X273_MAGIC UINT64_C(0x3337324e5758)
#define X273_CAPACITY (128u+4u*160u+L270_RUNS*64u)
typedef struct {
    uint64_t gate_error,transport_error,worker,gate,enabled,sealed,captures;
} X273Meta;
static inline void x273_word(uint8_t **p,uint64_t n)
{
    for (unsigned i=0;i<8;i++) *(*p)++=(uint8_t)(n>>(8*i));
}
static inline void x273_event(uint8_t **p,const L270Event *e)
{
    x273_word(p,e->seq);x273_word(p,e->identity);x273_word(p,e->generation);
    x273_word(p,e->kind);x273_word(p,e->slot);x273_word(p,e->code);
}
static inline unsigned x273_encode(const L270 *s,const X273Meta *m,uint8_t *out,unsigned capacity)
{
    if (!s || !m || !out || s->run_count>L270_RUNS) return 0;
    unsigned bytes=128+4*160+s->run_count*64;
    if (capacity<bytes) return 0;
    uint8_t *p=out;
    uint64_t h[16]={X273_MAGIC,273,bytes,4,s->run_count,s->sequence,s->error,
        m->gate_error,m->transport_error,m->worker,m->gate,m->enabled,m->sealed,
        m->captures,s->armed,0};
    for (unsigned i=0;i<16;i++) x273_word(&p,h[i]);
    for (unsigned i=0;i<4;i++) {
        const L270Watch *w=&s->watch[i];
        uint64_t row[8]={w->identity,w->generation,w->binds,w->decrements,
            w->live,w->has_bind,w->has_free,i};
        for (unsigned j=0;j<8;j++) x273_word(&p,row[j]);
        x273_event(&p,&w->first_bind);x273_event(&p,&w->final_free);
    }
    for (unsigned i=0;i<s->run_count;i++) {
        x273_event(&p,&s->runs[i].first);
        x273_word(&p,s->runs[i].last_seq);x273_word(&p,s->runs[i].count);
    }
    return (unsigned)(p-out);
}
#endif
