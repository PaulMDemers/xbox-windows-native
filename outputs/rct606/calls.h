/* MIT. Bounded x86 call pairing. Shared by the recorder and native host tests. */
#ifndef CALLS601_H
#define CALLS601_H
typedef unsigned int U32;
typedef struct { U32 id, api, ret, entry_sp, return_sp, arg0, arg1, selected, args[13]; } FRAME601;
typedef struct { FRAME601 frames[32]; U32 depth; } STACK601;
static int enter601(STACK601 *s, FRAME601 f, U32 cleanup) {
    if(s->depth==32 || !f.ret || !f.entry_sp || cleanup>64 ||
       f.entry_sp>0xffffffffu-4-cleanup) return 0;
    f.return_sp=f.entry_sp+4+cleanup;
    if(s->depth && f.return_sp>s->frames[s->depth-1].entry_sp) return 0;
    s->frames[s->depth++]=f; return 1;
}
/* 1 paired, 0 stale/shared site, -1 wrong ESP or non-LIFO/unwound frame. */
static int leave601(STACK601 *s,U32 address,U32 sp,FRAME601 *out) {
    U32 i;
    if(!s->depth) return 0;
    if(s->frames[s->depth-1].ret==address) {
        if(s->frames[s->depth-1].return_sp!=sp) return -1;
        *out=s->frames[--s->depth];return 1;
    }
    for(i=0;i<s->depth;i++) if(s->frames[i].ret==address) return -1;
    if(sp>s->frames[s->depth-1].return_sp) return -1;
    return 0;
}
#endif
