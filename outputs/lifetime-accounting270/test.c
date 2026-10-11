#include "lifetime.h"
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include "actual-prefix.h"
static unsigned checks;
#define CHECK(x) do {++checks; assert(x);} while(0)
static void fresh(L270 *s)
{
    memset(s,0,sizeof(*s));
    uint64_t id[]={101,102,103,104},gen[]={11,12,13,14};
    CHECK(l270_arm(s,id,gen));
}
static bool event(L270 *s,unsigned slot,unsigned kind,unsigned code)
{
    return l270_observe(s,slot,101+slot,11+slot,kind,code);
}
/* Independent expansion oracle reconstructs ALL callbacks in exact sequence.
 * Reserved lifecycle records and compressed nonfinal runs share one sequence. */
static void reconstruct(const L270 *s, const L270Event *expected, unsigned n)
{
    L270Event *flat=calloc(n+1,sizeof(*flat)); CHECK(flat!=NULL);
    for (unsigned i=0;i<4;i++) {
        const L270Watch *w=&s->watch[i];
        L270Event records[]={w->first_bind,w->final_free};
        bool exists[]={w->has_bind,w->has_free};
        for(unsigned j=0;j<2;j++) if(exists[j]) {
            CHECK(records[j].seq>0 && records[j].seq<=n);
            CHECK(!flat[records[j].seq].seq); flat[records[j].seq]=records[j];
        }
    }
    for(unsigned i=0;i<s->run_count;i++) {
        const L270Run *r=&s->runs[i]; CHECK(r->count==r->last_seq-r->first.seq+1);
        for(uint64_t j=0;j<r->count;j++) {
            L270Event e=r->first; e.seq+=j;
            CHECK(e.seq<=n && !flat[e.seq].seq); flat[e.seq]=e;
        }
    }
    for(unsigned i=1;i<=n;i++) {
        L270Event a=flat[i],b=expected[i-1];
        CHECK(a.seq==b.seq && a.kind==b.kind && a.slot==b.slot && a.code==b.code &&
              a.identity==b.identity && a.generation==b.generation);
    }
    free(flat);
}
int main(void)
{
    L270 s; L270Event expected[512]; fresh(&s);
    for(unsigned i=0;i<ACTUAL_COUNT;i++) {
        const unsigned *a=actual[i]; CHECK(event(&s,a[1],a[0],a[2]));
        expected[i]=(L270Event){i+1,101+a[1],11+a[1],a[0],a[1],a[2]};
    }
    CHECK(s.sequence==127 && s.watch[0].binds==1 && s.watch[0].decrements==123);
    CHECK(s.watch[1].decrements==1 && s.watch[2].decrements==1 && s.watch[3].decrements==1);
    reconstruct(&s,expected,ACTUAL_COUNT);
    printf("Actual269 prefix: %u callbacks, %u run records plus one first bind\n",ACTUAL_COUNT,s.run_count);
    CHECK(l270_complete(&s));
    /* Old input is truncated; replay must NOT rehabilitate the old run. */
    s.error |= L270_EXTERNAL; CHECK(!l270_complete(&s));

    fresh(&s);
    for(unsigned i=0;i<1000000;i++) CHECK(event(&s,0,L270_DEC,2));
    CHECK(s.run_count==1 && s.runs[0].count==1000000 && s.watch[0].decrements==1000000);
    for(unsigned i=0;i<4;i++) {CHECK(event(&s,i,L270_BIND,(i<<8)|2)); CHECK(event(&s,i,L270_DEC,1));}
    CHECK(l270_complete(&s));
    for(unsigned i=0;i<4;i++) CHECK(s.watch[i].has_bind && s.watch[i].has_free && !s.watch[i].live);

    /* Interleaved operations, repeated bind, independent complete expansion. */
    fresh(&s); unsigned n=0;
    for(unsigned cycle=0;cycle<8;cycle++) for(unsigned slot=0;slot<4;slot++) {
        unsigned kind=cycle&1?L270_BIND:L270_DEC,code=kind==L270_BIND?(slot<<8)|1:2+cycle;
        CHECK(event(&s,slot,kind,code));
        expected[n]=(L270Event){n+1,101+slot,11+slot,kind,slot,code}; ++n;
    }
    for(unsigned slot=0;slot<4;slot++) {
        CHECK(event(&s,slot,L270_DEC,1));
        expected[n]=(L270Event){n+1,101+slot,11+slot,L270_FREE,slot,1}; ++n;
    }
    reconstruct(&s,expected,n);
    /* Tombstone rejects both stale generation and reused address, no dereference. */
    CHECK(!l270_observe(&s,0,101,99,L270_BIND,1));
    CHECK(!event(&s,0,L270_BIND,1)); CHECK(!event(&s,0,L270_DEC,1));
    CHECK(s.watch[0].generation==11 && s.watch[0].final_free.seq==33);

    fresh(&s);
    for(unsigned i=0;i<L270_RUNS;i++) CHECK(event(&s,i%4,L270_DEC,2));
    CHECK(s.run_count==L270_RUNS && l270_complete(&s));
    CHECK(!event(&s,0,L270_DEC,3)); CHECK(s.error&L270_OVERFLOW);
    for(unsigned i=0;i<4;i++) {CHECK(!event(&s,i,L270_BIND,2)); CHECK(!event(&s,i,L270_DEC,1));}
    for(unsigned i=0;i<4;i++) CHECK(s.watch[i].has_bind && s.watch[i].has_free);
    CHECK(!l270_complete(&s));

    fresh(&s); s.sequence=UINT64_MAX; CHECK(!event(&s,0,L270_DEC,1));
    CHECK(s.watch[0].has_free && s.watch[0].final_free.seq==0 && (s.error&L270_SEQUENCE));
    fresh(&s); s.watch[0].decrements=UINT64_MAX; CHECK(!event(&s,0,L270_DEC,2));
    CHECK(s.watch[0].decrements==UINT64_MAX && !l270_complete(&s));
    fresh(&s); s.watch[0].binds=UINT64_MAX; CHECK(!event(&s,0,L270_BIND,1));
    CHECK(s.watch[0].first_bind.seq==1 && s.watch[0].binds==UINT64_MAX);
    fresh(&s); CHECK(!l270_observe(&s,0,101,99,L270_BIND,1));
    fresh(&s); CHECK(!l270_observe(&s,0,999,11,L270_BIND,1));
    fresh(&s); CHECK(!event(&s,4,L270_BIND,1));
    fresh(&s); CHECK(!event(&s,0,L270_DEC,0));
    fresh(&s); CHECK(!event(&s,0,L270_BIND,0));
    fresh(&s); CHECK(!event(&s,0,L270_BIND,0x401));
    fresh(&s); uint64_t id[]={101,102,103,104},gen[]={11,12,13,14}; CHECK(!l270_arm(&s,id,gen));
    memset(&s,0,sizeof(s)); id[3]=id[0]; CHECK(!l270_arm(&s,id,gen));
    memset(&s,0,sizeof(s)); id[3]=104; gen[3]=gen[0]; CHECK(!l270_arm(&s,id,gen));
    printf("PASS %u checks; no renderer/GL/guest invocation\n",checks);
    return 0;
}
