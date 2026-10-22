/* SPDX-License-Identifier: GPL-2.0-or-later */
#include "receipt.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
struct model {
    unsigned calls,fail_at,fail_after,reads,writes,flushes,corrupt_at,tear;
    char sequence[32];
    uint8_t cache[1536],disk[1536],before[1536];
};
static struct xwn652_identity id;
static struct xwn652_data data;
static unsigned checks;
static int begin(struct model *m,char op) {
    assert(m->calls<31);m->sequence[m->calls++]=op;
    return m->calls==m->fail_at && !m->fail_after;
}
static int end(struct model *m){return m->calls==m->fail_at && m->fail_after;}
static int rd(void *o,unsigned i,uint8_t *p) {
    struct model *m=o;assert(i<3);m->reads++;
    if(begin(m,'R'))return 1;
    memcpy(p,m->cache+i*512,512);
    if(m->calls==m->corrupt_at)p[100]^=1;
    return end(m);
}
static int wr(void *o,unsigned i,const uint8_t *p) {
    struct model *m=o;unsigned n=512;assert(i<3);m->writes++;
    if(begin(m,'W'))return 1;
    if(m->calls==m->fail_at && m->tear<512)n=m->tear;
    memcpy(m->cache+i*512,p,n);return end(m);
}
static int flush(void *o) {
    struct model *m=o;m->flushes++;if(begin(m,'F'))return 1;
    memcpy(m->disk,m->cache,1536);return end(m);
}
static void init(struct model *m) {
    unsigned i;memset(m,0,sizeof(*m));m->tear=512;
    for(i=0;i<3;i++)xwn652_seed(&id,i,m->cache+i*512);
    memcpy(m->disk,m->cache,1536);memcpy(m->before,m->cache,1536);
}
static int run(struct model *m,struct xwn652_guard *g) {
    struct xwn652_scratch scratch;struct xwn652_io io={m,rd,wr,flush};
    return xwn652_store(g,&io,&id,&data,&scratch);
}
static void refuse_retry(struct model *m,struct xwn652_guard *g) {
    unsigned calls=m->calls;assert(run(m,g)==XWN652_ALREADY_ATTEMPTED);
    assert(calls==m->calls);checks++;
}
int main(int argc,char **argv) {
    struct model m;struct xwn652_guard g;uint8_t record[1536];
    unsigned i,j,after;FILE *f;
    for(i=0;i<16;i++)id.attempt[i]=(uint8_t)(i+1);
    for(i=0;i<32;i++)id.candidate_sha256[i]=(uint8_t)(0xa0+i);
    data.result=-1;data.post_kind=2;
    for(i=0;i<8;i++)data.request[i]=0x10000000u+i;
    for(i=0;i<9;i++)data.state[i]=0x20000000u+i;
    for(i=0;i<63;i++)data.trace[i]=0x30000000u+i;
    for(i=0;i<47;i++){data.pre[i]=0x40000000u+i;data.post[i]=0x50000000u+i;}
    assert(xwn652_crc((const uint8_t *)"123456789",9)==0xcbf43926u);checks++;
    assert(xwn652_encode(&id,&data,record)==0 && xwn652_validate(&id,record));checks++;
    assert(argc==2);f=fopen(argv[1],"wbx");assert(f);
    assert(fwrite(record,1,1536,f)==1536 && fclose(f)==0);
    for(i=0;i<1536;i++)for(j=0;j<8;j++) {
        record[i]^=(uint8_t)(1u<<j);assert(!xwn652_validate(&id,record));
        record[i]^=(uint8_t)(1u<<j);checks++;
    }
    init(&m);g.attempted=0;assert(run(&m,&g)==0);
    assert(strcmp(m.sequence,"RRRWWFRRWFRRR")==0);
    assert(m.calls==13 && m.reads==8 && m.writes==3 && m.flushes==2);
    assert(xwn652_validate(&id,m.disk));checks++;refuse_retry(&m,&g);
    /* Fresh guard still must reject a consumed slot without a write. */
    g.attempted=0;m.calls=m.writes=0;assert(run(&m,&g)==XWN652_SEED_MISMATCH);
    assert(m.calls==1 && !m.writes);checks++;
    for(i=1;i<=13;i++)for(after=0;after<2;after++) {
        init(&m);g.attempted=0;m.fail_at=i;m.fail_after=after;
        assert(run(&m,&g)!=0 && m.calls==i);
        /* Only a completed second flush makes the simulated durable disk valid. */
        assert(xwn652_validate(&id,m.disk)==(i>10 || (i==10 && after)));
        checks++;refuse_retry(&m,&g);
    }
    /* Every torn prefix at every write: uncertain callback stops this attempt. */
    for(i=4;i<=9;i++)if(i==4 || i==5 || i==9)for(j=0;j<=512;j++) {
        init(&m);g.attempted=0;m.fail_at=i;m.fail_after=1;m.tear=j;
        assert(run(&m,&g)!=0 && m.calls==i);
        assert(!xwn652_validate(&id,m.disk));checks++;refuse_retry(&m,&g);
    }
    /* Corrupt each seed byte: no write, preserving the original slot. */
    for(i=0;i<1536;i++) {
        init(&m);g.attempted=0;m.cache[i]^=1;
        assert(run(&m,&g)==XWN652_SEED_MISMATCH && !m.writes);
        assert(!memcmp(m.disk,m.before,1536));checks++;
    }
    for(i=1;i<=13;i++)if(i<=3 || i==7 || i==8 || i>=11) {
        init(&m);g.attempted=0;m.corrupt_at=i;assert(run(&m,&g)!=0);
        assert(m.calls==i);checks++;refuse_retry(&m,&g);
    }
    /* Same bytes with a foreign identity must never be accepted. */
    for(i=0;i<16;i++){id.attempt[i]^=1;assert(!xwn652_validate(&id,record));id.attempt[i]^=1;checks++;}
    for(i=0;i<32;i++){id.candidate_sha256[i]^=1;assert(!xwn652_validate(&id,record));id.candidate_sha256[i]^=1;checks++;}
    init(&m);g.attempted=0;data.post_kind=0;
    assert(run(&m,&g)==XWN652_ARGUMENT && !m.calls && !g.attempted);checks++;
    data.post_kind=2;data.result=2;
    assert(run(&m,&g)==XWN652_ARGUMENT && !m.calls && !g.attempted);checks++;
    printf("{\"checks\":%u,\"passed\":true,\"physical_transport\":false}\n",checks);
    return 0;
}
