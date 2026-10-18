/* SPDX-License-Identifier: MIT; actual engine, modeled filesystem callbacks. */
#include "engine.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
struct model {
    unsigned calls,fail,opened,closed,live,stage,creates[2];
    unsigned short_write,short_read,extra_read,bad_read;
    unsigned char files[2][49];
};
static int hit(struct model *m) { return ++m->calls!=m->fail; }
static int op(void *p,unsigned s,int writing)
{
    struct model *m=p; assert(!m->live && s>=1 && s<=2);
    if (!hit(m)) return 0;
    if (writing) { assert(!m->creates[s-1]); ++m->creates[s-1]; }
    m->stage=s; m->live=1; ++m->opened; return 1;
}
static int wr(void *p,const unsigned char *d,size_t n,size_t *got)
{
    struct model *m=p; assert(m->live && n==48);
    if (!hit(m)) return 0;
    memcpy(m->files[m->stage-1],d,n); *got=m->short_write ? 47 : n; return 1;
}
static int fl(void *p) { struct model *m=p; assert(m->live); return hit(m); }
static int cl(void *p)
{
    struct model *m=p; assert(m->live); m->live=0; ++m->closed; return hit(m);
}
static int rd(void *p,unsigned char *d,size_t n,size_t *got)
{
    struct model *m=p; assert(m->live && n==49);
    if (!hit(m)) return 0;
    memcpy(d,m->files[m->stage-1],49);
    if (m->bad_read) d[11]^=1;
    *got=m->short_read ? 47 : m->extra_read ? 49 : 48; return 1;
}
int main(int argc,char **argv)
{
    const uint16_t kernel[4]={1,0,5838,1};
    unsigned cases=0;
    for (unsigned fail=0;fail<=14;++fail) {
        struct model m={0}; m.fail=fail;
        const struct io527 io={&m,op,wr,fl,cl,rd};
        assert(run527(&io,kernel)==(fail==0));
        assert(!m.live && m.opened==m.closed && m.calls<=14);
        if (fail && fail<=7) assert(!m.creates[1]);
        if (!fail) {
            assert(m.calls==14 && m.opened==4);
            assert(argc==2);
            FILE *f=fopen(argv[1],"wb"); assert(f);
            assert(fwrite(m.files[0],1,48,f)==48);
            assert(fwrite(m.files[1],1,48,f)==48); assert(fclose(f)==0);
        }
        ++cases;
    }
    for (unsigned bad=0;bad<4;++bad) {
        struct model m={0};
        if (bad==0) m.short_write=1;
        if (bad==1) m.short_read=1;
        if (bad==2) m.extra_read=1;
        if (bad==3) m.bad_read=1;
        const struct io527 io={&m,op,wr,fl,cl,rd};
        assert(!run527(&io,kernel));
        assert(!m.live && m.opened==m.closed && !m.creates[1]); ++cases;
    }
    printf("PASS %u actual engine scenarios; modeled OS services\n",cases);
}
