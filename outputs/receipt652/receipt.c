/* SPDX-License-Identifier: GPL-2.0-or-later */
#include "receipt.h"
static void put(uint8_t *p,uint32_t v) {
    unsigned i;for(i=0;i<4;i++)p[i]=(uint8_t)(v>>(8*i));
}
static uint32_t get(const uint8_t *p) {
    return (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
}
static void copy(uint8_t *d,const uint8_t *s,unsigned n) {
    unsigned i;for(i=0;i<n;i++)d[i]=s[i];
}
static int equal(const uint8_t *a,const uint8_t *b,unsigned n) {
    unsigned i;for(i=0;i<n;i++)if(a[i]!=b[i])return 0;return 1;
}
static int zero(const uint8_t *p,unsigned n) {
    unsigned i;for(i=0;i<n;i++)if(p[i])return 0;return 1;
}
static int identity_ok(const struct xwn652_identity *id) {
    return id && !zero(id->attempt,16) && !zero(id->candidate_sha256,32);
}
uint32_t xwn652_crc(const uint8_t *p,unsigned n) {
    uint32_t v=0xffffffffu;unsigned i,j;
    for(i=0;i<n;i++){v^=p[i];for(j=0;j<8;j++)v=(v>>1)^(0xedb88320u&(0u-(v&1u)));}
    return ~v;
}
static void header(uint8_t *p,const char *magic,unsigned n,const struct xwn652_identity *id) {
    unsigned i;for(i=0;i<n;i++)p[i]=0;
    copy(p,(const uint8_t *)magic,8);put(p+8,1);
    copy(p+16,id->attempt,16);copy(p+32,id->candidate_sha256,32);
}
void xwn652_seed(const struct xwn652_identity *id,unsigned sector,uint8_t *p) {
    header(p,"XWN652S1",512,id);put(p+12,sector);put(p+508,xwn652_crc(p,508));
}
static unsigned words(uint8_t *p,unsigned offset,const uint32_t *v,unsigned n) {
    unsigned i;for(i=0;i<n;i++)put(p+offset+4*i,v[i]);return offset+4*n;
}
int xwn652_encode(const struct xwn652_identity *id,const struct xwn652_data *d,uint8_t *p) {
    unsigned off=72;
    if(!identity_ok(id)||!d||!p||d->result < -1||d->result>1||
       (d->post_kind!=1 && d->post_kind!=2))return XWN652_ARGUMENT;
    header(p,"XWN652R1",1024,id);put(p+12,768);
    put(p+64,(uint32_t)d->result);put(p+68,d->post_kind);
    off=words(p,off,d->request,8);off=words(p,off,d->state,9);
    off=words(p,off,d->trace,63);off=words(p,off,d->pre,47);
    (void)words(p,off,d->post,47);
    header(p+1024,"XWN652C1",512,id);put(p+1036,1024);
    put(p+1088,xwn652_crc(p,1024));put(p+1532,xwn652_crc(p+1024,508));
    return XWN652_OK;
}
int xwn652_validate(const struct xwn652_identity *id,const uint8_t *p) {
    uint32_t result;
    if(!identity_ok(id)||!p)return 0;
    result=get(p+64);
    if(!equal(p,(const uint8_t *)"XWN652R1",8)||get(p+8)!=1||get(p+12)!=768||
       !equal(p+16,id->attempt,16)||!equal(p+32,id->candidate_sha256,32)||
       (result!=0 && result!=1 && result!=0xffffffffu)||
       (get(p+68)!=1 && get(p+68)!=2)||!zero(p+768,256))return 0;
    if(!equal(p+1024,(const uint8_t *)"XWN652C1",8)||get(p+1032)!=1||get(p+1036)!=1024||
       !equal(p+1040,id->attempt,16)||!equal(p+1056,id->candidate_sha256,32)||
       get(p+1088)!=xwn652_crc(p,1024)||!zero(p+1092,440)||
       get(p+1532)!=xwn652_crc(p+1024,508))return 0;
    return 1;
}
int xwn652_store(struct xwn652_guard *g,const struct xwn652_io *io,
                const struct xwn652_identity *id,const struct xwn652_data *d,
                struct xwn652_scratch *s) {
    unsigned i;int r;
    if(!g||!io||!io->read||!io->write||!io->flush||!s)return XWN652_ARGUMENT;
    if(g->attempted)return XWN652_ALREADY_ATTEMPTED;
    r=xwn652_encode(id,d,s->record);if(r)return r;
    g->attempted=1;
    for(i=0;i<3;i++) {
        uint8_t expected[512];
        xwn652_seed(id,i,expected);
        if(io->read(io->opaque,i,s->sector))return XWN652_PREFLIGHT_READ;
        if(!equal(expected,s->sector,512))return XWN652_SEED_MISMATCH;
    }
    for(i=0;i<2;i++)if(io->write(io->opaque,i,s->record+512*i))return XWN652_PAYLOAD_WRITE;
    if(io->flush(io->opaque))return XWN652_PAYLOAD_FLUSH;
    for(i=0;i<2;i++) {
        if(io->read(io->opaque,i,s->sector))return XWN652_PAYLOAD_READ;
        if(!equal(s->record+512*i,s->sector,512))return XWN652_PAYLOAD_MISMATCH;
    }
    if(io->write(io->opaque,2,s->record+1024))return XWN652_COMMIT_WRITE;
    if(io->flush(io->opaque))return XWN652_COMMIT_FLUSH;
    for(i=0;i<3;i++) {
        if(io->read(io->opaque,i,s->sector))return XWN652_FINAL_READ;
        if(!equal(s->record+512*i,s->sector,512))return XWN652_FINAL_MISMATCH;
    }
    return XWN652_OK;
}
